from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from sqlalchemy.sql.schema import ForeignKey
from .database import Base

class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=False) # hashed
  role = Column(String, default='user')
  server_quota = Column(Integer, default=1, nullable=False)

  servers = relationship("Server", back_populates='owner')



class Server(Base):
  __tablename__ = 'servers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  user = Column(Integer, ForeignKey('users.id'))
  name = Column(String, nullable=False)
  region = Column(String)
  status = Column(String, default='stopped')
  game_mode = Column(String, default='CTF')
  server_config = Column(String)

  owner = relationship("User", back_populates="servers")

class Invite(Base):
  __tablename__ = 'invites'
  token = Column(String, primary_key=True)
  expires_at = Column(Integer)
  created_by = Column(Integer, ForeignKey('users.id'))
  used_by = Column(Integer, ForeignKey('users.id'))
