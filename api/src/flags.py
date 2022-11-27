from collections import namedtuple

from sqlalchemy.orm.session import Session
from .database import models
import json

Flag = namedtuple('Flag', 'type,default')

FLAGS = {
  'disable_new_accounts': Flag(bool, False),
  'disable_unverified_accounts': Flag(bool, False),
  'disable_non_admin_accounts': Flag(bool, False)
}

def _query_flag(db: Session, key: str):
    if key not in FLAGS:
      raise Exception(f'\"{key}\" is not a valid flag')
    
    flag = db.query(models.Flag).filter(models.Flag.key == key).first()
    if flag is None:
      flag = models.Flag(key = key, value = json.dumps(FLAGS[key].default))
      db.add(flag)
      db.commit()
    
    return flag
    

def get_flag(db: Session, key: str):
  flag = _query_flag(db, key)  
  return json.loads(flag.value)

def set_flag(db: Session, key: str, value):
  flag = _query_flag(db, key)
  flag.value = json.dumps(value)  
  db.commit()

def get_all_flags(db: Session):
  return {
    key: get_flag(db, key) for key in FLAGS
  }