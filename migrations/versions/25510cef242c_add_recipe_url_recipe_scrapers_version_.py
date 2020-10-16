"""Add recipe_url.recipe_scrapers_version column

Revision ID: 25510cef242c
Revises: 8763d112afd0
Create Date: 2020-07-10 13:47:24.507652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25510cef242c'
down_revision = '8763d112afd0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe_urls', sa.Column('recipe_scrapers_version', sa.String(), nullable=True))
    op.create_index(op.f('ix_recipe_urls_recipe_scrapers_version'), 'recipe_urls', ['recipe_scrapers_version'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_recipe_urls_recipe_scrapers_version'), table_name='recipe_urls')
    op.drop_column('recipe_urls', 'recipe_scrapers_version')
    # ### end Alembic commands ###
