from typing import List
from sqlalchemy.orm import Session
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
  return servers

def get_server(db: Session, server_id: int) -> models.Server:
  server = db.query(models.Server).filter(models.Server.id == server_id).first()
  return server

def get_active_servers(db: Session, region: str = None, user: models.User = None) -> List[models.Server]:
  query = db.query(models.Server)

  if region:
    query = query.filter(models.Server.region == region)

  if user:
    query = query.filter(models.Server.owner == user.id)
    
  query = query.filter(models.Server.status == 'running')
  servers = query.all()
  return servers
