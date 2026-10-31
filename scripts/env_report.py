#!/usr/bin/env python3
"""Environment reporting script.

Collects and records Python version, OS details, installed packages, and
accelerator visibility (CUDA, MPS, ROCm, or none) without assuming any hardware.
Saves the report under runs/env_report.json.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def get_git_info() -> Dict[str, str]:
    """Retrieve git branch and commit if available."""
    info: Dict[str, str] = {"commit": "unknown", "branch": "unknown"}
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
        info["commit"] = commit
    except Exception:
        pass

    try:
        branch = (
            subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
        if branch:
            info["branch"] = branch
        else:
            branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
                )
                .decode("utf-8")
                .strip()
            )
            info["branch"] = branch
    except Exception:
        pass

    return info


def get_installed_packages() -> Dict[str, str]:
    """List all installed packages and their exact versions."""
    packages: Dict[str, str] = {}
    distributions = sorted(
        importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower()
    )
    for dist in distributions:
        name = dist.metadata["Name"]
        packages[name] = dist.version
    return packages


def detect_accelerators() -> Dict[str, Any]:
    """Detect available hardware accelerators without assuming any GPU."""
    accelerator_info: Dict[str, Any] = {
        "available": False,
        "type": "none",
        "devices": [],
        "details": "No GPU/accelerator detected; CPU-only execution.",
    }

    # Attempt PyTorch detection if installed
    try:
        import torch  # type: ignore

        if hasattr(torch, "cuda") and torch.cuda.is_available():
            count = torch.cuda.device_count()
            devices = [torch.cuda.get_device_name(i) for i in range(count)]
            accelerator_info["available"] = True
            accelerator_info["type"] = "cuda"
            accelerator_info["devices"] = devices
            device_str = ", ".join(devices)
            accelerator_info["details"] = f"CUDA available with {count} device(s): {device_str}"
            return accelerator_info

        if (
            hasattr(torch, "backends")
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
        ):
            accelerator_info["available"] = True
            accelerator_info["type"] = "mps"
            accelerator_info["devices"] = ["Apple Silicon MPS"]
            accelerator_info["details"] = "Apple Silicon MPS accelerator available."
            return accelerator_info
    except Exception:
        pass

    # Check for nvidia-smi as fallback
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            devices = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
            if devices:
                accelerator_info["available"] = True
                accelerator_info["type"] = "nvidia-smi"
                accelerator_info["devices"] = devices
                device_str = ", ".join(devices)
                accelerator_info["details"] = (
                    f"nvidia-smi detected {len(devices)} device(s): {device_str}"
                )
                return accelerator_info
    except Exception:
        pass

    return accelerator_info


def collect_environment_report() -> Dict[str, Any]:
    """Collect full environment data dictionary."""
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "version": platform.python_version(),
            "build": platform.python_build(),
            "compiler": platform.python_compiler(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "git": get_git_info(),
        "accelerator": detect_accelerators(),
        "packages": get_installed_packages(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate environment report.")
    parser.add_argument(
        "--output",
        type=str,
        default="runs/env_report.json",
        help="Path where JSON report will be saved (default: runs/env_report.json)",
    )
    args = parser.parse_args()

    report = collect_environment_report()

    git_rev = report["git"]["commit"]
    git_rev_short = git_rev[:8] if len(git_rev) >= 8 else git_rev

    # Print summary to stdout
    print("=" * 60)
    print("ENVIRONMENT REPORT")
    print("=" * 60)
    print(f"Timestamp (UTC): {report['timestamp_utc']}")
    print(f"Python Version : {report['python']['version']} ({report['python']['implementation']})")
    print(f"Executable     : {report['python']['executable']}")
    print(f"OS Platform    : {report['os']['platform']} ({report['os']['machine']})")
    print(f"Git Branch/Rev : {report['git']['branch']} @ {git_rev_short}")
    print(f"Accelerator    : {report['accelerator']['details']}")
    print(f"Total Packages : {len(report['packages'])}")
    print("=" * 60)

    # Save to file
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Saved complete environment report to: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
