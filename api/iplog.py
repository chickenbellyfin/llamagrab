import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from api.host_manager import HostManager
from loguru import logger
import time

from common import polling

Base = declarative_base()


class IPLogEntry(Base):
  __tablename__ = 'iplogs'
  id = Column(Integer, primary_key=True, autoincrement=True)
  timestamp = Column(Integer, nullable=False)
  label = Column(String, nullable=False)
  user_id = Column(Integer, nullable=False)
  display_name = Column(String, nullable=False)
  ip = Column(String, nullable=False)

class IPBan(Base):
  __tablename__ = "ip_bans"
  id = Column(Integer, primary_key=True, autoincrement=True)
  ip = Column(String, nullable=False)
  reason = Column(String)
  created_at = Column(Integer, nullable=False)
  created_by = Column(String, nullable=False) # no FK since its a separate DB

  def __str__(self):
    return f'IPBan(ip={self.ip} reason="{self.reason}")'

class IPLogDatabase():
  def __init__(self, base_path, host_manager: HostManager, db_file_name='iplog.db'):
    db_file_path = os.path.join(base_path, db_file_name)
    db_url = f'sqlite:///{db_file_path}'
    logger.info(f'path={db_file_path} url={db_url}')

    self.host_manager = host_manager
    self.engine = create_engine(db_url)
    Base.metadata.create_all(bind=self.engine)
    self.SessionFactory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False))
    self.interval_secs = 3600
    self.banlist_file_path = os.path.join(base_path, 'banlist.txt')

    polling.fixed_rate(self._poll, self.interval_secs)


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
  
  def get(self) -> List[IPLogEntry]:
    with self.SessionFactory() as db:
      return db.query(IPLogEntry).all()
  
  def get_bans(self) -> List[IPBan]:
    with self.SessionFactory() as db:
      return db.query(IPBan).all()

  def create_ban(self, ip: str, created_by: str, reason: str = None) -> IPBan:
    push = True
    new_ban = None
    with self.SessionFactory() as db:
      if db.query(IPBan).filter_by(ip = ip).count() > 0:
        logger.warning(f'IP Ban for {ip} already exists, skipping')
        push = False
      else:
        new_ban = IPBan(
          ip=ip,
          reason=reason,
          created_at=int(time.time()),
          created_by=created_by
        )
        db.add(new_ban)
        db.commit()
        
    if push:
      self.push_banlist()
    
    return new_ban
  
  def remove_ban(self, id: int) -> IPBan:
    with self.SessionFactory() as db:
      to_delete = db.query(IPBan).filter_by(id = id).first()
      db.delete(to_delete)
      db.commit() 
    self.push_banlist()
    return to_delete
  
  def push_banlist(self):
    with self.SessionFactory() as db:
      bans = db.query(IPBan.ip).all()
    ips = [b.ip for b in bans]
    self.host_manager.banlist(ips)

    # write banlist file locally
    txt = ''
    for ip in ips:
      txt += f'{ip}\n'
    with open(self.banlist_file_path, 'w') as f:
      f.write(txt)
