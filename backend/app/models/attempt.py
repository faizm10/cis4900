from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, Boolean, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Index

from app.database import Base


class Attempt(Base):
    __tablename__ = "attempt"
    __table_args__ = (
        Index("idx_attempt_learner_kc", "learner_id", "kc_id"),
        Index("idx_attempt_learner_ts", "learner_id", "timestamp"),
    )

    attempt_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    learner_id: Mapped[str] = mapped_column(String(100), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("item.item_id"), nullable=False)
    kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id"), nullable=False)
    correctness: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True, default=dict)

    item: Mapped["Item"] = relationship("Item", back_populates="attempts")
