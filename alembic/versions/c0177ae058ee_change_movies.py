"""change movies

Revision ID: c0177ae058ee
Revises: a90be6cadd4e
Create Date: 2025-12-11 13:00:40.683278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c0177ae058ee'
down_revision: Union[str, Sequence[str], None] = 'a90be6cadd4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # no-op: типы уже в конечном состоянии
    pass


def downgrade() -> None:
    pass
