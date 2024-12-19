"""Domains: add `cache_enabled` boolean flag

Revision ID: 8255e4e6e956
Revises: 506f652b919e
Create Date: 2024-12-19 16:13:34.383537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8255e4e6e956'
down_revision = '506f652b919e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('domains', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cache_enabled', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('domains', schema=None) as batch_op:
        batch_op.drop_column('cache_enabled')

    # ### end Alembic commands ###
