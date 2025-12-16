"""add_oauth_support

Revision ID: 7c8685625500
Revises: c0177ae058ee
Create Date: 2025-12-17 00:11:51.573422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c8685625500'
down_revision: Union[str, Sequence[str], None] = 'c0177ae058ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
