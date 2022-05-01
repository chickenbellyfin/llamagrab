"""empty message

Revision ID: 82d772e83139
Revises: 
Create Date: 2022-04-20 23:44:45.302270

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82d772e83139'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('servers', sa.Column('updated_at', sa.Integer))


def downgrade():
    pass
