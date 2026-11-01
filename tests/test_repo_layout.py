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
    "pyproject.toml",
    "requirements.txt",
    "requirements-lock.txt",
]

CANONICAL_DOC_FILES = [
    "docs/ARCHITECTURE.md",
    "docs/PROTOCOL.md",
    "docs/PHASE_0_PROMPTS.md",
    "docs/ENVIRONMENT_NOTES.md",
]

FORBIDDEN_ROOT_DUPLICATE_FILES = [
    "ARCHITECTURE.md",
    "PROTOCOL.md",
    "PHASE_0_PROMPTS.md",
]


def check_forbidden_folders(root_dir: Path) -> list[str]:
    """Return any forbidden competing folders found in root_dir."""
    found = []
    for folder in FORBIDDEN_COMPETING_FOLDERS:
        if (root_dir / folder).is_dir():
            found.append(folder)
    return found


def check_forbidden_root_duplicates(root_dir: Path) -> list[str]:
    """Return any forbidden duplicate documentation files found in root_dir."""
    found = []
    for filename in FORBIDDEN_ROOT_DUPLICATE_FILES:
        if (root_dir / filename).is_file():
            found.append(filename)
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
    """Assert required root files exist."""
    repo_root = Path(__file__).resolve().parent.parent

    for filename in CANONICAL_ROOT_FILES:
        f = repo_root / filename
        assert f.is_file(), f"Canonical root file missing: {filename}"


def test_canonical_doc_files_exist() -> None:
    """Assert canonical documentation exists only inside docs/."""
    repo_root = Path(__file__).resolve().parent.parent

    for doc_path in CANONICAL_DOC_FILES:
        f = repo_root / doc_path
        assert f.is_file(), f"Canonical doc file missing: {doc_path}"


def test_no_duplicate_root_docs() -> None:
    """Assert duplicate copies of docs do not exist at repository root."""
    repo_root = Path(__file__).resolve().parent.parent
    duplicates = check_forbidden_root_duplicates(repo_root)
    assert not duplicates, (
        f"Forbidden duplicate documentation files found in repository root: {duplicates}. "
        "Canonical documentation must reside solely inside docs/."
    )


def test_layout_fails_if_duplicate_root_docs_added(tmp_path: Path) -> None:
    """Verify that adding duplicate docs to root is caught and causes layout test failure."""
    for duplicate_name in FORBIDDEN_ROOT_DUPLICATE_FILES:
        fake_file = tmp_path / duplicate_name
        fake_file.write_text("duplicate", encoding="utf-8")

    duplicates = check_forbidden_root_duplicates(tmp_path)
    for duplicate_name in FORBIDDEN_ROOT_DUPLICATE_FILES:
        assert duplicate_name in duplicates, f"Failed to detect root duplicate: {duplicate_name}"


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
