from typing import List
from sqlalchemy.orm import Session
from database import models, queries
from loguru import logger

"""
Unverified:
  - Can create 1 server
  - Can not choose region
  - Can not set server password, or server admins
  - limit of 3 active servers of all unverified users, globally
    - 2 most recently started servers will run

Verified:
  - Can create up to 5 servers, 2 active
  - Can choose region, server password, and server admins
  - passworded servers have a 6 hour limit & 24 hour cooldown

Admin:
  - Unlimited servers
  - can verify users
  - Can view all server data and is admin on all servers

Super:
 - can create admins
"""
TIERS = {
  'unverified': 0,
  'verified': 1,
  'admin': 2,
  'super': 3
}

def is_verified(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['verified']

def is_admin(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['admin']

def is_super(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['super']

def can_create_server(db: Session, user: models.User) -> bool:
  count = queries.count_servers(db, user)
  limit = queries.user_by_id(db, user.id).limits.server_limit
  logger.info(f'user={user.id} count={count} limit={limit}')
  return limit is None or count < limit


def get_shared_servers(db: Session, user: models.User) -> List[models.Server]:
  server_editors = db.query(models.ServerEditor).filter(models.ServerEditor.user_id == user.id).all()
  return [
    s.server for s in server_editors
  ]

def get_server_editors(db: Session, server: models.Server) -> List[models.User]:
  server_editors = db.query(models.ServerEditor).filter(models.ServerEditor.server_id == server.id).all()
  return [s.user for s in server_editors]

def set_server_editors(db: Session, server: models.Server, editors: List[int]):
  # validate that editors is a list of valid user ids
  for editor in editors:
    if not queries.user_by_id(db, editor):
      raise Exception(f'User id {editor} is not valid')
  
  db.query(models.ServerEditor).filter(models.ServerEditor.server_id == server.id).delete()
  
  for editor in editors:
    if editor != server.user:
      db.add(models.ServerEditor(server_id=server.id, user_id=editor))
  db.commit()

def is_editor(db: Session, user: models.User, server: models.Server):
  editor = (db
    .query(models.ServerEditor)
    .filter(models.ServerEditor.server_id == server.id)
    .filter(models.ServerEditor.user_id == user.id)
    .first()
  )
  return editor is not None

def can_read_server(db: Session, user: models.User, server: models.Server) -> bool:
  is_owner = user.id == server.user
  return is_owner or is_admin(user) or is_editor(db, user, server)

def can_write_server(db: Session, user: models.User, server: models.Server) -> bool:
  is_owner = user.id == server.user
  return is_owner or is_admin(user) or is_editor(db, user, server)

def can_start_server(db: Session, user: models.User, server: models.Server) -> bool:
  pass
