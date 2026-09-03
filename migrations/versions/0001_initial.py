"""initial HireMe AI schema

Revision ID: 0001
Revises:
Create Date: 2026-10-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _common() -> list[sa.Column]:
    return [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "candidate_profiles",
        *_common(),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
    )
    op.create_table(
        "candidate_preferences",
        *_common(),
        sa.Column(
            "candidate_profile_id",
            sa.String(36),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_roles", sa.Text(), nullable=False),
        sa.Column("locations", sa.Text(), nullable=False),
        sa.Column("remote_preference", sa.String(50), nullable=False),
    )
    op.create_index(
        "ix_candidate_preferences_candidate_profile_id",
        "candidate_preferences",
        ["candidate_profile_id"],
    )
    op.create_table(
        "candidate_facts",
        *_common(),
        sa.Column(
            "candidate_profile_id",
            sa.String(36),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("fact_id", sa.String(64), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("predicate", sa.String(200), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("source_text", sa.Text()),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("verified_by_user", sa.Boolean(), nullable=False),
        sa.Column("immutable", sa.Boolean(), nullable=False),
        sa.Column("embedding", Vector(768)),
        sa.Column("embedding_model", sa.String(100)),
    )
    op.create_index(
        "ix_candidate_facts_candidate_profile_id", "candidate_facts", ["candidate_profile_id"]
    )
    op.create_index("ix_candidate_facts_fact_id", "candidate_facts", ["fact_id"], unique=True)
    op.create_table(
        "jobs",
        *_common(),
        sa.Column("source", sa.String(80), nullable=False),
        sa.Column("external_job_id", sa.String(200)),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("company", sa.String(300), nullable=False),
        sa.Column("location", sa.String(300)),
        sa.Column("canonical_url", sa.Text()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("description_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("embedding", Vector(768)),
        sa.Column("embedding_model", sa.String(100)),
        sa.UniqueConstraint("source", "external_job_id", name="uq_job_source_external"),
    )
    for col in ["source", "title", "company", "location", "description_hash", "status"]:
        op.create_index(f"ix_jobs_{col}", "jobs", [col])
    op.create_table(
        "job_snapshots",
        *_common(),
        sa.Column(
            "job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("verification_evidence", sa.Text()),
    )
    op.create_index("ix_job_snapshots_job_id", "job_snapshots", ["job_id"])
    op.create_table(
        "job_requirements",
        *_common(),
        sa.Column(
            "job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("role_family", sa.String(200)),
        sa.Column("minimum_experience", sa.Float()),
        sa.Column("maximum_experience", sa.Float()),
        sa.Column("raw_json", sa.Text(), nullable=False),
    )
    op.create_index("ix_job_requirements_job_id", "job_requirements", ["job_id"])
    op.create_table(
        "job_skills",
        *_common(),
        sa.Column(
            "job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("normalized_name", sa.String(120), nullable=False),
        sa.Column("original_text", sa.String(200), nullable=False),
        sa.Column("requirement_type", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
    )
    op.create_index("ix_job_skills_job_id", "job_skills", ["job_id"])
    op.create_index("ix_job_skills_normalized_name", "job_skills", ["normalized_name"])
    op.create_table(
        "candidate_job_matches",
        *_common(),
        sa.Column(
            "candidate_profile_id",
            sa.String(36),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("breakdown_json", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_candidate_job_matches_candidate_profile_id",
        "candidate_job_matches",
        ["candidate_profile_id"],
    )
    op.create_index("ix_candidate_job_matches_job_id", "candidate_job_matches", ["job_id"])
    op.create_table(
        "match_evidence",
        *_common(),
        sa.Column(
            "match_id",
            sa.String(36),
            sa.ForeignKey("candidate_job_matches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("requirement", sa.Text(), nullable=False),
        sa.Column("fact_ids", sa.Text(), nullable=False),
        sa.Column("alignment", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
    )
    op.create_index("ix_match_evidence_match_id", "match_evidence", ["match_id"])
    op.create_table(
        "resume_versions",
        *_common(),
        sa.Column(
            "candidate_profile_id",
            sa.String(36),
            sa.ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="SET NULL")),
        sa.Column("verification_status", sa.String(30), nullable=False),
        sa.Column("source_fact_ids", sa.Text(), nullable=False),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("preferred", sa.Boolean(), nullable=False),
    )
    op.create_index(
        "ix_resume_versions_candidate_profile_id", "resume_versions", ["candidate_profile_id"]
    )
    op.create_index(
        "ix_resume_versions_verification_status", "resume_versions", ["verification_status"]
    )
    op.create_table(
        "applications",
        *_common(),
        sa.Column(
            "job_id", sa.String(36), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column(
            "resume_version_id",
            sa.String(36),
            sa.ForeignKey("resume_versions.id", ondelete="SET NULL"),
        ),
    )
    op.create_index("ix_applications_job_id", "applications", ["job_id"])
    op.create_index("ix_applications_status", "applications", ["status"])
    op.create_table(
        "agent_runs",
        *_common(),
        sa.Column("workflow", sa.String(100), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("embedding_operations", sa.Integer(), nullable=False),
        sa.Column("http_calls", sa.Integer(), nullable=False),
    )
    op.create_index("ix_agent_runs_workflow", "agent_runs", ["workflow"])
    op.create_table(
        "agent_events",
        *_common(),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("agent_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("node", sa.String(100), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False),
    )
    op.create_index("ix_agent_events_run_id", "agent_events", ["run_id"])
    op.create_table(
        "tool_calls",
        *_common(),
        sa.Column(
            "run_id",
            sa.String(36),
            sa.ForeignKey("agent_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tool_name", sa.String(120), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
    )
    op.create_index("ix_tool_calls_run_id", "tool_calls", ["run_id"])


def downgrade() -> None:
    for table in [
        "tool_calls",
        "agent_events",
        "agent_runs",
        "applications",
        "resume_versions",
        "match_evidence",
        "candidate_job_matches",
        "job_skills",
        "job_requirements",
        "job_snapshots",
        "jobs",
        "candidate_facts",
        "candidate_preferences",
        "candidate_profiles",
    ]:
        op.drop_table(table)
