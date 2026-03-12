from datetime import datetime, timezone
from sqlalchemy import String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class KC(Base):
    __tablename__ = "kc"

    kc_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    p_l0: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    p_t: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    p_g: Mapped[float] = mapped_column(Float, default=0.25, nullable=False)
    p_s: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    created_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    items: Mapped[list["Item"]] = relationship("Item", back_populates="kc", cascade="all, delete-orphan")
    prereqs_as_source: Mapped[list["PrereqEdge"]] = relationship(
        "PrereqEdge", foreign_keys="PrereqEdge.from_kc_id", back_populates="from_kc", cascade="all, delete-orphan"
    )
    prereqs_as_target: Mapped[list["PrereqEdge"]] = relationship(
        "PrereqEdge", foreign_keys="PrereqEdge.to_kc_id", back_populates="to_kc", cascade="all, delete-orphan"
    )
