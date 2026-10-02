# Security

## Next.js boundary (October 3, 2026)

The new frontend talks only to same-origin BFF endpoints. Server-only modules attach
the private gateway key and an owner UUID verified from an HMAC-signed, HTTP-only
workspace cookie. Exact-origin and Fetch Metadata checks protect writes. Known
method/path operations, streamed-body limits, upstream redirect rejection and
normalized errors constrain the proxy. No Gemini or database credential enters
browser code. API responses are private/no-store; resume state uses tab memory.

Existing Python owner filters, database-backed daily quotas, parser checks,
provider limits, export reverification and verified database TLS remain in force.
Anonymous cookies are not accounts or strong anti-abuse identity. Clearing data
preserves usage counters. A 4 MiB frontend upload cap accommodates Vercel's payload
limit; Python retains 5 MiB. Headers include framing protection and a partial CSP,
not a full nonce-based script policy. See [the full boundary and limitations](NEXTJS_MIGRATION.md).

The following is the repository's broader threat model; individual scaffolding
controls should not be described as active in every live route without code evidence.

Threats: PII leakage, secret exposure, prompt injection, SSRF, malformed uploads, unsafe redirects, SQL injection, abusive rate, dependency compromise and tool misuse. Controls include typed schemas, SQLAlchemy parameterization, upload signature/size validation, untrusted-data prompt boundaries, suspicious-instruction detection, public HTTP(S)-only URL policy, blocklists for local/private/link-local/metadata targets, bounded timeouts, tool allowlists, in-process demo throttling and HITL for consequential external actions. No compliance certification is claimed.
