"""empty message

Revision ID: 7af856fb8978
Revises: be25215dba87
Create Date: 2022-06-24 14:07:00.573493

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '7af856fb8978'
down_revision = 'be25215dba87'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('servers') as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('game_mode')


def downgrade():
    pass
