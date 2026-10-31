# OPEN_QUESTIONS.md

This document tracks items that cannot be verified from documentation or tests, potential protocol conflicts, and decisions requiring team or mentor sign-off.

## Phase 0 Status

### T0.1 Repository Skeleton
- **Status:** Resolved / Verified.
- **Python version:** Python 3.13 selected and verified compatible with PyTorch 2.13.0, FAISS-CPU 1.15.1, DuckDB 2.0.0, Polars 2.1.0, Transformers 4.57.6, and Adapters 1.3.0.
- **Unresolved questions for T0.1:** None.

---

## Active Open Questions for Upcoming Tasks (from PROTOCOL.md Section 11)

1. **[?] T0.2 API Pilot Questions:**
   - Grouping support on `primary_topic.id`, `primary_topic.subfield.id`, `topics.id`, and `publication_year`.
   - Real cost per 1,000 records and observed rate-limit behaviour on `/rate-limit`.
   - Random sampling availability vs deterministic citation-agnostic sampling.
   - Exact filter semantics for `cites`, `cited_by`, and `referenced_works`.
   - Duplicate rate and frequency of citing/cited date anomalies.
2. **[?] T0.3 Embedding Benchmark:**
   - SPECTER2 embedding dimension verification (confirm 768) and chronology of training triplets.
   - Throughput (papers/sec) and peak memory across batch sizes and sequence lengths on local machine.
3. **[?] Project Decisions Requiring Sign-off:**
   - Hosted-app API budget (free allowance, prepaid, or hard cap).
   - Seed subfields and domain readers for evaluation.

