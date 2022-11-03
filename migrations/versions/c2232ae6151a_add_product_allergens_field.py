"""Add product.allergens field

Revision ID: c2232ae6151a
Revises: 1282ece687fa
Create Date: 2022-11-03 13:05:32.859420

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c2232ae6151a'
down_revision = '1282ece687fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('allergens', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'allergens')
    # ### end Alembic commands ###
