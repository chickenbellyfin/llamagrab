import json
from typing import Any, Dict

from attrs import define

from api import permissions
from api.audit import AuditLog
from api.database import models
from api.database.database import Database
from api.schema.app_config import Loginserver
from api.service import exceptions


@define
class Flag:
  flag_type: type
  default: Any
  options: list = None

FLAGS: Dict[str, Flag] = {
  'disable_new_accounts': Flag(bool, False),
  'disable_unverified_accounts': Flag(bool, False),
  'disable_non_admin_accounts': Flag(bool, False),
  'loginserver': Flag(str, None, ['ta.kfk4ever.com', 'llamagrab.net'])
}

class Flags:

  def __init__(
      self, 
      database: Database,
      audit: AuditLog,
      loginservers: Dict[str, Loginserver]
    ):
    self.database = database
    self.audit = audit
    self.FLAGS = FLAGS
    self.FLAGS['loginserver'].options = [l.url for l in loginservers] # TODO don't use global here

  def _check_admin(self, user: models.User):
    if not permissions.is_admin(user):
      raise exceptions.PermissionsException()

  def _query_flag(self, key: str):
      if key not in FLAGS:
        raise TypeError(f'\"{key}\" is not a valid flag')
      
      with self.database.session() as db:
        flag = db.query(models.Flag).filter(models.Flag.key == key).first()
        if flag is None:
          flag = models.Flag(key = key, value = json.dumps(FLAGS[key].default))
          db.add(flag)
          db.commit()
      
      return flag

  def get_flag(self, key: str):
    flag = self._query_flag(key) 
    return json.loads(flag.value)

  def set_flag(self, key: str, value, user: models.User) -> Flag:
    self._check_admin(user)
    flag = self._query_flag(key)

    if type(value) != FLAGS[key].flag_type:
      raise TypeError(f'Value "{value}" for flag \"{key}\" is {type(value)} but must be {FLAGS[key].flag_type}')
    if FLAGS[key].options is not None and value not in FLAGS[key].options:
      raise TypeError(f'Value "{value}" for flag \"{key}\" is not allowed ({FLAGS[key].options})')

    with self.database.session() as db:
      flag.value = json.dumps(value)  
      db.add(flag)
      db.commit()
    self.audit(user, f'updated {flag}')
    return flag

  def get_all_flags(self, user: models.User):
    self._check_admin(user)
    return {
      key: self.get_flag(key) for key in FLAGS
    }
  