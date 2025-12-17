"""add is_admin

Revision ID: faa3c3c43d15
Revises: b0dd98587a98
Create Date: 2025-12-08 20:10:59.177669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'faa3c3c43d15'
down_revision: Union[str, Sequence[str], None] = 'b0dd98587a98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # no-op: role column уже в схеме
    pass


def downgrade() -> None:
    pass
