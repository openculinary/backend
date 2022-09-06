"""Remove product-id-is-keyword check constraint

Revision ID: 4cad42f6e760
Revises: ba4c68100f65
Create Date: 2022-09-06 16:36:04.066433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cad42f6e760'
down_revision = 'ba4c68100f65'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('ck_products_id_keyword', 'products', type_='check')


def downgrade():
    op.create_check_constraint('ck_products_id_keyword', 'products', "id ~ '^[a-z_]+$'")
