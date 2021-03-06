"""Add 'kitchen staple' product property

Revision ID: c696855f1023
Revises: 06e4193e416f
Create Date: 2020-11-10 18:27:54.939253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c696855f1023'
down_revision = '06e4193e416f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingredient_products', sa.Column('is_kitchen_staple', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ingredient_products', 'is_kitchen_staple')
    # ### end Alembic commands ###
