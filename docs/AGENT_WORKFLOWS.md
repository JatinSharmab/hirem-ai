# Agent Workflows
Four workflows: Candidate Profile, Job Discovery, Resume Tailoring and Application Tracking. They remain separate to reduce state coupling and make retries/failures inspectable. Graph state stores structured raw data, not formatted prompts. The application workflow ends at a human approval/open-official-URL boundary; it never mass-applies.
