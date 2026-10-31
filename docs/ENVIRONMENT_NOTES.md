# ENVIRONMENT_NOTES.md

## Python Minor Version Selection

- **Selected Version:** Python 3.13 (pinned in `.python-version` as `3.13`)
- **Host Testing Environment:** Python 3.13.14 (64-bit) on Windows 10 (version 10.0.19045, AMD64; platform `Windows-10-10.0.19045-SP0`)
- **Date Verified:** October 2026

## Package Wheel Verification Evidence

In accordance with AGENTS.md Section 4 and docs/PHASE_0_PROMPTS.md T0.1, the Python minor version was selected after verifying that wheels exist and resolve cleanly for all planned downstream libraries:

| Package | Resolved Version | Wheel Architecture / ABI | Compatibility Verification |
|---|---|---|---|
| `torch` (PyTorch) | 2.13.0+cpu | `win_amd64` / CPython 3.13 | Prebuilt wheel installed; verified via live import: `import torch; print(torch.__version__)` -> `2.13.0+cpu` |
| `faiss-cpu` | 1.15.1 | `win_amd64` / CPython 3.13 | Prebuilt wheel installed; verified via live import: `import faiss; print(faiss.__version__)` -> `1.15.1` |
| `duckdb` | 2.0.0 | `duckdb-2.0.0-cp312-abi3-win_amd64.whl` | PyPI prebuilt wheel uses CPython Limited API / Stable ABI (`abi3`), compatible with Python 3.12+ and 3.13 |
| `polars` | 2.1.0 | `polars_runtime_32-2.1.0-cp311-abi3-win_amd64.whl` | PyPI prebuilt wheel uses CPython Limited API / Stable ABI (`abi3`), compatible with Python 3.11+ and 3.13 |
| `transformers` | 4.57.6 | `transformers-4.57.6-py3-none-any.whl` | Universal wheel (`py3-none-any`); resolved via pip dry-run resolver without conflict |
| `adapters` | 1.3.0 | `adapters-1.3.0-py3-none-any.whl` | Universal wheel (`py3-none-any`); resolved via pip dry-run resolver without conflict |

## Downstream Compatibility and PyTorch Planning

### 1. T0.3 Full Package Combination Compatibility
While preliminary dry-run resolution and isolated wheel imports succeed under Python 3.13, full runtime compatibility of the combined heavy stack (`torch` + `transformers` + `adapters` + `faiss-cpu`) remains to be established during the actual installation and sustained throughput benchmark in task T0.3. Python 3.13 remains pinned as the baseline pending those benchmark results.

### 2. Proposed PyTorch Installation Architecture
Because PyTorch builds are strictly hardware- and OS-dependent (e.g., CUDA compute versions on Linux, CPU-only wheels on Windows, MPS on macOS), pinning an exact platform wheel in a single universal `requirements-lock.txt` can break cross-platform portability.

- **Proposed Strategy:** Keep platform-specific PyTorch builds outside the shared cross-platform lock file. Provide environment-specific installation recipes (e.g., `requirements-torch-cpu.txt`, `requirements-torch-cuda.txt`) separately pinned and documented per build environment.
- **Status:** Planning only; not implemented without formal team review and approval.

## Dependency Management Policy

1. **Virtual Environment:** Every team member operates within the isolated `.venv` directory created by `make setup`.
2. **Direct vs. Locked Dependencies:**
   - `requirements.txt`: Records exact `==` pins for direct dependencies only (`pytest`, `ruff`, `pyyaml`).
   - `requirements-lock.txt`: Complete, resolved dependency tree generated directly by `pip freeze` from a clean virtual environment.
3. **Hardware Agnosticism:**
   - The repository operates out of the box on CPU.
   - `scripts/env_report.py` dynamically probes whether CUDA, ROCm, or Apple MPS accelerators are available without hardcoding assumptions.
