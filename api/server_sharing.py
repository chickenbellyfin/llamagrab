from typing import List

from loguru import logger
from sqlalchemy.orm.session import Session

from api.database import models
from api.database import queries as db_queries


def get_shared_servers(db: Session, user: models.User) -> List[models.Server]:
  server_editors = db.query(models.ServerEditor).filter(models.ServerEditor.user_id == user.id).all()
  return [s.server for s in server_editors]

def get_server_editors(db: Session, server: models.Server) -> List[models.User]:
  server_editors = db.query(models.ServerEditor).filter(models.ServerEditor.server_id == server.id).all()
  return [s.user for s in server_editors]

def is_editor(db: Session, user: models.User, server: models.Server) -> bool:
  editor = (db
    .query(models.ServerEditor)
    .filter(models.ServerEditor.server_id == server.id)
    .filter(models.ServerEditor.user_id == user.id)
    .first()
  )
  return editor is not None

def set_server_editors(db: Session, server: models.Server, user_ids: List[int]):
  db.query(models.ServerEditor).filter(models.ServerEditor.server_id == server.id).delete()
  # validate that editors is a list of valid user ids
  for user_id in user_ids:
    if not db_queries.user_by_id(db, user_id):
      logger.error(f'user id{user_id} is not valid. Skipped adding to editors of server {server.id}')
      continue
    if user_id == server.user:
      logger.error(f'user id {user_id} is the owner of server {server.id}. Skipped adding to editors')
      continue

    db.add(models.ServerEditor(server_id=server.id, user_id=user_id))
    db.commit()
