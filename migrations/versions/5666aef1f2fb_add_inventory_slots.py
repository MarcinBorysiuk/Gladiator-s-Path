"""add inventory slots

Revision ID: 5666aef1f2fb
Revises: 0abfdd4472b9
Create Date: 2021-11-05 20:39:53.486310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5666aef1f2fb'
down_revision = '0abfdd4472b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('inventory_slots', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'inventory_slots')
    # ### end Alembic commands ###