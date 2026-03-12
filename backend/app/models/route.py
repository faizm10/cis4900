from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index

from app.database import Base


class Route(Base):
    __tablename__ = "route"
    __table_args__ = (Index("idx_route_learner", "learner_id"),)

    route_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    learner_id: Mapped[str] = mapped_column(String(100), nullable=False)
    goal_kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id"), nullable=False)
    ordered_kc_ids: Mapped[list] = mapped_column(JSONB, nullable=False)  # [kc_id, ...]
    next_kc_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("kc.kc_id"), nullable=True)
    created_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
