#!/usr/bin/env python3
"""Launch using config values; shell wrappers supply only the config path."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from iploc_szy.branching import load_experiment_config


def launch_command(config, config_path):
    if "branch" in config:
        return [sys.executable, "tools/run_branch.py", str(config_path)]
    settings = config.get("launch", {})
    action = settings.get("action")
    if action not in {"train", "infer", "analyze"}:
        raise ValueError("launch.action must be train, infer or analyze")
    nproc = settings.get("nproc_per_node", 1)
    if type(nproc) is not int or nproc < 1:
        raise ValueError("launch.nproc_per_node must be a positive integer")
    if action in {"infer", "analyze"} and nproc != 1:
        raise ValueError(f"{action} uses one process with optional model sharding")
    if nproc == 1:
        return [sys.executable, f"tools/{action}.py", str(config_path)]
    return [sys.executable, "-m", "torch.distributed.run", "--standalone",
            f"--nproc_per_node={nproc}", f"tools/{action}.py", str(config_path)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()
    path = Path(args.config).resolve()
    config = load_experiment_config(path)
    command = launch_command(config, path)
    if args.inspect:
        print(command)
        return 0
    repository = Path(__file__).resolve().parents[1]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(repository)
    if "branch" in config:
        return subprocess.call(command, cwd=repository, env=environment)
    work_dir = Path(config["work_dir"]).resolve()
    if work_dir.exists():
        raise FileExistsError(f"choose a new work_dir in config: {work_dir}")
    work_dir.mkdir(parents=True, exist_ok=False)
    logs = work_dir / "logs"
    logs.mkdir()
    with (logs / f"console-{uuid4().hex}.log").open("w") as log:
        process = subprocess.Popen(command, cwd=repository, env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        try:
            for line in process.stdout:
                sys.stdout.write(line)
                log.write(line)
                log.flush()
            return process.wait()
        except BaseException:
            process.terminate()
            process.wait()
            raise


if __name__ == "__main__":
    raise SystemExit(main())
