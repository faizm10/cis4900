from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PrereqEdge(Base):
    __tablename__ = "prereq_edge"
    __table_args__ = (UniqueConstraint("from_kc_id", "to_kc_id", name="uq_prereq_edge"),)

    edge_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    from_kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False)
    to_kc_id: Mapped[int] = mapped_column(Integer, ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False)

    from_kc: Mapped["KC"] = relationship("KC", foreign_keys=[from_kc_id], back_populates="prereqs_as_source")
    to_kc: Mapped["KC"] = relationship("KC", foreign_keys=[to_kc_id], back_populates="prereqs_as_target")
