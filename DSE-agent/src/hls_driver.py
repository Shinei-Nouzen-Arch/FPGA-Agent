#!/usr/bin/env python3
"""Policy-aware HLS command adapter; receipts are not semantic acceptance."""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from artifacts import (file_hash, input_manifest, local_path, read_json,
                       verify_receipt, write_json)

STAGES = ("csim", "csynth", "cosim", "impl")
PATTERNS = {
    "csim": ("*csim*.log", "*csim*summary*"),
    "csynth": ("*_csynth.rpt",),
    "cosim": ("*_cosim.rpt",),
    "impl": ("export_impl.rpt", "*timing*routed*.rpt", "*utilization*routed*.rpt",
             "*power*routed*.rpt"),
}


def read_config(path):
    fields = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            fields.setdefault(key.strip(), []).append(value.strip())
    for key in ("part", "clock", "syn.top", "syn.file"):
        if not fields.get(key) or any(not value for value in fields[key]):
            raise ValueError(f"Config requires {key}")
    for key in ("part", "clock", "syn.top"):
        if len(fields[key]) != 1:
            raise ValueError(f"Config must have one unambiguous {key}")
    clock = float(fields["clock"][0])
    if not math.isfinite(clock) or clock <= 0:
        raise ValueError("clock must be a finite positive period in ns")
    return fields


def policy_check(project, workspace, mode):
    directive = read_json(project / "state/search_directive.json")
    assignment = read_json(local_path(workspace, ".dse/assignment.json"))
    for key in ("benchmark", "run_id"):
        if not directive.get(key) or directive.get(key) != assignment.get(key):
            raise ValueError(f"Directive/assignment {key} mismatch")
    role = assignment.get("role")
    if role not in ("explorer", "exploiter", "innovator"):
        raise ValueError("Unknown worker role")
    if workspace != local_path(project, f"workspace/{role}").resolve():
        raise ValueError("Workspace does not match the assigned role in the selected project")
    policy = directive.get("validation_policy", {})
    if policy != assignment.get("validation_policy"):
        raise ValueError("Directive/assignment validation policy mismatch")
    if policy.get("mode") not in ("formal", "cosim_only_user_override"):
        raise ValueError("Unknown validation policy")
    if not isinstance(policy.get("implementation_allowed"), bool):
        raise ValueError("validation_policy requires implementation_allowed")
    if mode in ("impl", "all"):
        if policy["mode"] == "cosim_only_user_override" or not policy["implementation_allowed"]:
            raise ValueError("Implementation is forbidden by the active validation policy")
    return assignment


def report_files(workspace, stage):
    output = {}
    root = workspace / "hls_project"
    if root.is_symlink():
        raise ValueError("Generated project directory cannot be a symlink")
    if root.exists():
        for pattern in PATTERNS[stage]:
            for path in sorted(root.rglob(pattern)):
                local_path(workspace, path)
                if path.is_file():
                    stat = path.stat()
                    output[path.relative_to(workspace).as_posix()] = (
                        stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size, file_hash(path))
    return output


def command(stage, part, config):
    if stage == "csynth":
        return ["v++", "-c", "--mode", "hls", "--part", part,
                "--work_dir", "hls_project", "--config", str(config)]
    return ["vitis-run", "--mode", "hls", f"--{stage}",
            "--work_dir", "hls_project", "--config", str(config)]


def run_stage(project, workspace, stage, config):
    policy_check(project, workspace, stage)
    fields = read_config(config)
    if stage in ("csim", "cosim") and not fields.get("tb.file"):
        raise ValueError(f"{stage} requires tb.file")
    manifest = input_manifest(workspace, config)
    for key in ("syn.file", "tb.file"):
        for value in fields.get(key, []):
            relative = local_path(workspace, value).relative_to(workspace).as_posix()
            if relative not in manifest["files"]:
                raise ValueError(f"Config input is missing from input_paths: {relative}")
    if stage in ("cosim", "impl"):
        verify_receipt(workspace, "csynth", manifest["input_digest"])
    args = command(stage, fields["part"][0], config)
    if shutil.which(args[0]) is None:
        raise ValueError(f"Required tool is unavailable: {args[0]}")
    # Invalidate the stage being replaced and all downstream receipts first.
    start = STAGES.index(stage)
    for later in STAGES[start:]:
        receipt = local_path(workspace, f".dse/{later}.json")
        if receipt.exists():
            receipt.unlink()
    before = report_files(workspace, stage)
    write_json(local_path(workspace, ".dse/input_manifest.json"), manifest)
    log = local_path(workspace, f".dse/{stage}.log")
    print(f"[hls_run] stage={stage} candidate={manifest['assignment']['candidate_id']}", flush=True)
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(args, cwd=workspace, stdout=output, stderr=subprocess.STDOUT,
                                check=False)
    if result.returncode:
        raise ValueError(f"{stage} failed (exit {result.returncode}); inspect {log}")
    policy_check(project, workspace, stage)
    if input_manifest(workspace, config) != manifest:
        raise ValueError("Inputs or tool identity changed while the stage was running")
    after = report_files(workspace, stage)
    fresh = {path: values[-1] for path, values in after.items() if before.get(path) != values}
    if not fresh:
        raise ValueError(f"{stage} produced no fresh recognized reports; inspect {log}")
    outputs = {}
    if stage == "csynth":
        for path in sorted((workspace / "hls_project").rglob("*")):
            local_path(workspace, path)
            if path.is_file() and "syn" in path.relative_to(workspace / "hls_project").parts:
                outputs[path.relative_to(workspace).as_posix()] = file_hash(path)
    receipt = {"stage": stage, "status": "completed",
               "candidate_id": manifest["assignment"]["candidate_id"],
               "input_digest": manifest["input_digest"], "command": args,
               "reports": fresh, "outputs": outputs, "log": str(log.relative_to(workspace))}
    write_json(local_path(workspace, f".dse/{stage}.json"), receipt)
    for path in fresh:
        print(workspace / path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace")
    parser.add_argument("mode", choices=(*STAGES, "all"))
    parser.add_argument("config", nargs="?", default="config.cfg")
    args = parser.parse_args()
    try:
        project = Path(os.environ.get("DSE_PROJECT_ROOT", os.getcwd())).resolve()
        workspace = local_path(project, args.workspace).resolve()
        config = local_path(workspace, args.config)
        policy_check(project, workspace, args.mode)
        if args.mode == "all":
            # Check the whole request before launching any stage.
            for executable in ("v++", "vitis-run"):
                if shutil.which(executable) is None:
                    raise ValueError(f"Required tool is unavailable: {executable}")
        for stage in STAGES if args.mode == "all" else (args.mode,):
            run_stage(project, workspace, stage, config)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"[hls_run] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
