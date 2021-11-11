"""weapon add min max dmg

Revision ID: 633158f62c66
Revises: d105a83c45b0
Create Date: 2021-11-07 23:22:43.892854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '633158f62c66'
down_revision = 'd105a83c45b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weapon', sa.Column('min_dmg', sa.Integer(), nullable=False))
    op.add_column('weapon', sa.Column('max_dmg', sa.Integer(), nullable=False))
    op.drop_column('weapon', 'damage')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('weapon', sa.Column('damage', sa.INTEGER(), nullable=False))
    op.drop_column('weapon', 'max_dmg')
    op.drop_column('weapon', 'min_dmg')
    # ### end Alembic commands ###
