from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
import threading
import time

from .database import models
from .host_manager import HostManager

class ServerStatusManager:
  """
    Handles fetching & tracking server statuses from HostManager
    Compares running status with the servers's desired state to derive status as one of:
        offline, stopping, starting, running
  """
  def __init__(
    self, host_manager:
    HostManager,
    db_session: sessionmaker,
    polling_rate: int = 60
  ):
    self.host_manager = host_manager
    self.db_session = db_session
    self.polling_rate = polling_rate
    self.host_statuses = {}
    threading.Thread(target=self._poller, daemon=True).start()


  def _poller(self):
    while True:
        self.host_statuses = self.host_manager.status()
        time.sleep(self.polling_rate)


  def get_region_status(self, region):
    return self.host_statuses.get(region) is not None


  def get_server_status(self, server: models.Server) -> str:
    if server.region is None or self.host_statuses.get(server.region) is None:
      return 'offline'

    if server.enabled:
      if server.id in self.host_statuses[server.region]:
        return 'running'
      else:
        return 'starting'
    else:
      if server.id in self.host_statuses[server.region]:
        return 'stopping'
      else:
        return 'offline'
