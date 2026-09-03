from hireme_ai.api.routers import (
    applications,
    insights,
    jobs,
    matches,
    profile,
    resumes,
    runs,
    settings,
    workspace,
)

ALL_ROUTERS = [
    workspace.router,
    settings.router,
    profile.router,
    jobs.router,
    matches.router,
    resumes.router,
    applications.router,
    insights.router,
    runs.router,
]
