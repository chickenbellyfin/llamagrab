import json
from typing import Any, List

from attrs import define
from sqlalchemy.orm.session import Session

from api.database import models


@define
class Flag:
  flag_type: type
  default: Any
  options: list = None

FLAGS = {
  'disable_new_accounts': Flag(bool, False),
  'disable_unverified_accounts': Flag(bool, False),
  'disable_non_admin_accounts': Flag(bool, False),
  'loginserver': Flag(str, None, ['ta.kfk4ever.com', 'llamagrab.net'])
}

def _query_flag(db: Session, key: str):
    if key not in FLAGS:
      raise TypeError(f'\"{key}\" is not a valid flag')
    
    flag = db.query(models.Flag).filter(models.Flag.key == key).first()
    if flag is None:
      flag = models.Flag(key = key, value = json.dumps(FLAGS[key].default))
      db.add(flag)
      db.commit()
    
    return flag

def set_loginserver_urls(urls: List[str]):
  FLAGS['loginserver'].options = list(urls)

def get_flag(db: Session, key: str):
  flag = _query_flag(db, key) 
  return json.loads(flag.value)

def set_flag(db: Session, key: str, value):
  flag = _query_flag(db, key)

  if type(value) != FLAGS[key].flag_type:
    raise TypeError(f'Value "{value}" for flag \"{key}\" is {type(value)} but must be {FLAGS[key].flag_type}')
  if FLAGS[key].options is not None and value not in FLAGS[key].options:
    raise TypeError(f'Value "{value}" for flag \"{key}\" is not allowed ({FLAGS[key].options})')

  flag.value = json.dumps(value)  
  db.commit()

def get_all_flags(db: Session):
  return {
    key: get_flag(db, key) for key in FLAGS
  }