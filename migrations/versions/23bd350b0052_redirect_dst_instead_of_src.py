"""redirect-dst-instead-of-src

Revision ID: 23bd350b0052
Revises: 49bad27ec620
Create Date: 2023-08-29 11:34:40.433204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23bd350b0052'
down_revision = '49bad27ec620'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        schema='events',
        table_name='redirects',
        column_name='src',
        new_column_name='dst'
    )


def downgrade():
    op.alter_column(
        schema='events',
        table_name='redirects',
        column_name='dst',
        new_column_name='src'
    )
