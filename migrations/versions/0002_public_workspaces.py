"""Anonymous workspace isolation, expiry and atomic usage budgets."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs", sa.Column("owner_id", sa.String(64), nullable=False, server_default="legacy-local")
    )
    op.add_column("jobs", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_jobs_owner_id", "jobs", ["owner_id"])
    op.create_index("ix_jobs_expires_at", "jobs", ["expires_at"])
    op.drop_constraint("uq_job_source_external", "jobs", type_="unique")
    op.create_unique_constraint(
        "uq_job_owner_source_external", "jobs", ["owner_id", "source", "external_job_id"]
    )
    op.create_table(
        "workspace_items",
        sa.Column("owner_id", sa.String(64), primary_key=True),
        sa.Column("kind", sa.String(32), primary_key=True),
        sa.Column("item_id", sa.String(64), primary_key=True),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspace_items_expires_at", "workspace_items", ["expires_at"])
    op.create_table(
        "usage_buckets",
        sa.Column("bucket", sa.String(160), primary_key=True),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_usage_buckets_expires_at", "usage_buckets", ["expires_at"])


def downgrade() -> None:
    # Reverting the tenant uniqueness constraint can fail if different visitors imported
    # the same job. Do not silently delete their data to make a downgrade succeed.
    op.drop_table("usage_buckets")
    op.drop_table("workspace_items")
    op.drop_constraint("uq_job_owner_source_external", "jobs", type_="unique")
    op.create_unique_constraint("uq_job_source_external", "jobs", ["source", "external_job_id"])
    op.drop_index("ix_jobs_owner_id", table_name="jobs")
    op.drop_index("ix_jobs_expires_at", table_name="jobs")
    op.drop_column("jobs", "expires_at")
    op.drop_column("jobs", "owner_id")
