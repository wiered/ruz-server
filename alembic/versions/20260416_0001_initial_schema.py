"""Initial schema.

Revision ID: 20260416_0001
Revises:
Create Date: 2026-04-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260416_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("faculty_name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "lecturer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("short_name", sa.String(), nullable=False),
        sa.Column("rank", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "kind_of_work",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type_of_work", sa.String(), nullable=False),
        sa.Column("complexity", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "discipline",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("examtype", sa.String(), nullable=True),
        sa.Column("has_labs", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "auditorium",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("guid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("building", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lesson",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kind_of_work_id", sa.Integer(), nullable=False),
        sa.Column("discipline_id", sa.Integer(), nullable=False),
        sa.Column("auditorium_id", sa.Integer(), nullable=False),
        sa.Column("lecturer_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("begin_lesson", sa.Time(), nullable=False),
        sa.Column("end_lesson", sa.Time(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sub_group", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["auditorium_id"],
            ["auditorium.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["discipline_id"],
            ["discipline.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["kind_of_work_id"],
            ["kind_of_work.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lecturer_id"],
            ["lecturer.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("group_oid", sa.Integer(), nullable=True),
        sa.Column("subgroup", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_oid"],
            ["groups.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lesson_group",
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lesson.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("lesson_id", "group_id"),
    )


def downgrade() -> None:
    op.drop_table("lesson_group")
    op.drop_table("users")
    op.drop_table("lesson")
    op.drop_table("auditorium")
    op.drop_table("discipline")
    op.drop_table("kind_of_work")
    op.drop_table("lecturer")
    op.drop_table("groups")
