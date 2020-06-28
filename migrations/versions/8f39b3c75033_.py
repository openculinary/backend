"""recipe_ingredients.quantity* -> recipe_ingredients.magnitude*

Revision ID: 8f39b3c75033
Revises: 
Create Date: 2020-06-28 16:09:49.000760

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8f39b3c75033'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('recipe_ingredients', 'quantity_parser', new_column_name='magnitude_parser')
    op.alter_column('recipe_ingredients', 'quantity', new_column_name='magnitude')


def downgrade():
    op.alter_column('recipe_ingredients', 'magnitude_parser', new_column_name='quantity_parser')
    op.alter_column('recipe_ingredients', 'magnitude', new_column_name='quantity')
