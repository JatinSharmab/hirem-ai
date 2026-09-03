from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from hireme_ai.db.base import Base, UUIDTimestampMixin


class CandidateProfileModel(UUIDTimestampMixin, Base):
    __tablename__ = "candidate_profiles"
    name: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(Text, default="")


class CandidatePreferenceModel(UUIDTimestampMixin, Base):
    __tablename__ = "candidate_preferences"
    candidate_profile_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    target_roles: Mapped[str] = mapped_column(Text, default="")
    locations: Mapped[str] = mapped_column(Text, default="")
    remote_preference: Mapped[str] = mapped_column(String(50), default="any")


class CandidateFactModel(UUIDTimestampMixin, Base):
    __tablename__ = "candidate_facts"
    candidate_profile_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    fact_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(200))
    predicate: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(Text)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verified_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    immutable: Mapped[bool] = mapped_column(Boolean, default=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100), nullable=True)


class JobModel(UUIDTimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint(
            "owner_id", "source", "external_job_id", name="uq_job_owner_source_external"
        ),
    )
    owner_id: Mapped[str] = mapped_column(String(64), server_default="legacy-local", index=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    source: Mapped[str] = mapped_column(String(80), index=True)
    external_job_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    company: Mapped[str] = mapped_column(String(300), index=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True, index=True)
    canonical_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text)
    description_hash: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String(100), nullable=True)


class JobSnapshotModel(UUIDTimestampMixin, Base):
    __tablename__ = "job_snapshots"
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30))
    verification_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)


class JobRequirementModel(UUIDTimestampMixin, Base):
    __tablename__ = "job_requirements"
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    role_family: Mapped[str | None] = mapped_column(String(200), nullable=True)
    minimum_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    maximum_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)


class JobSkillModel(UUIDTimestampMixin, Base):
    __tablename__ = "job_skills"
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    normalized_name: Mapped[str] = mapped_column(String(120), index=True)
    original_text: Mapped[str] = mapped_column(String(200))
    requirement_type: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float, default=1.0)


class CandidateJobMatchModel(UUIDTimestampMixin, Base):
    __tablename__ = "candidate_job_matches"
    candidate_profile_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    score: Mapped[float] = mapped_column(Float)
    eligible: Mapped[bool] = mapped_column(Boolean)
    breakdown_json: Mapped[str] = mapped_column(Text)


class MatchEvidenceModel(UUIDTimestampMixin, Base):
    __tablename__ = "match_evidence"
    match_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_job_matches.id", ondelete="CASCADE"), index=True
    )
    requirement: Mapped[str] = mapped_column(Text)
    fact_ids: Mapped[str] = mapped_column(Text, default="")
    alignment: Mapped[str] = mapped_column(String(30))
    confidence: Mapped[float] = mapped_column(Float)


class ResumeVersionModel(UUIDTimestampMixin, Base):
    __tablename__ = "resume_versions"
    candidate_profile_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"), index=True
    )
    target_job_id: Mapped[str | None] = mapped_column(
        ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    verification_status: Mapped[str] = mapped_column(String(30), index=True)
    source_fact_ids: Mapped[str] = mapped_column(Text, default="")
    content_json: Mapped[str] = mapped_column(Text)
    preferred: Mapped[bool] = mapped_column(Boolean, default=False)


class ApplicationModel(UUIDTimestampMixin, Base):
    __tablename__ = "applications"
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    resume_version_id: Mapped[str | None] = mapped_column(
        ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )


class AgentRunModel(UUIDTimestampMixin, Base):
    __tablename__ = "agent_runs"
    workflow: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(30))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    embedding_operations: Mapped[int] = mapped_column(Integer, default=0)
    http_calls: Mapped[int] = mapped_column(Integer, default=0)


class AgentEventModel(UUIDTimestampMixin, Base):
    __tablename__ = "agent_events"
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True)
    node: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30))
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")


class ToolCallModel(UUIDTimestampMixin, Base):
    __tablename__ = "tool_calls"
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id", ondelete="CASCADE"), index=True)
    tool_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
