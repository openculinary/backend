"""Add 'path' string field to search event query records

Revision ID: a061b3526863
Revises: 6b187bc74d7a
Create Date: 2021-06-12 15:36:01.029078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a061b3526863'
down_revision = '6b187bc74d7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('searches', sa.Column('path', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('searches', 'path')
    # ### end Alembic commands ###