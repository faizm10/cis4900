"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "kc",
        sa.Column("kc_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("p_l0", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("p_t", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("p_g", sa.Float(), nullable=False, server_default="0.25"),
        sa.Column("p_s", sa.Float(), nullable=False, server_default="0.1"),
        sa.Column("created_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    op.create_table(
        "prereq_edge",
        sa.Column("edge_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("from_kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("from_kc_id", "to_kc_id", name="uq_prereq_edge"),
    )

    op.create_table(
        "item",
        sa.Column("item_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id", ondelete="CASCADE"), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("choices", JSONB(), nullable=True),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.Float(), nullable=False, server_default="0.5"),
    )
    op.create_index("idx_item_kc", "item", ["kc_id"])

    op.create_table(
        "mastery",
        sa.Column("mastery_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("learner_id", sa.String(100), nullable=False),
        sa.Column("kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id"), nullable=False),
        sa.Column("p_mastery", sa.Float(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("learner_id", "kc_id", name="uq_mastery_learner_kc"),
    )
    op.create_index("idx_mastery_learner", "mastery", ["learner_id"])

    op.create_table(
        "route",
        sa.Column("route_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("learner_id", sa.String(100), nullable=False),
        sa.Column("goal_kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id"), nullable=False),
        sa.Column("ordered_kc_ids", JSONB(), nullable=False),
        sa.Column("next_kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id"), nullable=True),
        sa.Column("created_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_route_learner", "route", ["learner_id"])

    op.create_table(
        "attempt",
        sa.Column("attempt_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("learner_id", sa.String(100), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("item.item_id"), nullable=False),
        sa.Column("kc_id", sa.Integer(), sa.ForeignKey("kc.kc_id"), nullable=False),
        sa.Column("correctness", sa.Boolean(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("metadata", JSONB(), nullable=True, server_default=sa.text("'{}'")),
    )
    op.create_index("idx_attempt_learner_kc", "attempt", ["learner_id", "kc_id"])
    op.create_index("idx_attempt_learner_ts", "attempt", ["learner_id", "timestamp"])


def downgrade() -> None:
    op.drop_table("attempt")
    op.drop_table("route")
    op.drop_table("mastery")
    op.drop_table("item")
    op.drop_table("prereq_edge")
    op.drop_table("kc")
