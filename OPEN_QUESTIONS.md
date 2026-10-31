# OPEN_QUESTIONS.md

This document tracks items that cannot be verified from documentation or tests, potential protocol conflicts, and decisions requiring team or mentor sign-off.

## Phase 0 Status

### T0.1 Repository Skeleton
- **Status:** Resolved / Verified.
- **Python version:** Python 3.13 pinned as baseline. Dry-run dependency resolution and isolated wheel imports verified for planned packages.
- **T0.3 Planning Note:** Full end-to-end runtime compatibility of the combined `torch` + `transformers` + `adapters` + `faiss-cpu` stack remains to be empirically verified during the T0.3 installation and benchmark.
- **PyTorch Installation Strategy:** Proposal to keep platform-specific PyTorch builds outside the cross-platform lockfile (using environment-specific requirement files) is pending team approval.

---

## Active Open Questions for Upcoming Tasks (from docs/PROTOCOL.md Section 11)

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
