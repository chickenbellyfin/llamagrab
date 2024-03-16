import os
import time
from ipaddress import ip_network
from typing import List, Optional

from loguru import logger
from sqlalchemy import Column, Integer, create_engine, desc
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            scoped_session, sessionmaker)

from api import permissions
from api.audit import AuditLog
from api.database.models import User
from api.host_manager import HostManager
from api.service import exceptions
from common import polling

Base = declarative_base()


class IPLogEntry(Base):
  __tablename__ = 'iplogs'
  id = Column(Integer, primary_key=True, autoincrement=True)
  timestamp: Mapped[int]
  label: Mapped[str]
  user_id: Mapped[int]
  display_name: Mapped[str]
  ip: Mapped[str] 

class IPBan(Base):
  __tablename__ = "ip_bans"
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  ip: Mapped[str]
  reason: Mapped[Optional[str]]
  created_at: Mapped[int]
  created_by: Mapped[str] # no FK since its a separate DB

  def __str__(self):
    return f'IPBan(ip={self.ip} reason="{self.reason}")'

class IPLogDatabase():
  def __init__(self, base_path, host_manager: HostManager, audit: AuditLog, db_file_name='iplog.db'):
    db_file_path = os.path.join(base_path, db_file_name)
    db_url = f'sqlite:///{db_file_path}'
    logger.info(f'path={db_file_path} url={db_url}')

    self.host_manager = host_manager
    self.audit = audit
    self.engine = create_engine(db_url)
    Base.metadata.create_all(bind=self.engine)
    self.SessionFactory: sessionmaker = scoped_session(
      sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)
    )
    self.interval_secs = 3600
    self.banlist_file_path = os.path.join(base_path, 'banlist.txt')

    polling.fixed_rate(self._poll, self.interval_secs)

  def _check_admin(self, user: User):
    if not permissions.is_admin(user):
      raise exceptions.PermissionsException()

  def _poll(self):
    iplogs = self.host_manager.iplogs()

    if len(iplogs) > 0:
      logger.info(f'Merging {len(iplogs)} entries to IP Logs')

    added = 0
    updated = 0
    ignored = 0

    for iplog in iplogs:
      
      # match existing by player id, name, ip, and server id (label)
      filter_args = {
        'user_id': iplog['user_id'],
        'display_name': iplog['display_name'],
        'ip': iplog['ip'],
        'label': iplog['label']
      }
      

      with self.SessionFactory() as db:
        entry = db.query(IPLogEntry).filter_by(**filter_args).first()
        if entry is not None:
          # update timestamp (last seen) if its newer
          if iplog['timestamp'] > entry.timestamp:
            entry.timestamp = iplog['timestamp']
            updated += 1
          else:
            ignored += 1
        else:
          entry = IPLogEntry(**iplog)
          db.add(entry)
          added += 1
        db.commit()
    
    if added + updated + ignored > 0:
      logger.info(f'Added {added}, Updated {updated}, Ignored {ignored}')
  
  def do_poll(self, user: User):
    self._check_admin(user)
    self._poll()

  def get(self, user: User) -> List[IPLogEntry]:
    self._check_admin(user)
    with self.SessionFactory() as db:
      return db.query(IPLogEntry).order_by(desc(IPLogEntry.timestamp)).limit(1000).all()
  
  def get_bans(self, user: User) -> List[IPBan]:
    self._check_admin(user)
    with self.SessionFactory() as db:
      return db.query(IPBan).all()

  def create_ban(self, ip: str, reason: str, user: User):
    self._check_admin(user)
    
    try:
      network = ip_network(ip)
    except ValueError as e:
      raise exceptions.BadArgumentsException(str(e))

    if network.prefixlen < 8:
      raise exceptions.BadArgumentsException('netmask can not be < 8 bits')
    if not network.is_global:
      raise exceptions.BadArgumentsException('IP must be public')
    
    with self.SessionFactory() as db:
      if db.query(IPBan).filter_by(ip = ip).count() > 0:
        logger.warning(f'IP Ban for {ip} already exists, skipping')
        created = False
      else:
        new_ban = IPBan(
          ip=ip,
          reason=reason,
          created_at=int(time.time()),
          created_by=user.username
        )
        db.add(new_ban)
        db.commit()
        created = True
        
    if created:
      self.audit(user, f'created {created}')
      self.push_banlist(user)
    
    return
  
  def remove_ban(self, id: int, user: User) -> IPBan:
    self._check_admin(user)
    with self.SessionFactory() as db:
      to_delete = db.query(IPBan).filter_by(id = id).first()
      db.delete(to_delete)
      db.commit() 
    self.push_banlist(user)
    
    self.audit(user, f'deleted {to_delete}')
    return to_delete
  
  def push_banlist(self, user: User):
    self._check_admin(user)
    with self.SessionFactory() as db:
      bans = db.query(IPBan.ip).all()
    ips = [b.ip for b in bans]
    self.host_manager.banlist(ips)
    self.audit(user, 'triggered IP banlist push')

    # write banlist file locally
    txt = ''
    for ip in ips:
      txt += f'{ip}\n'
    with open(self.banlist_file_path, 'w') as f:
      f.write(txt)
