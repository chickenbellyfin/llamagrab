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
  tier = Column(String, default='unverified')
  tribes_username = Column(String)

  servers = relationship("Server", back_populates='owner', foreign_keys='Server.user')
  limits = relationship("UserLimits", uselist=False)

class UserLimits(Base):
  __tablename__ = 'user_limits'
  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('users.id'))
  server_limit = Column(Integer)
  active_limit = Column(Integer)

  relationship('User', back_populates='limits')


class Server(Base):
  __tablename__ = 'servers'
  id = Column(Integer, primary_key=True, autoincrement=True)
  user = Column(Integer, ForeignKey('users.id'))
  name = Column(String, nullable=False)
  region = Column(String)
  status = Column(String, default='stopped')
  game_mode = Column(String, default='CTF')
  server_config = Column(String)
  updated_at = Column(Integer, nullable=False)
  updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

  owner = relationship("User", back_populates="servers", foreign_keys=[user])


class ServerVersion(Base):
  __tablename__ = 'server_versions'
  id = Column(Integer, primary_key=True, autoincrement=True)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  server_config = Column(String, nullable=False)
  num_changes = Column(Integer, nullable=False)
  created_at = Column(Integer, nullable=False)
  created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

  server = relationship("Server", foreign_keys=[server_id])
  creator = relationship('User', foreign_keys=[created_by])

class ServerEditor(Base):
  __tablename__ = 'server_editors'  
  id = Column(Integer, primary_key=True, autoincrement=True) # not used, required by sqlalchemy
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

  server = relationship('Server', foreign_keys=[server_id])
  user = relationship('User', foreign_keys=[user_id])

