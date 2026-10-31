# AGENTS.md: rules for every AI agent in this repository

Before any task, read `docs/ARCHITECTURE.md` and `docs/PROTOCOL.md`. If a task prompt conflicts with them, they win: stop and write the conflict to `OPEN_QUESTIONS.md`.

## 1. Non-negotiable rules
1. **Never invent facts.** Do not guess API fields, column names, model names, adapter names, library functions, paper IDs or numbers. Check the official docs, the installed package (`help()`, `--help`), or a real API response. If it cannot be verified, add it to `OPEN_QUESTIONS.md` and stop that sub-task.
2. **Temporal firewall** (PROTOCOL.md section 3). Track `d_pub`, `D_snap` and `T_cut` separately. Use only helpers in `src/common/time_guard.py` to filter by cutoff. A citation edge is visible only if both endpoints are visible. Present-day citation measures (`cited_by_count`, `counts_by_year`, `fwci`, citation percentiles) are display-only: store them only in `display_`-prefixed columns, never use them in features, sampling, labels, ranking or training. Every feature must be computable from records visible at `T_cut` alone; label-window quantities (`f`, `E_f`) never appear in feature tables.
3. **No number without a run.** Every number in a note, table or README comes from a logged run: `runs/<run_id>/metrics.json` with config, git commit, seed, data build ID. Never write remembered or "expected" results.
4. **Frozen definitions.** Do not change PROTOCOL.md sections marked FROZEN or any calibrated threshold. Propose changes in `CHANGELOG.md`.
5. **Tests before done.** A task is done only when its acceptance tests pass and the output is pasted into its note.
6. **Stop conditions.** Stop and report if: a test fails twice for unclear reasons; a step needs a credential or data you do not have; a design decision would change the protocol; a step would exceed the stated budget (API cost, memory, disk).

## 2. API and budget rules
- OpenAlex key and LLM key come from environment variables only. Never in code, configs, logs, notes or commits. Never print or log full request URLs containing a key; strip `api_key` from cache keys and logs.
- Every OpenAlex call goes through the shared client in `src/common/openalex_client.py` (rate limiting, retries with exponential backoff, hash-keyed cache, spend ledger). No direct `requests` calls elsewhere.
- Use `per_page=100`, `select=` only needed fields, cursor paging past 10,000 results. No dataset-scale cursor paging: harvests are throttled, resumable and checkpointed per harvest unit (topic-year).
- Every script has a hard `--max-cost-usd` and `--max-calls` argument with a conservative default. Check `/rate-limit` before large jobs.
- Evaluation builds run in replay mode: live calls disabled and a test enforces it.

## 3. Resource rules (hardware-agnostic)
- Never load a full table into pandas. Use DuckDB or Polars lazily, chunked, column-pruned.
- All long jobs are resumable, idempotent, seeded, and write manifests; a shard or artifact is either complete or absent (write to a temp path, then atomic rename).
- Batch sizes and corpus stages come from measured benchmarks recorded in `docs/results_notes/`, never from guesses.
- Large artifacts (`data/`, `runs/`, model files) are git-ignored. Commit code, configs, small metrics, figures and notes only.

## 4. Code conventions
- **Layout:** the only canonical repository layout is `docs/ARCHITECTURE.md` section 5. Configuration lives in `configs/` (never `config/`). Do not create competing folders or move modules; a new top-level folder needs a `CHANGELOG.md` entry approved by a reviewer.
- Config-driven (`configs/*.yaml`): no hard-coded paths, cutoffs, seeds, thresholds, budgets.
- Type hints and docstrings on public functions; `ruff` for lint; `pytest` for tests.
- Modules: `src/{data,kg,embed,topics,forecast,rag,verify,gaps,app,common}`.
- Stable identity: OpenAlex work ID is canonical; integer node IDs are append-only.

### Environment and dependency pinning
- One Python minor version for everyone and CI, written in `.python-version` (chosen in T0.1 after checking that the planned packages publish compatible wheels; never assumed).
- Every member works in a project virtual environment (`.venv`, git-ignored) created by `make setup`.
- `requirements.txt` lists **direct** dependencies with exact `==` versions. `requirements-lock.txt` is the full resolved set (`pip freeze` from a clean environment) and is what CI and `make setup` install. Never guess a version: resolve it by installing in a clean environment and recording what was installed.
- Add a dependency only when a task uses it; the PR states why and shows the lock-file diff. Packages for later phases are not pre-installed.
- Hardware-dependent builds (for example the CPU or CUDA build of PyTorch) are documented in `docs/ENVIRONMENT_NOTES.md` per machine type; the project never assumes a GPU. `scripts/env_report.py` records Python, OS, package versions and accelerator availability into every run's metadata.
- Model artifacts are pinned by the exact Hugging Face revision (commit hash) that was loaded, recorded in the build manifest. Seeds come from `configs/`, and training or sampling code sets Python, NumPy and (if used) PyTorch seeds.
- Secrets: names only in `.env.example` (`OPENALEX_API_KEY`, `GROQ_API_KEY` as team convention); real values only in each member's environment, never committed.

## 5. LLM and evidence rules
- Generated output is structured: `{claim, paper_ids[], supporting_sentence}`. Every ID must be in the evidence set for that query; reject unknown IDs.
- Only evidence-eligible papers (abstract present, accepted type and language) go to the LLM. Metadata-only records are never used as evidence.
- Evidence is tagged "abstract only". Do not assert sample sizes, effect sizes or methods unless the number appears in the cited abstract.
- Unsupported claims are removed or flagged, never silently kept. Never fabricate citations, authors or quotes.
- Log prompt, model name and version, temperature and raw output for every evaluation run.

## 6. Reporting rules
- Search reports have three separate parts: API accounting, channel contribution, and (offline only) measured benchmark recall. Never compute "coverage" as fetched divided by API-reported matches.
- Use "candidate underexplored relationship", never "novel gap".

## 7. Working method for each task
1. Restate the task and acceptance tests.
2. Inspect real inputs (a small sample) before writing code.
3. Implement the smallest version; run tests.
4. Write `docs/results_notes/<task_id>.md`: what was done, commands, test output, run IDs, limitations, open questions.
5. One task per branch (`phaseX/<task-id>-<short-name>`); open a pull request; do not push to `main`.

## 8. Commands (kept current in the Makefile)
`make setup`, `make test`, `make lint`, `make leakage`.

## 9. Definition of done
Acceptance tests pass; leakage audit passes if data was touched; lint clean; note written; PR opened; no secrets or large files committed.
