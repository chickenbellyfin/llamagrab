"""empty message

Revision ID: 2e6559a572a8
Revises: 726cbf520426
Create Date: 2022-05-18 18:19:43.199692

"""
import sqlalchemy as sa
from alembic import op

from api.database import models

# revision identifiers, used by Alembic.
revision = '2e6559a572a8'
down_revision = '726cbf520426'
branch_labels = None
depends_on = None


def upgrade():
  op.add_column('servers', sa.Column('enabled', sa.Boolean, default=False, server_default='0', nullable=False))

  bind = op.get_bind()
  session = sa.orm.Session(bind=bind)
  for server in session.query(models.Server):
    server.enabled = (server.status == 'running')
    print(server.status, server.enabled)
  session.commit()

def downgrade():
  pass
