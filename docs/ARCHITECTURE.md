# Architecture
## WHAT
HireMe AI is a domain-specific Agentic Career Intelligence product: profile verification, job discovery/verification, deterministic + semantic matching, resume tailoring and application tracking.
## WHY
The workflow spans multiple trusted/untrusted inputs and consequential outputs, so explicit state, provenance and validation matter more than a single LLM call.
## HOW
Streamlit is presentation only. FastAPI exposes typed contracts. Services own business logic. Separate LangGraph workflows orchestrate semantic steps. PostgreSQL + pgvector stores relational and semantic data. External providers are behind interfaces.
## WHERE
User → Streamlit → FastAPI → services/workflows → repositories/providers.
## WHY THIS TECHNOLOGY
FastAPI/Pydantic provide typed boundaries; Streamlit keeps portfolio UI cost low; LangGraph makes state/routing/HITL inspectable; PostgreSQL + pgvector avoids a second persistence system.
## WHY NOT ALTERNATIVES
Flask is lighter but less typed; Django/DRF adds product/admin machinery not needed here. React/Next.js would be better for commercial UX but increases frontend scope. CrewAI/AutoGen emphasize agent abstraction over explicit workflow control. Qdrant is valid at larger vector scale but adds consistency/ops complexity for this MVP.
## FAILURE MODES
ATS contract changes, provider outages, malformed resumes, weak extraction, DB outage, embedding-model mismatch.
## SECURITY
PII, malicious uploads, prompt injection, SSRF, secret leakage and over-broad tool permissions are primary risks.
## TESTING
Unit deterministic components, mocked provider/adapter integration, workflow routes, malicious inputs, export parsing, and golden evaluation.
## SCALING
100K users requires auth, workers, Redis/distributed limiting, pooled DB access, queues/schedulers, object storage, observability stack, backups and HA.
## INTERVIEW EXPLANATION
“I separated deterministic invariants from LLM reasoning, used LangGraph only where state and HITL are useful, and made every resume claim traceable to verified candidate facts.”
