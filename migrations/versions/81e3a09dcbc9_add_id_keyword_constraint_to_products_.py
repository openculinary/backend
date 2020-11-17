"""Add id keyword constraint to products table

Revision ID: 81e3a09dcbc9
Revises: bc84259ca6bc
Create Date: 2020-11-17 12:29:04.135392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81e3a09dcbc9'
down_revision = '8742627bf204'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint('ck_products_id_keyword', 'products', "id ~ '^[a-z_]+$'")


def downgrade():
    op.drop_constraint('ck_products_id_keyword', 'products', type_='check')
