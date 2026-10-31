"""Tests enforcing the canonical repository layout from docs/ARCHITECTURE.md Section 5."""

from pathlib import Path

CANONICAL_SRC_PACKAGES = [
    "data",
    "kg",
    "embed",
    "topics",
    "forecast",
    "rag",
    "verify",
    "gaps",
    "app",
    "common",
]

CANONICAL_FOLDERS = [
    "configs",
    "tests",
    "scripts",
    "docs",
    "docs/results_notes",
    "docs/annotation",
    ".agents/rules",
]

FORBIDDEN_COMPETING_FOLDERS = [
    "config",
    "source",
    "utils",
    "data_raw",
]

CANONICAL_ROOT_FILES = [
    "AGENTS.md",
    ".gitignore",
    ".python-version",
    ".env.example",
    "Makefile",
    "CHANGELOG.md",
    "OPEN_QUESTIONS.md",
    "requirements.txt",
    "requirements-lock.txt",
]


def check_forbidden_folders(root_dir: Path) -> list[str]:
    """Return any forbidden competing folders found in root_dir."""
    found = []
    for folder in FORBIDDEN_COMPETING_FOLDERS:
        if (root_dir / folder).is_dir():
            found.append(folder)
    return found


def test_canonical_directories_exist() -> None:
    """Assert all canonical repository directories exist."""
    repo_root = Path(__file__).resolve().parent.parent

    for folder in CANONICAL_FOLDERS:
        p = repo_root / folder
        assert p.is_dir(), f"Canonical directory missing: {folder}"

    for pkg in CANONICAL_SRC_PACKAGES:
        pkg_dir = repo_root / "src" / pkg
        assert pkg_dir.is_dir(), f"Canonical source package missing: src/{pkg}"
        init_file = pkg_dir / "__init__.py"
        assert init_file.is_file(), f"Missing __init__.py in src/{pkg}"


def test_canonical_root_files_exist() -> None:
    """Assert required root files and documents exist."""
    repo_root = Path(__file__).resolve().parent.parent

    for filename in CANONICAL_ROOT_FILES:
        f = repo_root / filename
        assert f.is_file(), f"Canonical root file missing: {filename}"

    # Documentation in docs/
    assert (repo_root / "docs" / "ARCHITECTURE.md").is_file(), "docs/ARCHITECTURE.md is missing"
    assert (repo_root / "docs" / "PROTOCOL.md").is_file(), "docs/PROTOCOL.md is missing"
    assert (repo_root / "docs" / "ENVIRONMENT_NOTES.md").is_file(), (
        "docs/ENVIRONMENT_NOTES.md is missing"
    )


def test_no_competing_folders() -> None:
    """Assert known competing folders do not exist."""
    repo_root = Path(__file__).resolve().parent.parent
    violations = check_forbidden_folders(repo_root)
    assert not violations, f"Forbidden competing folder(s) found in repository root: {violations}"


def test_layout_fails_if_config_folder_added(tmp_path: Path) -> None:
    """Verify that adding a competing 'config/' folder is properly detected and causes failure."""
    fake_config = tmp_path / "config"
    fake_config.mkdir(parents=True)

    violations = check_forbidden_folders(tmp_path)
    assert "config" in violations, "Detector failed to identify competing 'config/' directory."
