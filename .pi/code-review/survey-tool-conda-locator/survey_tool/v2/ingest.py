"""Human-gated promotion of staged acquisition artifacts into canonical research files."""
from __future__ import annotations

import hashlib
import pathlib
import re
import shutil
from typing import Any, Callable

from .store import V2Store


def _safe_staged(root: pathlib.Path, relative: str, *, file: bool = False) -> pathlib.Path:
    staging = (root / ".survey-tool/staging").resolve()
    path = (root / relative).resolve()
    if staging not in path.parents or (file and not path.is_file()) or (not file and not path.is_dir()):
        raise ValueError("staged artifact is missing or outside staging")
    return path


def _canonical_stem(candidate: dict[str, Any]) -> str:
    title = re.sub(r'[\\/:*?"<>|]+', " ", str(candidate.get("title") or candidate["citekey"])).strip()[:160]
    year = str(candidate.get("year") or "").strip()
    return f"{title}_{year}" if year and not title.endswith(f"_{year}") else title


def _hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def ingest_staged_candidate(
    root: pathlib.Path,
    store: V2Store,
    object_id: str,
    *,
    expected_revision: int,
    actor_id: str,
    ingest_runner: Callable[[pathlib.Path, dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Copy verified staged artifacts and invoke canonical ingest with rollback.

    The caller must enforce the human confirmation phrase. Existing canonical
    files are never overwritten or merged automatically.
    """
    candidate = store.get_paper_candidate(object_id)
    if candidate["revision"] != int(expected_revision):
        raise ValueError(f"revision conflict: expected {expected_revision}, actual {candidate['revision']}")
    if candidate.get("verification_status") == "ingested":
        return candidate
    download_id = candidate.get("acquisition_job_id")
    if not download_id:
        raise ValueError("candidate has no acquisition pipeline")
    download = store.get_job(download_id)
    related = [job for job in store.list_jobs(target_object_id=object_id) if job.get("depends_on_job_id") == download_id and job["kind"] == "mineru"]
    mineru = related[0] if related else None
    if download["status"] != "succeeded" or mineru is None or mineru["status"] != "succeeded":
        raise ValueError("download and MinerU jobs must both succeed before ingest")
    staged_pdf = _safe_staged(root, str(download["result"].get("staged_pdf") or ""), file=True)
    staged_mineru = _safe_staged(root, str(mineru["result"].get("staged_mineru_dir") or ""))
    markdown_relative = str(mineru["result"].get("markdown") or "")
    staged_markdown = _safe_staged(root, markdown_relative, file=True)
    if staged_mineru not in staged_markdown.parents:
        raise ValueError("MinerU Markdown is outside the staged MinerU directory")

    papers = root / "papers"; papers.mkdir(parents=True, exist_ok=True)
    stem = _canonical_stem(candidate)
    canonical_pdf = papers / f"{stem}.pdf"
    canonical_dir = papers / stem
    note = root / "shell/03_evidence/papers" / f"{candidate['citekey']}.md"
    citations = root / "kernel/citations.md"
    citation_marker = f"## [{candidate['citekey']}]"
    if canonical_pdf.exists() or canonical_dir.exists() or note.exists() or (citations.exists() and citation_marker in citations.read_text(encoding="utf-8")):
        raise FileExistsError("canonical paper, note, or citekey already exists; manual conflict resolution required")

    citations_existed = citations.exists()
    citations_before = citations.read_bytes() if citations_existed else b""
    created: list[pathlib.Path] = []
    try:
        shutil.copy2(staged_pdf, canonical_pdf); created.append(canonical_pdf)
        hybrid_source = staged_markdown.parent if staged_markdown.parent.name == "hybrid_auto" else staged_markdown.parent
        canonical_hybrid = canonical_dir / "hybrid_auto"
        canonical_dir.mkdir(parents=True); created.append(canonical_dir)
        shutil.copytree(hybrid_source, canonical_hybrid)
        result = ingest_runner(canonical_pdf, candidate)
        if not result.get("ok"):
            raise RuntimeError(str(result.get("error") or "canonical ingest failed"))
        content_hash = _hash(canonical_pdf)
        if result.get("content_hash") and result["content_hash"] != content_hash:
            raise RuntimeError("ingest hash does not match canonical PDF")
        return store.mark_candidate_ingested(
            object_id, expected_revision=expected_revision, canonical_paper_path=str(canonical_pdf.relative_to(root)),
            content_hash=content_hash, actor_id=actor_id,
        )
    except Exception:
        for path in reversed(created):
            if path.is_dir(): shutil.rmtree(path, ignore_errors=True)
            else: path.unlink(missing_ok=True)
        note.unlink(missing_ok=True)
        if citations_existed:
            citations.parent.mkdir(parents=True, exist_ok=True); citations.write_bytes(citations_before)
        else:
            citations.unlink(missing_ok=True)
        raise
