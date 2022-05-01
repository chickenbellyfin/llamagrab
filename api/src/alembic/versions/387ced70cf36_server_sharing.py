"""empty message

Revision ID: 387ced70cf36
Revises: 82d772e83139
Create Date: 2022-04-22 12:37:41.230518

"""
from alembic import op
import sqlalchemy as sa

from src.database import models 


# revision identifiers, used by Alembic.
revision = '387ced70cf36'
down_revision = '82d772e83139'
branch_labels = None
depends_on = None


def upgrade():

    def default_updated_by(context):
        return context.current_parameters['user']

    # https://alembic.sqlalchemy.org/en/latest/batch.html
    # Create Server.updated_at column with default value of 1
    with op.batch_alter_table('servers') as batch_op:
        batch_op.add_column(sa.Column(
            'updated_by', 
            sa.Integer,  
            server_default='1',
            nullable=False
        ))
        batch_op.create_foreign_key('fk_servers_updated_by', 'users', ['updated_by'], ['id'])

    # Create ServerVersion.created_by column with default value of 1
    with op.batch_alter_table('server_versions') as batch_op:
        batch_op.add_column(sa.Column(
            'created_by', 
            sa.Integer,  
            server_default='1',
            nullable=False
        ))
        batch_op.create_foreign_key('fk_server_versions_created_by', 'users', ['created_by'], ['id'])

    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    
    # Set the updated_by for all servers to the owner
    for server in session.query(models.Server).all():
        server.updated_by = server.user
    
    # Set the created_by for all server versions for the owner
    for version in session.query(models.ServerVersion).all():
        #server = session.query(models.Server).filter(models.Server.id == version.id).first()
        version.created_by = version.server.updated_by
    
    session.commit()


def downgrade():
    pass
