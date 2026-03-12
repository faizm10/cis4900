from sqlalchemy import Integer, ForeignKey, Text, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "item"

    item_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # "multiple_choice" | "free_text"
    choices: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # [{"label": "A", "text": "..."}]
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    kc: Mapped["KC"] = relationship("KC", back_populates="items")
    attempts: Mapped[list["Attempt"]] = relationship("Attempt", back_populates="item")
