from sqlalchemy.pool import StaticPool

from api.app import ensure_admin_user
from api.database import models, queries
from api.database.database import Database


def test_initialize_db():
    # sqlite will be inmemory if path is empty
  database = Database('', '', poolclass=StaticPool)

  with database.session() as session:
    assert len(session.query(models.Server).all()) == 0
    assert len(session.query(models.User).all()) == 0
    assert len(session.query(models.UserLimits).all()) == 0

  ensure_admin_user(database)

  with database.session() as session:
    assert queries.get_user(session, 'admin') is not None
    assert queries.get_user(session, 'admin').limits is not None
    assert len(queries.get_servers(session, queries.get_user(session, 'admin'))) > 0
    ran = True
