from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from .database import Base

# NOTE:
# - All tables with a autoincrement should have `__table_args__ = {'sqlite_autoincrement': True}`,
#   which configures sqlite to never re-use autoincrement ids
# - All relationships should have lazy=joined so that the object can be used outside of a session


class User(Base):
  __tablename__ = 'users'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String, nullable=False, unique=True)
  password = Column(String, nullable=False) # hashed
  tier = Column(String, default='unverified')
  tribes_username = Column(String)

  servers = relationship("Server", back_populates='owner', foreign_keys='Server.user', lazy='joined')
  limits = relationship("UserLimits", uselist=False, lazy='joined')

  def __str__(self):
    return f'User(id={self.id} name="{self.username}")'

class UserLimits(Base):
  __tablename__ = 'user_limits'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('users.id'))
  server_limit = Column(Integer)
  active_limit = Column(Integer)

  relationship('User', back_populates='limits', lazy='joined')


class Server(Base):
  __tablename__ = 'servers'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True)
  user = Column(Integer, ForeignKey('users.id'))
  name = Column(String, nullable=False)
  region = Column(String)
  enabled = Column(Boolean, default=False, nullable=False)
  game = Column(String, nullable=False)
  server_config = Column(String)
  updated_at = Column(Integer, nullable=False)
  updated_by = Column(Integer, ForeignKey('users.id'), nullable=False)

  owner: User = relationship("User", back_populates="servers", foreign_keys=[user], lazy='joined')

  def __str__(self):
    return f'Server(id={self.id} name="{self.name}")'


class ServerVersion(Base):
  __tablename__ = 'server_versions'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True)
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  server_config = Column(String, nullable=False)
  num_changes = Column(Integer, nullable=False)
  created_at = Column(Integer, nullable=False)
  created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

  server = relationship("Server", foreign_keys=[server_id], lazy='joined')
  creator = relationship('User', foreign_keys=[created_by], lazy='joined')

  def __str__(self):
    return f'ServerVersion(id={self.id})'

class ServerEditor(Base):
  __tablename__ = 'server_editors'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True) # not used, required by sqlalchemy
  server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

  server = relationship('Server', foreign_keys=[server_id], lazy='joined')
  user = relationship('User', foreign_keys=[user_id], lazy='joined')

class Flag(Base):
  __tablename__ = 'flags'
  key = Column(String, nullable=False, primary_key=True)
  value = Column(String)

  def __str__(self):
    return f'Flag(key={self.key} value={self.value})'

class AuditLogEvent(Base):
  __tablename__ = 'audit_log'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True, autoincrement=True)
  timestamp = Column(Integer, nullable=False)
  details = Column(String, nullable=False)
  user_id = Column(Integer, nullable=False) # not FK since it can't be deleted
  user_name = Column(String, nullable=False)
  user_tier = Column(String, nullable=False)
