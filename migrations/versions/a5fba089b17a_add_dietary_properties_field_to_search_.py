"""Add dietary_properties field to search event model

Revision ID: a5fba089b17a
Revises: 58641e07557c
Create Date: 2022-08-18 11:50:08.986579

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a5fba089b17a'
down_revision = '58641e07557c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('searches', sa.Column('dietary_properties', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('searches', 'dietary_properties')
    # ### end Alembic commands ###
