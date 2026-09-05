#!/usr/bin/env python3
"""Input fingerprints, receipt verification, and exclusive candidate snapshots."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


def read_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")
    temporary.replace(path)


def local_path(root, value):
    root = Path(root).resolve()
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    if ".." in path.parts:
        raise ValueError(f"Parent traversal is not allowed: {value}")
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path is outside the workspace: {value}") from exc
    cursor = root
    for part in relative.parts:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError(f"Symlinks are not tracked inputs/evidence: {cursor}")
    return path


def listed_files(root, paths):
    found = {}
    for value in paths:
        path = local_path(root, value)
        if not path.exists():
            raise ValueError(f"Missing input: {path}")
        children = [path] if path.is_file() else sorted(path.rglob("*"))
        for child in children:
            local_path(root, child)
            if child.is_file():
                found[child.relative_to(root).as_posix()] = file_hash(child)
    return dict(sorted(found.items()))


def tool_identity():
    identity = {}
    for name in ("v++", "vitis-run"):
        executable = shutil.which(name)
        if executable:
            path = Path(executable).resolve()
            identity[name] = {"path": str(path), "sha256": file_hash(path)}
        else:
            identity[name] = None
    return identity


def input_manifest(workspace, config, toolchain=None):
    workspace = Path(workspace).resolve()
    assignment = read_json(local_path(workspace, ".dse/assignment.json"))
    for key in ("benchmark", "run_id", "candidate_id", "role"):
        if not isinstance(assignment.get(key), str) or not assignment[key]:
            raise ValueError(f"Assignment requires {key}")
    paths = assignment.get("input_paths")
    if not isinstance(paths, list) or not paths or not all(isinstance(p, str) for p in paths):
        raise ValueError("Assignment requires a nonempty input_paths list")
    for value in paths:
        relative = local_path(workspace, value).relative_to(workspace)
        if not relative.parts or relative.parts[0] in (".dse", "hls_project"):
            raise ValueError("List input trees explicitly; exclude .dse and generated hls_project")
    config = local_path(workspace, config).relative_to(workspace).as_posix()
    payload = {
        "assignment": assignment,
        "config": config,
        "files": listed_files(workspace, paths + [config]),
        "toolchain": tool_identity() if toolchain is None else toolchain,
    }
    return {**payload, "input_digest": digest(payload)}


def verify_inputs(workspace):
    workspace = Path(workspace).resolve()
    manifest = read_json(local_path(workspace, ".dse/input_manifest.json"))
    current = input_manifest(workspace, manifest["config"], manifest["toolchain"])
    if current != manifest:
        raise ValueError("Input files or assignment no longer match the recorded manifest")
    return manifest


def verify_receipt(workspace, stage, input_digest):
    workspace = Path(workspace).resolve()
    receipt = read_json(local_path(workspace, f".dse/{stage}.json"))
    if receipt.get("stage") != stage or receipt.get("status") != "completed":
        raise ValueError(f"No completed {stage} receipt")
    if receipt.get("input_digest") != input_digest:
        raise ValueError(f"Stale {stage} receipt: input digest differs")
    reports = receipt.get("reports")
    if not isinstance(reports, dict) or not reports:
        raise ValueError(f"No report evidence for {stage}")
    for relative, expected in reports.items():
        path = local_path(workspace, relative)
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"Changed or missing {stage} report: {relative}")
    for relative, expected in receipt.get("outputs", {}).items():
        path = local_path(workspace, relative)
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"Changed or missing {stage} output: {relative}")
    return receipt


def verify(workspace):
    workspace = Path(workspace).resolve()
    manifest = verify_inputs(workspace)
    stages = []
    for stage in ("csim", "csynth", "cosim", "impl"):
        if local_path(workspace, f".dse/{stage}.json").exists():
            verify_receipt(workspace, stage, manifest["input_digest"])
            stages.append(stage)
    return {"input_digest": manifest["input_digest"], "verified_receipts": stages}


def snapshot_files(root):
    root = Path(root).resolve()
    return listed_files(root, [p.name for p in sorted(root.iterdir())])


def archive(workspace, result_file, destination):
    workspace = Path(workspace).resolve()
    result_file = Path(result_file).resolve()
    destination = Path(destination).absolute()
    if destination.is_relative_to(workspace):
        raise ValueError("Archive destination cannot be inside the source workspace")
    # Reject symlinks in the destination path before creating any directories.
    local_path(Path(destination.anchor), destination)
    result = read_json(result_file)
    before = snapshot_files(workspace)
    result_digest = file_hash(result_file)
    try:
        validation = verify(workspace)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # Failed/incomplete candidates still need preservation, not promotion.
        validation = {"verification_error": str(exc)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(exist_ok=False)
    shutil.copytree(workspace, destination / "workspace", symlinks=False)
    shutil.copy2(result_file, destination / "result.json")
    after = snapshot_files(destination / "workspace")
    if before != after or before != snapshot_files(workspace):
        raise ValueError(f"Workspace changed during archive; snapshot is incomplete: {destination}")
    if file_hash(result_file) != result_digest or file_hash(destination / "result.json") != result_digest:
        raise ValueError(f"Result changed during archive; snapshot is incomplete: {destination}")
    record = {"candidate_id": result.get("id"), "files": after,
              "result_sha256": result_digest, "verification": validation}
    write_json(destination / "snapshot.json", record)
    return {"archive": str(destination), "snapshot_digest": digest(record), **validation}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    check = sub.add_parser("verify")
    check.add_argument("workspace")
    save = sub.add_parser("archive")
    save.add_argument("workspace")
    save.add_argument("result_file")
    save.add_argument("destination")
    args = parser.parse_args()
    try:
        output = (verify(args.workspace) if args.operation == "verify" else
                  archive(args.workspace, args.result_file, args.destination))
        print(json.dumps(output, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
