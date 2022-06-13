from typing import List

from sqlalchemy.orm.session import Session

from .database import models
from .schema.game_server_config import GameServerConfig


def diff_game_server_config(old_config: GameServerConfig, new_config: GameServerConfig):
  old = old_config.dict()
  new = new_config.dict()
  diff = {}
  all_keys = set(old.keys()).union(set(new.keys()))
  for key in all_keys:
    old_val = old.get(key)
    new_val = new.get(key)
    if old_val != new_val:
      diff[key] = {
        'old': old_val,
        'new': new_val
      }
  return diff

def add_version(db: Session, server: models.Server) -> None:
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
      return

  db.add(models.ServerVersion(
    server_id = server.id,
    server_config= server.server_config,
    num_changes = num_changes,
    created_at = server.updated_at,
    created_by = server.updated_by
  ))
  db.commit()

def get_versions(db: Session, server: models.Server) -> List[models.ServerVersion]:
  return list(
    db.query(models.ServerVersion)
      .filter(models.ServerVersion.server_id == server.id)
      .all()
  )
