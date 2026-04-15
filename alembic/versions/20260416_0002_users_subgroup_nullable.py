"""Make users.subgroup nullable.

Revision ID: 20260416_0002
Revises: 20260416_0001
Create Date: 2026-04-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260416_0002"
down_revision: str | Sequence[str] | None = "20260416_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Allow `users.subgroup` to be absent for older records."""

    op.alter_column(
        "users",
        "subgroup",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Restore the previous NOT NULL constraint."""

    op.alter_column(
        "users",
        "subgroup",
        existing_type=sa.Integer(),
        nullable=False,
    )
