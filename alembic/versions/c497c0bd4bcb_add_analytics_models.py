"""add analytics models

Revision ID: c497c0bd4bcb
Revises: 7c8685625500
Create Date: 2025-12-17 11:42:16.467257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c497c0bd4bcb'
down_revision: Union[str, Sequence[str], None] = '7c8685625500'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
