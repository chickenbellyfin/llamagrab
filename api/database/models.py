from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
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

  def __str__(self):
    return f'User(id={self.id} name={self.username})'

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
  enabled = Column(Boolean, default=False, nullable=False)
  game = Column(String, nullable=False)
  server_config = Column(String)
  updated_at = Column(Integer, nullable=False)
  updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

  owner: User = relationship("User", back_populates="servers", foreign_keys=[user])

  def __str__(self):
    return f'Server(id={self.id} name={self.name})'


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

  def __str__(self):
    return f'ServerVersion(id={self.id})'

class ServerEditor(Base):
  __tablename__ = 'server_editors'
  id = Column(Integer, primary_key=True, autoincrement=True) # not used, required by sqlalchemy
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

  server = relationship('Server', foreign_keys=[server_id])
  user = relationship('User', foreign_keys=[user_id])

class Flag(Base):
  __tablename__ = 'flags'
  key = Column(String, nullable=False, primary_key=True)
  value = Column(String)

class AuditLogEvent(Base):
  __tablename__ = 'audit_log'
  id = Column(Integer, primary_key=True, autoincrement=True)
  timestamp = Column(Integer, nullable=False)
  details = Column(String, nullable=False)
  user_id = Column(Integer, nullable=False) # not FK since it can't be deleted
  user_name = Column(String, nullable=False)
  user_tier = Column(String, nullable=False)
