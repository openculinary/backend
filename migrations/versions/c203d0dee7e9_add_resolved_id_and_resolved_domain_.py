"""Add resolved-id and resolved-domain crawl results

Revision ID: c203d0dee7e9
Revises: 11742ee5cedb
Create Date: 2025-01-28 16:17:33.743557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c203d0dee7e9'
down_revision = '11742ee5cedb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crawl_urls', schema=None) as batch_op:
        batch_op.add_column(sa.Column('resolved_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('resolved_domain', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_crawl_urls_resolved_id'), ['resolved_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crawl_urls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_crawl_urls_resolved_id'))
        batch_op.drop_column('resolved_domain')
        batch_op.drop_column('resolved_id')

    # ### end Alembic commands ###
