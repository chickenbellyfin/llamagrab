from sqlalchemy.orm import Session
from database import models, queries
from loguru import logger

"""
Unverified:
  - Can create 1 server
  - Can not choose region
  - Can not set server password, or server admins
  - limit of 3 active servers of all unverified users, globally
    - 2 most recently started servers will run

Verified:
  - Can create up to 5 servers, 2 active
  - Can choose region, server password, and server admins
  - passworded servers have a 6 hour limit & 24 hour cooldown

Admin:
  - Unlimited servers
  - can verify users
  - Can view all server data and is admin on all servers

Super:
 - can create admins
"""
TIERS = {
  'unverified': 0,
  'verified': 1,
  'admin': 2,
  'super': 3
}


def is_verified(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['verified']

def is_admin(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['admin']

def is_super(user: models.User) -> bool:
  return TIERS[user.tier] >= TIERS['super']

def can_create_server(db: Session, user: models.User) -> bool:
  count = queries.count_servers(db, user)
  limit = queries.user_by_id(db, user.id).limits.server_limit
  logger.info(f'user={user.id} count={count} limit={limit}')
  return limit is None or count < limit


def can_start_server(db: Session, user: models.User, server: models.Server) -> bool:
  
  pass


def can_verify_user(user: models.User) -> bool:
  pass

