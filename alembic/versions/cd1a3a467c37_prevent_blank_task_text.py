"""prevent blank task text

Revision ID: cd1a3a467c37
Revises: a4d5fc93ce7c
Create Date: 2026-07-18 14:20:34.154351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd1a3a467c37'
down_revision: Union[str, Sequence[str], None] = 'a4d5fc93ce7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_tasks_text_not_blank",
        "tasks",
        "length(trim(text)) > 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_tasks_text_not_blank",
        "tasks",
        type_="check",
    )
