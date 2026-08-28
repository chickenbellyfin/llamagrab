from typing import List

from sqlalchemy.orm.session import Session

from api.database import models
from api.schema.game_server_config import GameServerConfig


def diff_game_server_config(old_config: GameServerConfig, new_config: GameServerConfig):
  old = old_config.dict()
  new = new_config.dict()
  diff = {}
  all_keys = set(old.keys()).union(set(new.keys()))
  for key in all_keys:
    old_val = old.get(key)
    new_val = new.get(key)

    if type(old_val) is list and type(new_val) is list:
      # if the data is a list, show only the items that changed
      removed = [x for x in old_val if x not in new_val]
      added = [x for x in new_val if x not in old_val]
      if len(removed) > 0 or len(added) > 0:
        diff[key] = {
          'old': removed,
          'new': added
        }
    else:
      # treat empty list as None
      if old_val == []:
        old_val = None
      if new_val == []:
        new_val = None

      if old_val != new_val:
        diff[key] = {
          'old': old_val,
          'new': new_val
        }
  return diff

def add_version(db: Session, server: models.Server) -> models.ServerVersion:
  # Get the latest version for server or None
  previous = (
    db.query(models.ServerVersion)
      .filter(models.ServerVersion.server_id == server.id)
      .order_by(models.ServerVersion.id.desc())
      .limit(1)
      .first()
  )

  if not previous:
    num_changes = -1 # no previous versions, -1 means 'server created'
  else:
    config_diff = diff_game_server_config(
      GameServerConfig.parse(previous.server_config),
      GameServerConfig.parse(server.server_config)
    )
    num_changes = len(config_diff.keys())

    # don't record a version if nothing changed
    if num_changes == 0:
      return previous

  new_version = models.ServerVersion(
    server_id = server.id,
    server_config= server.server_config,
    num_changes = num_changes,
    created_at = server.updated_at,
    created_by = server.updated_by
  )
  db.add(new_version)
  db.commit()
  return new_version

def get_versions(db: Session, server: models.Server) -> List[models.ServerVersion]:
  return list(
    db.query(models.ServerVersion)
      .filter(models.ServerVersion.server_id == server.id)
      .all()
  )

def get_diff(db: Session, server: models.Server, version: int):

  versions = get_versions(db, server)
  current = db.query(models.ServerVersion).filter(models.ServerVersion.id == version).first()
  prev_idx = versions.index(current) - 1

  if prev_idx < 0:
    return {}

  prev = versions[prev_idx]
  return diff_game_server_config(
    GameServerConfig.parse(prev.server_config),
    GameServerConfig.parse(current.server_config)
  )
