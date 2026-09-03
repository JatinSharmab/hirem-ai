# Data Model
Relational chain: candidate_profiles → candidate_facts; jobs → snapshots/requirements/skills; candidate_job_matches → match_evidence; resume_versions link candidate/job/facts; applications link job/resume; agent_runs → events/tool_calls. UUID identifiers, indexes and idempotency constraints are used where meaningful. pgvector columns store vectors plus model metadata.
