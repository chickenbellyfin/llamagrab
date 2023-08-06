from typing import Optional
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

# NOTE:
# - All tables with a autoincrement should have `__table_args__ = {'sqlite_autoincrement': True}`,
#   which configures sqlite to never re-use autoincrement ids
# - All relationships should have lazy=joined so that the object can be used outside of a session


class User(Base):
  __tablename__ = 'users'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  username: Mapped[str] = mapped_column(unique=True)
  password: Mapped[str] # hashed
  tier: Mapped[str] = mapped_column(default='unverified')
  tribes_username: Mapped[Optional[str]]

  servers = relationship(
    "Server", 
    back_populates='owner', 
    foreign_keys='Server.user', 
    lazy='joined',
    cascade="all, delete"
  )
  limits = relationship(
    "UserLimits", 
    uselist=False, 
    lazy='joined',
    cascade="all, delete"
  )

  def __str__(self):
    return f'User(id={self.id} name="{self.username}")'

class UserLimits(Base):
  __tablename__ = 'user_limits'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  server_limit: Mapped[Optional[int]]
  active_limit: Mapped[Optional[int]]

  relationship('User', back_populates='limits', lazy='joined')


class Server(Base):
  __tablename__ = 'servers'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  user: Mapped[int] = mapped_column(ForeignKey('users.id'))
  name: Mapped[str]
  region: Mapped[str]
  enabled: Mapped[bool] = mapped_column(default=False)
  game: Mapped[str]
  server_config: Mapped[str]
  updated_at: Mapped[int]
  updated_by: Mapped[int] = mapped_column(ForeignKey('users.id'))

  owner: Mapped[User] = relationship("User", back_populates="servers", foreign_keys=[user], lazy='joined')

  def __str__(self):
    return f'Server(id={self.id} name="{self.name}")'


class ServerVersion(Base):
  __tablename__ = 'server_versions'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  server_id: Mapped[int] = mapped_column(ForeignKey('servers.id'))
  server_config: Mapped[str]
  num_changes: Mapped[int]
  created_at: Mapped[int] 
  created_by: Mapped[int] = mapped_column(ForeignKey('users.id'))

  server: Mapped[Server] = relationship("Server", foreign_keys=[server_id], lazy='joined')
  creator: Mapped[User] = relationship('User', foreign_keys=[created_by], lazy='joined')

  def __str__(self):
    return f'ServerVersion(id={self.id})'

class ServerEditor(Base):
  __tablename__ = 'server_editors'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # not used, required by sqlalchemy
  server_id: Mapped[int] = mapped_column(ForeignKey('servers.id'))
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

  server = relationship('Server', foreign_keys=[server_id], lazy='joined')
  user = relationship('User', foreign_keys=[user_id], lazy='joined')

class Flag(Base):
  __tablename__ = 'flags'
  key: Mapped[str] = mapped_column(primary_key=True)
  value: Mapped[str]

  def __str__(self):
    return f'Flag(key={self.key} value={self.value})'

class AuditLogEvent(Base):
  __tablename__ = 'audit_log'
  __table_args__ = {'sqlite_autoincrement': True}
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  timestamp: Mapped[int]
  details: Mapped[str]
  user_id: Mapped[int] # not FK since it can't be deleted
  user_name: Mapped[str]
  user_tier: Mapped[str]
