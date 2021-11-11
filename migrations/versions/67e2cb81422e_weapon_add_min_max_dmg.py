"""weapon add min max dmg

Revision ID: 67e2cb81422e
Revises: d105a83c45b0
Create Date: 2021-11-07 23:24:10.318816

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67e2cb81422e'
down_revision = 'd105a83c45b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weapon', sa.Column('min_dmg', sa.Integer(), nullable=True))
    op.add_column('weapon', sa.Column('max_dmg', sa.Integer(), nullable=True))
    op.drop_column('weapon', 'damage')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weapon', sa.Column('damage', sa.INTEGER(), nullable=False))
    op.drop_column('weapon', 'max_dmg')
    op.drop_column('weapon', 'min_dmg')
    # ### end Alembic commands ###
