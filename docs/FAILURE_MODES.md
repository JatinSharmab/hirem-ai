# Failure Modes
|Failure|Detection|Impact|Fallback|Retry?|User behavior|Signal|
|---|---|---|---|---|---|---|
|LLM unavailable|provider exception|semantic step blocked|Demo/deterministic path|bounded transient|show degraded mode|error_type|
|Rate limit|HTTP 429|delayed AI|backoff+jitter|yes|retry message|429 count|
|ATS schema change|validation failure|source partial|mark source unhealthy|limited|show UNKNOWN|adapter failures|
|ATS unavailable|timeout/5xx|no fresh jobs|cached/demo data|yes|source warning|latency/5xx|
|Malformed resume|parser error|profile blocked|ask valid PDF/DOCX|no|clear validation|INVALID_RESUME|
|JD prompt injection|pattern/schema warning|unsafe model influence|data-only handling|no|developer warning|injection count|
|Duplicate jobs|fingerprint collision|bad UX|deterministic dedupe|n/a|single result|dedupe ratio|
|Unknown job date|missing field|freshness uncertain|preserve null|no|show unknown|missing-date rate|
|Embedding unavailable|provider error|semantic score absent|exact matching only|yes transient|degraded score|embedding errors|
|DB unavailable|readiness failure|persistence blocked|Demo fixtures where safe|yes infra|degraded status|ready failure|
|Critic disagrees|validator/critic mismatch|review needed|deterministic validator wins|no|show warning|disagreement count|
|PDF rendering fails|exception|export blocked|DOCX available|limited|export error|renderer errors|
