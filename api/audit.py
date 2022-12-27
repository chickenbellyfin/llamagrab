from typing import List
from api.database.database import Database
from api.database import models
from loguru import logger
import time

class AuditLog:
  """
    Audit log should only capture changes made and not 'reads'
  """
  def __init__(self, database: Database):
    self.database = database

  def __call__(self, user: models.User, details: str,):
    """
      Usage:
        audit(user, ' did something to {some resource}')
    """
    with self.database.session() as session:
      event = models.AuditLogEvent(
        timestamp=int(time.time()),
        details=details,
        user_id=user.id,
        user_name=user.username,
        user_tier=user.tier
      )
      session.add(event)
      session.commit()
      logger.info(f'Event: {user} {details}')
  
  def get(self) -> List[models.AuditLogEvent]:
    with self.database.session() as session:
      return session.query(models.AuditLogEvent).all()
  