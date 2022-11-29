"""Add a flag to enable/disable web crawling on a per-domain basis

Revision ID: 49bad27ec620
Revises: 65710cf38339
Create Date: 2022-11-21 21:06:40.991201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49bad27ec620'
down_revision = '65710cf38339'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('domains', sa.Column('crawl_enabled', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('domains', 'crawl_enabled')
    # ### end Alembic commands ###
