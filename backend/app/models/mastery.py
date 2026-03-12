from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, Float, String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index

from app.database import Base


class Mastery(Base):
    __tablename__ = "mastery"
    __table_args__ = (
        UniqueConstraint("learner_id", "kc_id", name="uq_mastery_learner_kc"),
        Index("idx_mastery_learner", "learner_id"),
    )

    mastery_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    learner_id: Mapped[str] = mapped_column(String(100), nullable=False)
    kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id"), nullable=False)
    p_mastery: Mapped[float] = mapped_column(Float, nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
