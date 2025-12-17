"""change english title

Revision ID: fc603d790f41
Revises: e54d1ec4eba6
Create Date: 2025-11-27 13:51:56.694951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc603d790f41'
down_revision: Union[str, Sequence[str], None] = 'e54d1ec4eba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # english_title уже nullable
    pass


def downgrade() -> None:
    pass
