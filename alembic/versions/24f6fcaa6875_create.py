"""create

Revision ID: 24f6fcaa6875
Revises: 
Create Date: 2025-11-27 10:56:13.309212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24f6fcaa6875'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Initial schema creation."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('user', 'admin', name='userrole', native_enum=False), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'movies',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('kp_id', sa.Integer(), unique=True, index=True),
        sa.Column('title', sa.String(), nullable=False, index=True),
        sa.Column('english_title', sa.String(), nullable=True),
        sa.Column('kp_rating', sa.Float(), server_default='0'),
        sa.Column('imdb_rating', sa.Float(), server_default='0'),
        sa.Column('critics_rating', sa.Float(), server_default='0'),
        sa.Column('site_rating', sa.Float(), server_default='0'),
        sa.Column('fees_world', sa.String(), nullable=True),
        sa.Column('sum_votes', sa.Integer(), nullable=True),
        sa.Column('poster_url', sa.String(length=512), nullable=True),
        sa.Column('movie_length', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('world_premiere', sa.Date(), nullable=True),
        sa.Column('budget', sa.String(), nullable=True),
        sa.Column('year_release', sa.Integer(), nullable=True),
        sa.Column('age_rating', sa.Integer(), nullable=True),
        sa.Column('genres', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('countries', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('persons', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('director', sa.String(), nullable=True),
    )

    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('movie_id', sa.Integer(), sa.ForeignKey('movies.id')),
    )

    op.create_table(
        'movie_lists',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id')),
    )

    op.create_table(
        'list_movie_association',
        sa.Column('list_id', sa.Integer(), sa.ForeignKey('movie_lists.id'), primary_key=True),
        sa.Column('movie_id', sa.Integer(), sa.ForeignKey('movies.id'), primary_key=True),
    )

    op.create_table(
        'movie_similarities',
        sa.Column('movie_id', sa.Integer(), sa.ForeignKey('movies.id'), primary_key=True),
        sa.Column('similar_movie_id', sa.Integer(), sa.ForeignKey('movies.id'), primary_key=True),
    )

    # analytics/logs tables
    op.create_table(
        'search_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('query', sa.String(length=255), nullable=False, index=True),
        sa.Column('has_results', sa.Boolean(), nullable=False, index=True, server_default=sa.text('false')),
        sa.Column('results_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )

    op.create_table(
        'page_view_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('path', sa.String(length=512), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )

    op.create_table(
        'movie_view_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('movie_id', sa.Integer(), sa.ForeignKey('movies.id'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )

    op.create_table(
        'error_logs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('level', sa.String(length=32), nullable=False, index=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table('error_logs')
    op.drop_table('movie_view_logs')
    op.drop_table('page_view_logs')
    op.drop_table('search_logs')
    op.drop_table('movie_similarities')
    op.drop_table('list_movie_association')
    op.drop_table('movie_lists')
    op.drop_table('reviews')
    op.drop_table('movies')
    op.drop_table('users')
