from typing import Dict, List
from sanic import Request
from api.database import models, queries
from api.database.database import Database
from api.schema import responses
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from sqlalchemy.orm import Session

from api.server_status import ServerStatusManager

def if_htmx(value):
    return value if Request.get_current().headers.get('hx-request') else None

def server_status_list(
        servers: List[models.Server], 
        status_manager: ServerStatusManager,
        regions: Dict[str, Region],
        db: Session) -> List[responses.ServerStatus]:
    return [
      responses.ServerStatus(
        id=s.id,
        owner=queries.user_by_id(db, s.user).username,
        name=s.name,
        region=s.region,
        region_name=regions[s.region].name if s.region in regions else s.region,
        enabled=s.enabled,
        status=status_manager.get_server_status(s),
        game=s.game,
        is_private=GameServerConfig.parse(s.server_config).password is not None
      )
      for s in servers
    ]

def region_statuses(
    status_manager: ServerStatusManager,
    regions: Dict[str, Region],
    database: Database
):
    with database.session() as db:
      return [
        {
          'region_name': region.name,
          'online': status_manager.get_region_status(region.key),
          'servers': server_status_list(queries.get_active_servers(db, region.key), status_manager, regions, db)
        }
        for region in regions.values()
      ]