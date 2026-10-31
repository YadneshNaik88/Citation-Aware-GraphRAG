# CHANGELOG.md

All notable changes, protocol revisions, and layout adjustments to this project are documented in this file.

## [Unreleased] - Phase 0

### Added
- Repository skeleton adhering strictly to `docs/ARCHITECTURE.md` Section 5 layout (T0.1).
- Empty source packages under `src/`: `data`, `kg`, `embed`, `topics`, `forecast`, `rag`, `verify`, `gaps`, `app`, `common`.
- Pinned Python minor version to `3.13` with wheel verification notes in `docs/ENVIRONMENT_NOTES.md`.
- Base dependencies pinned in `requirements.txt` (`pytest`, `ruff`, `pyyaml`) and full resolved lockfile in `requirements-lock.txt`.
- Cross-platform `Makefile` with targets: `setup`, `test`, `lint`, `leakage`, `lock`.
- Environment reporting tool `scripts/env_report.py` and unit test `tests/test_env_report.py`.
- Repository layout test `tests/test_repo_layout.py` ensuring canonical directories exist and forbidding competing directories or duplicate root documentation.
- GitHub Actions CI workflow in `.github/workflows/ci.yml`.

### Changed
- Consolidated all project documentation (`ARCHITECTURE.md`, `PROTOCOL.md`, `PHASE_0_PROMPTS.md`) strictly under `docs/`; removed duplicate root copies.
- Added `pyproject.toml` to canonical root-file list in `docs/ARCHITECTURE.md` Section 5.
