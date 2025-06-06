"""Remove ingredient/product nutrition schema

Revision ID: afd5854d504f
Revises: 4952a0d12844
Create Date: 2025-04-24 13:20:51.039353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afd5854d504f'
down_revision = '4952a0d12844'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_nutrition')
    with op.batch_alter_table('ingredient_nutrition', schema=None) as batch_op:
        batch_op.drop_index('ix_ingredient_nutrition_ingredient_id')

    op.drop_table('ingredient_nutrition')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredient_nutrition',
    sa.Column('ingredient_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('carbohydrates', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('energy', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('fat', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('fibre', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('protein', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('carbohydrates_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('energy_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('fat_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('fibre_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('protein_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ingredient_id'], ['recipe_ingredients.id'], name='ingredient_nutrition_ingredient_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='ingredient_nutrition_pkey')
    )
    with op.batch_alter_table('ingredient_nutrition', schema=None) as batch_op:
        batch_op.create_index('ix_ingredient_nutrition_ingredient_id', ['ingredient_id'], unique=False)

    op.create_table('product_nutrition',
    sa.Column('carbohydrates', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('energy', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('fat', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('fibre', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('protein', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('product_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('carbohydrates_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('energy_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('fat_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('fibre_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('protein_units', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='product_nutrition_product_id_fkey', onupdate='CASCADE', ondelete='CASCADE', deferrable=True),
    sa.PrimaryKeyConstraint('product_id', name='product_nutrition_pkey')
    )
    # ### end Alembic commands ###
