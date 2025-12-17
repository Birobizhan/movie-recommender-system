"""add created

Revision ID: b0dd98587a98
Revises: 9064c5aeed15
Create Date: 2025-12-08 11:29:23.067780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0dd98587a98'
down_revision: Union[str, Sequence[str], None] = '9064c5aeed15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # no-op: timestamps уже есть в начальной схеме
    pass


def downgrade() -> None:
    pass
