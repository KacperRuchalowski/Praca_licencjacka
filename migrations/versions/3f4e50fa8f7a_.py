"""empty message

Revision ID: 3f4e50fa8f7a
Revises: 7f837a2fb771
Create Date: 2021-03-31 18:49:05.179694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f4e50fa8f7a'
down_revision = '7f837a2fb771'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('article', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('article', 'location')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('location', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('article', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
