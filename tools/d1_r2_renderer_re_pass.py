#!/usr/bin/env python3
"""Run the exact CUSA00219 owner-provided eboot renderer RE pass from R2.

The raw executable remains outside Git. This tool pulls the already-owned object
from the user's configured rclone remote, verifies exact identity, and runs the
renderer discovery stages added to this repository.

Default object:
  R2:houseofkublai/destiny/CUSA00219_01.33/eboot.bin

Identity:
  size   29,249,016 bytes
  sha256 672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_R2_OBJECT = "R2:houseofkublai/destiny/CUSA00219_01.33/eboot.bin"
EXPECTED_SIZE = 29_249_016
EXPECTED_SHA256 = "672f03411c0503dfbcda804cbb9fb27cdd9a8d73a8bcb71bf0c4f688073b0833"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_executable(path: Path) -> dict:
    size = path.stat().st_size
    sha256 = sha256_file(path)
    if size != EXPECTED_SIZE:
        raise RuntimeError(
            f"unexpected eboot size {size:,}; expected {EXPECTED_SIZE:,}"
        )
    if sha256 != EXPECTED_SHA256:
        raise RuntimeError(
            f"unexpected eboot SHA-256 {sha256}; expected {EXPECTED_SHA256}"
        )
    return {"path": str(path), "size": size, "sha256": sha256}


def run(command: list[str], *, cwd: Path) -> None:
    print("+", " ".join(str(x) for x in command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def fetch_r2(rclone: str, remote: str, destination: Path, *, repo: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            rclone,
            "copyto",
            remote,
            str(destination),
            "--s3-no-check-bucket",
            "--progress",
        ],
        cwd=repo,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--r2-object",
        default=DEFAULT_R2_OBJECT,
        help="rclone object path for the owner-provided decrypted eboot",
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("build/executable_renderer/672f03411c0503df"),
    )
    parser.add_argument(
        "--rclone",
        default="rclone",
        help="rclone executable name/path",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="reuse an already-downloaded verified eboot in work-dir",
    )
    parser.add_argument(
        "--skip-generic-probe",
        action="store_true",
        help="skip d1_executable_probe.py after identity verification",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    work = args.work_dir
    if not work.is_absolute():
        work = repo / work
    work.mkdir(parents=True, exist_ok=True)
    eboot = work / "eboot.bin"

    if not (args.reuse and eboot.exists()):
        if shutil.which(args.rclone) is None and not Path(args.rclone).exists():
            raise RuntimeError(
                f"rclone executable {args.rclone!r} is not available; "
                "install rclone or pass --rclone <path>"
            )
        fetch_r2(args.rclone, args.r2_object, eboot, repo=repo)

    identity = verify_executable(eboot)
    identity.update({
        "r2_object": args.r2_object,
        "status": "EXACT_OWNER_PROVIDED_EBOOT_VERIFIED",
    })
    identity_path = work / "identity.json"
    identity_path.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(identity, indent=2), flush=True)

    py = sys.executable
    if not args.skip_generic_probe:
        run(
            [
                py,
                "tools/d1_executable_probe.py",
                str(eboot),
                "--strings",
                "-o",
                str(work / "executable_probe.json"),
            ],
            cwd=repo,
        )

    run(
        [
            py,
            "tools/d1_executable_renderer_strings.py",
            str(eboot),
            "-o",
            str(work / "renderer_strings.json"),
        ],
        cwd=repo,
    )

    next_steps = {
        "status": "D1_RENDERER_RAW_EXECUTABLE_FRONTIER_READY",
        "identity": identity,
        "renderer_strings": str(work / "renderer_strings.json"),
        "next": [
            (
                "Run Ghidra auto-analysis + D1ExportCodeGraph.py on this exact "
                "eboot, normalize the graph, then run "
                "d1_executable_renderer_frontier.py."
            ),
            (
                "Run D1ExportRendererSlices.py on the ranked frontier to recover "
                "material-state, draw-submit, G-buffer, light and post-process "
                "control/data flow."
            ),
        ],
    }
    (work / "NEXT.json").write_text(
        json.dumps(next_steps, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(next_steps, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
