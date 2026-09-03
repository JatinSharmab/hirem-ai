from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hireme_ai.db.base import Base


class WorkspaceItem(Base):
    __tablename__ = "workspace_items"
    owner_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content_json: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class UsageBucket(Base):
    __tablename__ = "usage_buckets"
    bucket: Mapped[str] = mapped_column(String(160), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
