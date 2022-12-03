"""empty message

Revision ID: be25215dba87
Revises: 2e6559a572a8
Create Date: 2022-06-12 00:39:47.117269

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'be25215dba87'
down_revision = '2e6559a572a8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('servers', sa.Column('game', sa.String, default='tribes_ascend_ootb', server_default='tribes_ascend_ootb', nullable=False))

def downgrade():
    pass
