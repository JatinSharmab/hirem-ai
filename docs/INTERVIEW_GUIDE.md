# Interview Guide
**What problem does HireMe AI solve?** It turns job search and resume tailoring into an evidence-grounded workflow instead of an opaque keyword or freeform LLM process.

**Why Agentic AI?** Only multi-step semantic tasks need orchestration: search planning, extraction, explanation and tailoring. Validation/scoring/persistence stay deterministic.

**Why LangGraph?** Explicit typed state, conditional routing, retries/checkpointing and HITL are easier to inspect than autonomous-agent abstractions.

**Why not CrewAI/AutoGen?** They can work, but this project values controlled workflow topology and deterministic boundaries more than agent-persona collaboration.

**Why FastAPI?** Strong typed contracts, Pydantic integration, OpenAPI and async HTTP support.

**Why Streamlit?** The project is AI/backend focused. Commercial SaaS would likely move to Next.js for richer UX and auth.

**Why PostgreSQL + pgvector?** Career data is relational and semantic. One system reduces consistency complexity. Qdrant becomes attractive when vector scale/latency benchmarks justify it.

**Why different from Elyqorix?** Elyqorix demonstrates general agent/reasoning infrastructure and may use a dedicated vector store; HireMe AI intentionally demonstrates a domain workflow and unified relational/vector persistence tradeoff.

**How is Career Fit Score calculated?** Deterministically from configurable weighted components after hard eligibility. The LLM explains but never invents the score.

**Why not “ATS Score”?** It is not calibrated against a commercial applicant tracking system; calling it that would be misleading.

**How do you prevent resume hallucinations?** Candidate Fact Ledger + per-bullet provenance + deterministic numeric/factual verification + semantic critic as second pass.

**Why deterministic verification before critic?** Numbers, dates and source IDs are hard invariants; a second LLM should never overrule them.

**Prompt injection defense?** JD is untrusted data, schema-constrained output, no tool instructions from JD, suspicious-pattern warnings and allowlisted tools.

**SSRF defense?** Only HTTP(S), block localhost/private/link-local/reserved/metadata endpoints, and validate redirects/resolution in hardened live deployments.

**Job verification?** Re-fetch authoritative ATS/job URL; 404/410 closes it, success can mark open, ambiguous responses remain UNKNOWN.

**Deduplication?** Canonical URL/external ID first, then normalized company/title/location + description hash. LLM is unnecessary for obvious duplicates.

**Evaluation?** Golden synthetic candidates/jobs, deterministic expected gaps/evidence, mocked providers, security tests and zero unsupported claims invariant.

**1M jobs / 100K users?** Workers/schedulers, queues, partitioned ingestion, distributed cache/rate limits, stronger vector indexing, DB pooling/replicas, auth and observability.

**Biggest limitations?** Portfolio UI, no auth, evolving ATS contracts, hand-calibrated scoring weights and free-host constraints.
