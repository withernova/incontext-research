"""Standalone Git worker, sent over SSH. Never print Git stderr or credentials."""
import json
import os
import pathlib
import re
import subprocess
import sys


class Blocked(Exception):
    pass


def github_identity(value):
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:)([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?", value)
    if not match:
        raise Blocked("origin must be a credential-free GitHub HTTPS or SSH URL")
    return match.group(1).lower()


def under(path, root):
    return path == root or root in path.parents


def worker(spec):
    repo = pathlib.Path(spec["repo"]).resolve(strict=True)
    if ".publish" in repo.parts or repo == pathlib.Path("/"):
        raise Blocked("publish snapshots and filesystem root are not development repositories")
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")

    def git(*args, check=True, raw=False, byte_output=False):
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-c", "submodule.recurse=false", "-C", str(repo), *args], env=env, capture_output=True, timeout=90)
        if check and result.returncode:
            raise Blocked("Git command failed: " + args[0] + "; check authentication/configuration locally (stderr withheld)")
        if not check:
            return result.returncode
        if byte_output:
            return result.stdout
        text = result.stdout.decode("utf-8", "strict")
        return text if raw else text.strip()

    if pathlib.Path(git("rev-parse", "--show-toplevel")).resolve() != repo:
        raise Blocked("binding must point to the exact Git worktree root")
    action = spec["action"]
    origin = git("remote", "get-url", "origin")
    identity = github_identity(origin)
    if action != "discover" and identity != github_identity(spec["repository_url"]):
        raise Blocked("origin repository does not match binding")
    current_branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    branch = current_branch if action == "discover" else spec["branch"]
    if git("check-ref-format", "--branch", branch, check=False):
        raise Blocked("invalid branch")
    if current_branch != branch:
        raise Blocked("wrong branch or detached HEAD; no automatic checkout")
    for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "BISECT_LOG"):
        if pathlib.Path(git("rev-parse", "--git-path", name)).is_absolute():
            pending = pathlib.Path(git("rev-parse", "--git-path", name))
        else:
            pending = repo / git("rev-parse", "--git-path", name)
        if pending.exists():
            raise Blocked("unfinished Git operation")
    if action not in {"discover", "inspect", "advance", "verify", "checkpoint", "publish"}:
        raise Blocked("invalid operation")
    if action == "checkpoint" and not spec.get("remote"):
        raise Blocked("automatic checkpoint is only allowed for the bound remote repository")
    if action not in {"discover", "checkpoint"} and git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
        raise Blocked("dirty repository; no stash/reset/clean is permitted")
    common = pathlib.Path(git("rev-parse", "--git-common-dir"))
    common = (common if common.is_absolute() else repo / common).resolve()
    head = git("rev-parse", "HEAD")
    if action == "verify":
        if head != spec["target"]:
            raise Blocked("remote commit does not match Run git_commit")
        return {"head": head, "repo": str(repo), "clean": True, "git_common_dir": str(common)}
    if spec.get("remote"):
        # Resolve policy roots remotely too: lexical checks do not protect symlinks.
        allows = [pathlib.Path(p).resolve() for p in spec["allowed_write_roots"]]
        denies = [pathlib.Path(p).resolve() for p in spec["forbidden_paths"]]
        reads = [pathlib.Path(p).resolve() for p in spec["read_only_roots"]]
        for target in (repo, pathlib.Path(git("rev-parse", "--absolute-git-dir")).resolve(), common, (repo / ".git").resolve()):
            a = max((len(str(p)) for p in allows if under(target, p)), default=0)
            d = max((len(str(p)) for p in denies if under(target, p)), default=0)
            if not a or d >= a or any(under(target, p) for p in reads):
                raise Blocked("repository or Git metadata escapes effective write policy")
    if action == "discover":
        if not spec.get("remote"):
            raise Blocked("binding discovery requires the bound remote repository")
        return {"head": head, "repo": str(repo), "repository_url": "https://github.com/" + identity, "branch": branch, "transport": "ssh" if origin.startswith("git@github.com:") else "https"}

    def fetch():
        git("fetch", "--no-tags", "--no-recurse-submodules", "origin", "+refs/heads/" + branch + ":refs/remotes/origin/" + branch)
        return git("rev-parse", "refs/remotes/origin/" + branch)

    def push(head):
        # Explicit bound branch only; reject pushurl/mirror redirects and force.
        urls = git("remote", "get-url", "--push", "--all", "origin").splitlines()
        if len(urls) != 1 or github_identity(urls[0]) != github_identity(spec["repository_url"]):
            raise Blocked("push destination does not match the bound repository")
        if git("config", "--get", "remote.origin.mirror", check=False) == 0:
            raise Blocked("mirror push configuration is not supported")
        git("push", "--no-verify", "--recurse-submodules=no", "origin", head + ":refs/heads/" + branch)
        if fetch() != head:
            raise Blocked("upstream changed after push; no successful receipt issued")

    def validate_code_path(name):
        # data/datasets can contain source modules, not just dataset payloads.
        # A source suffix is a classification hint, not a content-safety exemption.
        protected = {".git", "weights", "checkpoints", "outputs", "logs", "wandb", "__pycache__", ".venv"}
        source_suffixes = {".py", ".pyi", ".sh", ".bash", ".js", ".jsx", ".ts", ".tsx", ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".rs", ".go", ".jl", ".r", ".lua", ".rb", ".java"}
        relative = pathlib.PurePosixPath(name)
        target = (repo / name).resolve()
        if not name or relative.is_absolute() or ".." in relative.parts or not under(target, repo):
            raise Blocked("checkpoint path escapes repository")
        parts = {part.lower() for part in relative.parts}
        suffix = relative.suffix.lower()
        if any(part == ".env" or part.startswith(".env.") for part in parts) or suffix in {".pem", ".key", ".p12"}:
            raise Blocked("checkpoint contains paths reserved for credentials; preserve and handle separately")
        if parts & protected or suffix in {".pt", ".pth", ".ckpt", ".safetensors"}:
            raise Blocked("checkpoint contains protected repository/cache or data/output paths; preserve and handle separately")
        if parts & {"data", "datasets"} and suffix not in source_suffixes:
            raise Blocked("checkpoint contains a non-source data/datasets path; only source-file suffixes are permitted there")
        if spec.get("remote"):
            a = max((len(str(p)) for p in allows if under(target, p)), default=0)
            d = max((len(str(p)) for p in denies if under(target, p)), default=0)
            if not a or d >= a or any(under(target, p) for p in reads):
                raise Blocked("checkpoint file escapes effective write policy")

    def validate_code_content(content):
        if b"\0" in content or re.search(rb"(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}|(?:api[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_+/=-]{16,})", content, re.I):
            raise Blocked("checkpoint contains binary content or a suspected credential (value withheld)")

    def checkpoint_files():
        tracked = git("diff", "HEAD", "--name-only", "-z", "--", raw=True).split("\0")
        untracked = git("ls-files", "--others", "--exclude-standard", "-z", raw=True).split("\0")
        files = sorted(set(tracked + untracked) - {""})
        if len(files) > 1000:
            raise Blocked("too many files for an automatic checkpoint")
        for name in files:
            validate_code_path(name)
            entry = repo / name
            if entry.is_symlink() or (entry.exists() and not entry.is_file()):
                raise Blocked("automatic checkpoint does not accept symlinks or submodules")
            if entry.is_file():
                if entry.stat().st_size > 1_000_000:
                    raise Blocked("checkpoint file too large; handle data/output files separately")
                validate_code_content(entry.read_bytes())
        return files

    def validate_outgoing(upstream, head):
        # Inspect every outgoing version, including secrets later deleted from HEAD.
        commits = git("rev-list", "--max-count=101", upstream + ".." + head).splitlines()
        if len(commits) > 100:
            raise Blocked("too many unpublished commits for automatic code publication")
        seen = set()
        for commit in commits:
            names = set(git("diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", "-z", commit, "--", raw=True).split("\0")) - {""}
            if len(names) > 1000:
                raise Blocked("too many changed files for automatic code publication")
            for name in names:
                validate_code_path(name)
                entries = git("--literal-pathspecs", "ls-tree", "-z", commit, "--", name, raw=True).split("\0")
                for entry in filter(None, entries):
                    metadata, _ = entry.split("\t", 1)
                    mode, kind, oid = metadata.split()
                    if mode not in {"100644", "100755"} or kind != "blob":
                        raise Blocked("automatic publication does not accept symlinks or submodules")
                    if oid in seen:
                        continue
                    seen.add(oid)
                    if len(seen) > 1000 or int(git("cat-file", "-s", oid)) > 1_000_000:
                        raise Blocked("outgoing code too large for automatic publication")
                    validate_code_content(git("cat-file", "blob", oid, byte_output=True))

    def finish():
        if spec.get("remote"):
            proc = pathlib.Path("/proc")
            if not proc.is_dir():
                raise Blocked("remote process inspection requires Linux /proc")
            for entry in proc.iterdir():
                if not entry.name.isdigit() or int(entry.name) == os.getpid():
                    continue
                try:
                    if entry.stat().st_uid != os.getuid():
                        continue
                    cwd = (entry / "cwd").resolve(strict=True)
                    command = (entry / "cmdline").read_bytes()
                except FileNotFoundError:
                    continue  # Process exited, or a kernel thread without a cwd.
                except PermissionError:
                    raise Blocked("cannot inspect same-user process; idle state is unknown")
                if under(cwd, repo) or str(repo).encode() in command:
                    # Our parent SSH shell carries the worker JSON in its command line.
                    if int(entry.name) == os.getppid():
                        continue
                    raise Blocked("repository in use by a same-user process")
        head = git("rev-parse", "HEAD")
        if action != "checkpoint" and git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
            raise Blocked("dirty repository after lock acquisition")
        if spec.get("expected_head") and head != spec["expected_head"]:
            raise Blocked("HEAD changed since preflight")
        if action in {"checkpoint", "publish"}:
            upstream = fetch()
            committed = False
            if action == "checkpoint":
                # Validate before merge/staging. Never stash, rebase, force, or clean.
                files = checkpoint_files()
                if git("merge-base", "--is-ancestor", upstream, head, check=False):
                    if git("merge-base", "--is-ancestor", head, upstream, check=False):
                        raise Blocked("remote repository diverged from upstream")
                    git("merge", "--ff-only", "--no-edit", upstream)
                files = checkpoint_files()
                if files:
                    git("--literal-pathspecs", "add", "-A", "--", *files)
                    git("commit", "-m", "Checkpoint remote code before local editing")
                    committed = True
                if git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
                    raise Blocked("remote checkpoint left a dirty repository; no push performed")
                head = git("rev-parse", "HEAD")
            else:
                if not re.fullmatch(r"[0-9a-f]{40}", spec.get("target", "")) or head != spec["target"]:
                    raise Blocked("publish requires the exact clean local HEAD")
                baseline = spec.get("baseline", "")
                if not re.fullmatch(r"[0-9a-f]{40}", baseline) or git("merge-base", "--is-ancestor", baseline, head, check=False):
                    raise Blocked("local code does not descend from the prepared baseline")
                if upstream not in {baseline, head}:
                    raise Blocked("upstream changed since prepare; do not overwrite another task")
            if git("merge-base", "--is-ancestor", upstream, head, check=False):
                raise Blocked("push is not a fast-forward")
            pushed = head != upstream
            if pushed:
                validate_outgoing(upstream, head)
                push(head)
            if git("rev-parse", "HEAD") != head or git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
                raise Blocked("repository changed during publication; no successful receipt issued")
            return {"head": head, "upstream": head, "repo": str(repo), "clean": True, "commit_created": committed, "push_performed": pushed}
        if action == "inspect":
            upstream = fetch()
            if git("merge-base", "--is-ancestor", head, upstream, check=False):
                raise Blocked("repository is ahead or diverged; publish/preserve changes explicitly first")
            return {"head": head, "upstream": upstream, "repo": str(repo), "clean": True}
        if action != "advance" or not re.fullmatch(r"[0-9a-f]{40}", spec.get("target", "")):
            raise Blocked("invalid operation or commit")
        target = spec["target"]
        if git("merge-base", "--is-ancestor", head, target, check=False):
            raise Blocked("target is not a fast-forward")
        if git("merge-base", "--is-ancestor", target, "refs/remotes/origin/" + branch, check=False):
            raise Blocked("target is not published on the bound branch")
        git("merge", "--ff-only", "--no-edit", target)
        if git("rev-parse", "HEAD") != target or git("status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"):
            raise Blocked("post-sync verification failed; no rollback performed")
        return {"head": target, "repo": str(repo), "clean": True}

    import fcntl
    descriptor=os.open(common / "survey-tool-code.lock",os.O_CREAT | os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW,0o600)
    with os.fdopen(descriptor,"a") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise Blocked("repository locked by a managed Run or code operation")
        return finish()


if __name__ == "__main__":
    try:
        print(json.dumps({"ok": True, **worker(json.loads(sys.argv[1]))}))
    except (Blocked, OSError, subprocess.SubprocessError, ValueError, KeyError):
        error = sys.exc_info()[1]
        print(json.dumps({"ok": False, "error": str(error) if isinstance(error, Blocked) else "Git/SSH worker unavailable; no successful sync receipt was issued"}))
        sys.exit(1)
