"""Make URL hash-id required and indexed

Revision ID: 330fe0f5e304
Revises: 0ed6bcd27647
Create Date: 2023-12-12 18:41:13.134572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '330fe0f5e304'
down_revision = '0ed6bcd27647'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crawl_urls', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.create_index(batch_op.f('ix_crawl_urls_id'), ['id'], unique=False)

    with op.batch_alter_table('recipe_urls', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.create_index(batch_op.f('ix_recipe_urls_id'), ['id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipe_urls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_recipe_urls_id'))
        batch_op.alter_column('id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    with op.batch_alter_table('crawl_urls', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_crawl_urls_id'))
        batch_op.alter_column('id',
               existing_type=sa.VARCHAR(),
               nullable=True)

    # ### end Alembic commands ###
