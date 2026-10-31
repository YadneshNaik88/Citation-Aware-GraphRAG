# PROTOCOL.md: research protocol (v1.0, replaces the snapshot-based v0.1)

Project: Citation-Aware Graph-RAG for Evidence-Grounded Scientific Trend Detection and Research-Gap Discovery.
Status: DRAFT until the guide signs it off. After sign-off, sections marked **[FROZEN]** change only through a dated entry in `CHANGELOG.md`.

Tags: **[V]** verified from official documentation (Oct 2026); **[E]** estimate to be replaced by a measurement; **[?]** must be verified or measured in Phase 0/1; **[R]** team decision or recommendation.

---

## 1. Purpose and claims

Build and scientifically evaluate a platform that (a) retrieves literature with global OpenAlex discovery plus local semantic and citation-graph retrieval, (b) generates evidence-grounded syntheses, (c) detects and forecasts emerging, declining, burst and sustained research topics, and (d) proposes candidate research gaps tested against future publications.

The platform must never claim that: a gap is novel because a paper is missing from the local corpus or from OpenAlex; retrieval is exhaustive; a verbatim quote proves a claim is true; abstracts support claims that need full-text detail.

## 2. Data source and acquisition **[V unless tagged]**

- Source: OpenAlex **API only**. The full snapshot is out of scope.
- Paging: basic paging stops at 10,000 results; `per_page` max 100; use cursor paging beyond that. The docs discourage dataset-scale cursor paging, so harvests are throttled, selective and resumable.
- Search: keyword `search` (uppercase AND/OR/NOT, quoted phrases, stemming; `search.exact` disables stemming; URL length about 4 KB). `search.semantic`: up to 50 results, first 2,000 characters of the query, one request per second, cannot be combined with other search parameters, `cited_by_count` and institution-country filters unsupported.
- Filters listed in the works reference: `primary_topic.id`, `primary_topic.subfield.id`, `topics.id`, `publication_year`, `from_publication_date`, `type`, `language`, `has_abstract`, `openalex`, `cites`, `cited_by`, `referenced_works`. Group-by listed for `primary_topic.id`, `primary_topic.subfield.id`, `topics.id`, `publication_year`, `type`, `language`, `has_abstract`. Groups: up to 200 per page, cursor paging, sorted by key. The grouping guide does not show topic or year examples, so **[?]** confirm by pilot.
- Cost (OpenAlex pricing page): free key gives $1/day; list+filter about $0.0001 per call, keyword search about $0.001, semantic search listed inconsistently across pages, so read the real value from the `/rate-limit` endpoint **[?]**; singleton lookups free.
- Classification: 4 domains, 26 fields, about 250 subfields, about 4,500 topics. Each work has a `primary_topic` and up to three ranked `topics`. Topics are model-assigned, not human labels.
- `abstract_inverted_index` can be null. Abstract text is rebuilt from the inverted index.
- The API excludes the expansion (XPAC) corpus by default. Keep the default and document it.

### 2.1 Tier A (broad metadata, all disciplines)
Topic-year counts, field and subfield totals, and unordered topic co-assignment counts by year, from grouped queries. Fallback if grouping is unsupported or too costly: per-topic, per-year filtered count queries. Citation flow between topics is derived from Tier B only.

### 2.2 Tier B (semantic corpus)
Stratified by subfield, topic and year, topic-coherent, requiring abstracts. **Never select by citation count** (present-day counts include future citations). Origin tags: `seed_sample`, `closure` (papers frequently referenced by in-corpus papers, counted only over edges visible at the cutoff), `query_discovered` (live app only). Stage sizes (10k, 100k, 500k, larger) are **infrastructure benchmarks, not limits on discovery**. A stage is passed only when measured resource headroom is adequate, retrieval quality still improves materially, and graph density is adequate.

## 3. Time axes and the temporal firewall **[FROZEN]**

Three axes, never conflated:

| Axis | Symbol | Rule |
|---|---|---|
| Publication date | `d_pub(p)` | Stored per record. Year-only dates are treated as 31 December. Records without a usable date are excluded from evaluation builds and logged |
| Data snapshot date | `D_snap` | Harvest window recorded in the build manifest and per record `retrieved_at`. Must be later than the end of the label window |
| Evaluation cutoff | `T_cut` | A record is visible only if `d_pub ≤ T_cut` |

Rules:
1. Each evaluation build has a manifest with: harvest window, taxonomy copy and content hash, `T_cut`, label window, API parameters, fixed type filter, software and model versions.
2. Evaluation builds are **frozen and replay-only**: all API responses come from the request cache; live calls are disabled and a test enforces it.
3. Builds from different snapshots are never mixed. A refresh creates a new build ID.
4. A **node** is visible iff `d_pub ≤ T_cut`. A **citation edge A→B** is visible iff both endpoints are visible and in the corpus, i.e. its date is `max(d_pub(A), d_pub(B))`. Edges whose cited paper is dated after the citing paper are excluded from evaluation builds and counted as anomalies **[?]** rate to measure.
5. Present-day citation measures (`cited_by_count`, `counts_by_year`, `fwci`, citation percentiles) are **display-only metadata**. They may be stored under `display_`-prefixed columns and shown in the interface or descriptive reports, but must never be used in feature building, sampling or selection, labels, retrieval or ranking scores, or model training. Any feature must be computable from records visible at `T_cut` alone (verified by the truncation-invariance test in T0.4).
6. Text embeddings depend only on a paper's own text and may be computed once, but every index query filters on visibility at `T_cut`.
7. Threats to validity to report: (a) retrospective topic reassignment (topics are assigned by a snapshot-time model, so history may be partly constructed in hindsight; direction of effect unknown without a second snapshot), (b) retrospective metadata updates (abstracts, references, dates, merges and deletions), (c) hindsight completeness (late-indexed works appear in the past), (d) SPECTER2 was trained on citation triplets and the chronology of its training data is **[?]** unknown, so vectors may encode post-cutoff citation relations.
8. Scope of claims: results are "as of snapshot `D_snap`", not a reconstruction of what was knowable at `T_cut`.

## 4. Trend definitions **[thresholds calibrated on early rolling origins only, then FROZEN]**

Unit: OpenAlex topic via `primary_topic`. `N_t(y)` = count; share `s_t(y) = N_t(y) / N_field(y)`.
- **Emerging:** share significantly above the base window (count test, Poisson or negative binomial, Benjamini–Hochberg false-discovery control within field), effect-size ratio above a threshold, minimum volume.
- **Declining:** the reverse.
- **Burst:** significant rise that does not persist (last-year share falls back).
- **Sustained:** elevated across consecutive years including the last.
Targets: log share at horizons of 1, 2 and 3 years; emerging class over the next 3 years; ranking by share change. Methods: year-over-year growth, linear regression on log share, ARIMA, ETS, then gradient boosting. Temporal GNN is an optional experiment only.
Validation: multiple rolling origins (each year from the early 2010s through 2019 with label windows ending ≤ 2022). Hyperparameters and thresholds use only these. The final model is applied at origin 2022 and tested once on 2023–2025.

## 5. Research-gap definition and labels **[FROZEN after calibration]**

**Candidate research gap:** an *unordered* topic pair with a high predicted probability of becoming co-assigned and a low observed co-assignment, plus an evidence package and generated research question that passed counterevidence checks, with a cautious confidence level. Confidence levels: Rejected (bridging work found), Speculative, Candidate, Expert-reviewed. The UI never says "novel".

### 5.1 Pairs
Unordered pairs {A, B}, A ≠ B, canonical key (smaller ID first). All features symmetric; any asymmetric quantity enters as min/max or sum/absolute difference. Citation flow `f(A→B)` and `f(B→A)` stays directed and separate (Tier B only, edges visible at cutoff) and is **not** part of the label. Optional ablation: symmetric summaries of flow as features.

### 5.2 Label definition
Co-assignment means both topics appear in a work's topic list (up to three). At cutoff `T`: `N_A`, `N_B` visible works per topic, `W` total visible works, `b` cumulative co-assigned count up to `T`, `f` co-assigned count in `(T, T+3 years]`. Expected counts under independence: `E_b = N_A·N_B/W` (visible marginals at `T`) and `E_f = N_A^f·N_B^f/W^f`, where `N_A^f`, `N_B^f`, `W^f` are the corresponding counts in the label window. `f`, `E_f` and every other label-window quantity define labels only and must never appear in any feature table (enforced by the leakage tests, PHASE_0_PROMPTS.md T0.4).

| Category | Conditions | Use |
|---|---|---|
| Ineligible | Either topic below `n_min` works in the 3 years before `T` or in the label window, or `E_b < e_min` | Excluded (not a negative) |
| Already connected | `b > c` | Outside the gap universe |
| Positive | Eligible, `b ≤ c`, `f ≥ k`, and `f` significantly above `E_f` (Poisson, Benjamini–Hochberg) | Primary training and evaluation |
| Reliable negative | Eligible, `b ≤ c`, `f = 0`, both topics stayed active in the label window (at least `n_min` works), **and `E_f ≥ e_min`** | Primary training and evaluation, degree-matched |
| Ambiguous | Eligible, `b ≤ c`, and any of: `0 < f < k`; `f ≥ k` without significance; `f` within a margin below `k`; **or `f = 0` with `E_f < e_min`** | Excluded from primary training and evaluation; used only for sensitivity bounds (all-negative and all-positive) |

Rationale for the `E_f` condition: an observed zero is informative only if a co-occurrence was actually expected in the label window. A pair with `f = 0` and `E_f < e_min` is therefore never a reliable negative. It is **ambiguous** when it passes the eligibility rules above, and **ineligible** when it fails them (for example a topic below `n_min` in the label window). Classification order: ineligible, then already connected, then positive, then reliable negative, then ambiguous (everything remaining).

Starting placeholder: `n_min = 100`. `c`, `k`, `e_min`, the margin and `α` are calibrated on the early rolling origins only (cutoffs through 2019 with label windows ending ≤ 2022), reporting the resulting class counts and sensitivity at each setting, and then frozen. `e_min` is one shared threshold applied to both `E_b` (eligibility) and `E_f` (reliable negatives); if calibration shows they need different values, split them into `e_min_b` and `e_min_f` through a `CHANGELOG.md` entry before freezing. No label parameter may change after the 2023–2025 labels are first computed.
Negatives are matched to positives on log topic sizes (binned min and max) and on the number of distinct co-assigned partners. Report AUROC and PR-AUC on the matched sample and on the full eligible universe (ambiguous excluded).
Smoothed PMI: `PMI_α(A,B) = log[(b+α)/(E_b+α)]` with `α` a pseudo-count (start 0.5 or 1), negative values kept (deficit is informative). Compute the deficit feature only when `E_b ≥ e_min`, and give the model `E_b` as a separate support feature.
Features (visible at `T` only): Common Neighbours, Jaccard, Adamic–Adar, Resource Allocation, Preferential Attachment on the co-assignment graph; smoothed PMI; centroid cosine and citation-flow summaries where Tier B coverage exists. Models: each heuristic as a baseline, then logistic regression and gradient boosting.

## 6. Retrieval and ranking

Hybrid score for candidate `p` in merged set `C`:
`score(p) = (1−λ)·[α·ŝ_sem(p) + (1−α)·ŝ_lex(p)] + λ·ŝ_graph(p) + γ·ŝ_found(p)`
`ŝ` are per-query percentile ranks within `C`; missing scores are 0 and flagged. `s_sem` is query-adapter vs proximity-adapter cosine; `s_lex` is local BM25 over the expanded query; `s_graph` is personalized PageRank from the top-m semantic seeds on the query subgraph; `s_found` is an optional foundational prior from in-corpus in-degree over edges visible at the cutoff (default γ = 0). Tune α, λ, m, damping, hop depth on development queries by NDCG@10 with a small grid; report test-set results with bootstrap confidence intervals.

## 7. Evaluation **[FROZEN]**

| Task | Metrics |
|---|---|
| Emerging-topic ranking and classification | Recall@K, Precision@K, PR-AUC |
| Forecasting | MAE, RMSE on log share, Spearman, rolling origins |
| Retrieval (local-only, global keyword, global semantic, BM25, hybrid) | Recall@K, Precision@K, NDCG@K, MRR, **pool recall** (with pooling caveat) |
| Topic-pair prediction | AUROC, PR-AUC, hit@K vs baselines |
| Grounded synthesis | Citation correctness, claim support, unsupported-claim rate |
| Gap quality | Future-link hit rate, evidence coverage, verification pass rate, human plausibility, usefulness, novelty |

Search reporting (live queries) has three separate parts and **no** fetched-divided-by-matched percentage:
1. **API search accounting:** reported match counts per query string, records fetched, pages, duplicates, calls, cost, cache hits, stop reasons.
2. **Discovery-channel contribution:** candidates per channel, exclusive vs shared, share of top-K and evidence set.
3. **Measured retrieval recall:** only on the human-judged benchmark, offline.

Baselines: BM25, OpenAlex keyword and semantic search, vector-only, one generic sentence-embedding model; for trends, YoY growth, linear trend, ARIMA, ETS; for pairs, each heuristic and Preferential Attachment. Ablations: global discovery, query expansion, graph score, closure, delta index, verifier stages, compressed vs exact index, query adapter vs proximity.
≥ 3 seeds where training is involved, bootstrap 95% confidence intervals, field-wise reporting. Human evaluation fields: Computer Science, Medicine, Environmental Science, Social Sciences. Trends cover all fields.

## 8. Annotation
- Retrieval: queries per evaluation field with a domain reader; graded 0/1/2 on pooled top results from all systems; two annotators on a subset.
- Claim support: sample per field, two annotators, kappa.
- Contradictions: labelled pair set, two annotators.
- Gaps: at least 3 raters, rubric, blinded to system.
- Sample sizes decided after a Phase 0 effort estimate; guidelines in `docs/annotation/` before annotation starts.

## 9. API budget governance
Per-query governor (max calls, cost, wall time, per-channel allowance, priority order keyword → semantic → citation → topic). Daily governor with a spend ledger cross-checked against `/rate-limit`, plus a reserve for offline work. Hash-keyed request cache with time-to-live (live) and replay mode (evaluation). Client-side rate limiter (one request per second for semantic search) and per-user limits on the backend; exponential backoff. Fallback ladder, always disclosed in the search report: 0 normal; 1 fewer channels/pages, cache preferred; 2 cache plus local-only retrieval; 3 local-only with banner. Hosted-app budget (free allowance, prepaid, or hard cap) is an open decision.

## 10. Resource planning (estimates, hardware-agnostic)
Per million papers **[E]**: abstract text 0.5–1.2 GB compressed; cached API responses 2–15 GB; embeddings 3.1 GB fp32 / 1.5 GB fp16 (768 dimensions **[?]**); flat index about 3.1 GB RAM; IVF-PQ about 0.1 GB; citation graph about 0.4 GB per 100M in-corpus edges per direction; model weights about 0.2–0.5 GB **[?]**; embedding compute about 56 GFLOPs per 256-token abstract (2 × parameters × tokens), time = work ÷ **measured** sustained throughput. No machine assignments are made here; Phase 0 measures what is available.

## 9.1 Phase gates

| Gate | Evidence required |
|---|---|
| G0 | Protocol signed; repo and CI green; API pilot report; embedding benchmark report; build-manifest schema and leakage-audit skeleton |
| G1 | Tier A tables; Tier B stage 0–1 with manifests; MVP v0 end to end; leakage audit passing |
| G2 | SPECTER2 pipeline, main+delta index, CSR graph; recall vs exact index; first NDCG on judged queries |
| G3 | Trend thresholds calibrated on early origins and frozen |
| G4 | Forecasting vs baselines with intervals; final test run once |
| G5 | Hybrid parameters tuned; retrieval ablation table |
| G6 | Verification and synthesis metrics on annotated samples |
| G7 | Topic-pair labels frozen; future-link results vs baselines; evidence pipeline; expert review |
| G8 | Application, ablations, paper, reproducibility check from manifests |

## 11. Open decisions needing measurement or humans
1. Pilot results (grouping, sampling option, citation-filter direction, real cost per 1,000 records, duplicate rate, type vocabulary).
2. Hosted-app API budget; Groq model and budget.
3. Embedding dimension, SPECTER2 training chronology, English-only behaviour.
4. Throughput, fp16 effect, compression recall loss, latency.
5. Trend thresholds and label parameters `n_min`, `c`, `k`, `e_min`, margin, `α`.
6. Seed subfields and domain readers.
7. Annotation capacity.
8. Whether any optional experiment (GraphSAGE, fused GNN, temporal GNN, cross-encoder) is worth time.
