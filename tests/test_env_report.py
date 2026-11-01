"""Tests for scripts/env_report.py verifying hardware-agnostic operation."""

import json
import subprocess
import sys
from pathlib import Path

from scripts.env_report import collect_environment_report, detect_accelerators


def test_collect_environment_report_schema() -> None:
    """Verify that collect_environment_report returns all required fields."""
    report = collect_environment_report()

    assert "python" in report
    assert "version" in report["python"]
    assert "os" in report
    assert "system" in report["os"]
    assert "platform" in report["os"]
    assert "git" in report
    assert "accelerator" in report
    assert "available" in report["accelerator"]
    assert "type" in report["accelerator"]
    assert "details" in report["accelerator"]
    assert "packages" in report
    assert isinstance(report["packages"], dict)


def test_env_report_runs_without_gpu(monkeypatch) -> None:
    """Test that detect_accelerators succeeds on a machine with no GPU or torch."""
    import sys

    # Remove torch from sys.modules if imported or mock it
    monkeypatch.setitem(sys.modules, "torch", None)

    # Mock subprocess.run to simulate absence of nvidia-smi
    def mock_subprocess_run(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi not found")

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    result = detect_accelerators()
    assert result["available"] is False
    assert result["type"] == "none"
    assert "No GPU/accelerator detected" in result["details"]


def test_env_report_cli_execution(tmp_path: Path) -> None:
    """Test CLI execution of scripts/env_report.py writing to specified output."""
    out_file = tmp_path / "env_report.json"
    repo_root = Path(__file__).resolve().parent.parent
    script_path = repo_root / "scripts" / "env_report.py"

    cmd = [sys.executable, str(script_path), "--output", str(out_file)]
    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 0, f"env_report.py failed: {res.stderr}"
    assert out_file.is_file(), "env_report.json was not created"

    with open(out_file, encoding="utf-8") as f:
        data = json.load(f)

    assert "python" in data
    assert "os" in data
    assert "accelerator" in data
    assert "packages" in data
