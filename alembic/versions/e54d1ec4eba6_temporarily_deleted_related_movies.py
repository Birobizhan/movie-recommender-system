"""temporarily deleted related movies

Revision ID: e54d1ec4eba6
Revises: 24f6fcaa6875
Create Date: 2025-11-27 11:04:55.189950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e54d1ec4eba6'
down_revision: Union[str, Sequence[str], None] = '24f6fcaa6875'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
