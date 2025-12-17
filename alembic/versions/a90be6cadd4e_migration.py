"""migration

Revision ID: a90be6cadd4e
Revises: faa3c3c43d15
Create Date: 2025-12-11 10:21:52.943682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a90be6cadd4e'
down_revision: Union[str, Sequence[str], None] = 'faa3c3c43d15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # no-op: role уже есть, is_admin нет
    pass


def downgrade() -> None:
    pass
