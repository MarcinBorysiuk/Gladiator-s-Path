"""merge two heads

Revision ID: 027b42591253
Revises: 633158f62c66, 67e2cb81422e
Create Date: 2021-11-08 20:27:55.349897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '027b42591253'
down_revision = ('633158f62c66', '67e2cb81422e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
