# Future production scaling

The current live path uses FastAPI services, PostgreSQL records, Gemini extraction/selection and deterministic scoring/verification. Graph/vector dependencies do not make it a production RAG or autonomous-agent system.

1. Measure latency, error rates, provider usage, database query time and hosted payload sizes. Avoid unmeasured scale or accuracy claims.
2. Add backend pagination for jobs/applications; the current job listing includes descriptions and can outgrow Vercel function response limits.
3. Add durable jobs and idempotency keys for long or retried operations. Browser cancellation does not guarantee provider cancellation.
4. Add account-based ownership and recovery when persistent personal use is required. Migrate anonymous records only through an explicit ownership process.
5. Move short-term limits/concurrency coordination to a shared service before running multiple API processes. Keep database-backed global usage ceilings.
6. Add observability without resume text or secret logging, provider circuit breakers, retries only for safe operations, and dead-letter handling for workers.
7. Add object storage with scoped uploads if files must exceed the 4 MiB frontend cap. Define retention, scanning and access controls before storing resumes.
8. Practice backup restoration and least-privilege database/secrets rotation. Consider managed pooling, autoscaling and regional placement based on measurements.
9. Build a larger labeled evaluation set before adding semantic retrieval or publishing accuracy metrics. Introduce a vector system only if evaluated retrieval needs justify it.
10. Consider paid always-on compute only when the user chooses that operating cost. The present portfolio migration remains on free hosting and adds no scheduled keep-alive.

These are future steps, not features claimed to be implemented or necessary purchases for the current portfolio. See [the migration trade-offs](NEXTJS_MIGRATION.md).
