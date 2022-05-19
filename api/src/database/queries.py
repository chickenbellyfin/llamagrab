from typing import List
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models


def user_by_id(db: Session, id: int) -> models.User:
  return db.query(models.User).filter(models.User.id == id).first()

def get_user(db: Session, username: str) -> models.User:
  user = db.query(models.User).filter(models.User.username == username).first()
  return user

def count_servers(db: Session, user: models.User) -> int:
  return db.query(models.Server).filter(models.Server.user == user.id).count()

def get_servers(db: Session, user: models.User) -> List[models.Server]:
  servers = db.query(models.Server).filter(models.Server.user == user.id).all()
  return list(servers)

def get_server(db: Session, server_id: int) -> models.Server:
  server = db.query(models.Server).filter(models.Server.id == server_id).first()
  return server

def get_active_servers(db: Session, region: str = None, user: models.User = None) -> List[models.Server]:
  query = db.query(models.Server)

  if region:
    query = query.filter(models.Server.region == region)

  if user:
    query = query.filter(models.Server.owner == user.id)

  query = query.filter(models.Server.enabled)
  servers = query.all()
  return list(servers)

def get_admin_tribes_usernames(db: Session) -> List[str]:
  query = db.query(models.User.tribes_username)
  query = query.filter(or_(models.User.tier == 'admin', models.User.tier == 'super'))
  query = query.filter(models.User.tribes_username.isnot(None))
  result = query.all()
  return list(map(lambda t: t[0], result))
