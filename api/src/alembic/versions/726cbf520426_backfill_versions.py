"""empty message

Revision ID: 726cbf520426
Revises: 387ced70cf36
Create Date: 2022-04-22 14:17:03.485527

"""
import time

from alembic import op
import sqlalchemy as sa

from src.database import models 


# revision identifiers, used by Alembic.
revision = '726cbf520426'
down_revision = '387ced70cf36'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    now = int(time.time())
    
    # add a version for all servers which dont have one
    for server in session.query(models.Server).all():
        versions = session.query(models.ServerVersion).filter(models.ServerVersion.server_id == server.id).all()
        if len(versions) == 0:
            new_version = models.ServerVersion(
                server_id=server.id,
                server_config=server.server_config,
                num_changes=-1,
                created_at=now,
                created_by=server.updated_by
            )
            session.add(new_version)

    session.commit()


def downgrade():
    pass
