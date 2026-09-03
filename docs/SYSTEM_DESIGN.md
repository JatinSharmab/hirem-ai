# System Design
Boundaries: router → service → repository/provider. Deterministic functions remain pure where possible. External calls require timeouts and bounded concurrency. LLM model names are environment-driven. Content hashes key extraction/embedding caches. New ATS providers implement `JobSourceAdapter` instead of scattering source-specific parsing.
