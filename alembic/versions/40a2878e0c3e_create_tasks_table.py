"""create tasks table

Revision ID: 40a2878e0c3e
Revises: 
Create Date: 2026-07-17 14:36:46.001697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40a2878e0c3e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tasks")
