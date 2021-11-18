from typing import List
from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, username: str) -> models.User:
  user = db.query(models.User).filter(models.User.username == username).first()
  return user


def count_servers(db: Session, user: models.User) -> int:
  return db.query(models.Server).filter(models.Server.user == user.id).count()

def get_servers(db: Session, user: models.User) -> List[models.Server]:
  servers = db.query(models.Server).filter(models.Server.user == user.id).all()
  return servers

def get_server(db: Session, server_id: int) -> models.Server:
  server = db.query(models.Server).filter(models.Server.id == server_id).first()
  return server

def get_active_servers(db: Session, region: str) -> List[models.Server]:
  query = db.query(models.Server)
  query = query.filter(models.Server.region == region)
  query = query.filter(models.Server.status == 'running')
  servers = query.all()
  return servers
