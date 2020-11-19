"""Remove IngredientProduct model

Revision ID: 3b29701d26ca
Revises: 80af893c0415
Create Date: 2020-11-18 17:23:56.106701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b29701d26ca'
down_revision = '80af893c0415'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_ingredient_products_ingredient_id', table_name='ingredient_products')
    op.drop_index('ix_ingredient_products_product_id', table_name='ingredient_products')
    op.drop_table('ingredient_products')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient_products',
    sa.Column('ingredient_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('product_parser', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('is_plural', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['recipe_ingredients.id'], name='ingredient_products_ingredient_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='ingredient_products_product_id_fkey', deferrable=True),
    sa.PrimaryKeyConstraint('id', name='ingredient_products_pkey')
    )
    op.execute('''
        insert into ingredient_products (ingredient_id, id, product_id, product_parser, is_plural)
        select
            ri.id,
            ri.id,
            ri.product_id,
            ri.product_parser,
            ri.product_is_plural
        from recipe_ingredients as ri
    ''')
    op.create_index('ix_ingredient_products_product_id', 'ingredient_products', ['product_id'], unique=False)
    op.create_index('ix_ingredient_products_ingredient_id', 'ingredient_products', ['ingredient_id'], unique=False)
    # ### end Alembic commands ###
