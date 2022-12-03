import time

from passlib.hash import argon2
from sqlalchemy.orm.session import Session

from api.database import models, queries
from api.schema import requests, responses
from api.schema.game_server_config import GameServerConfig

with open('resources/defaults/tribes_ascend_ootb.json') as default_file:
  default_json = default_file.read()

users = [
  models.User(
    username='admin',
    password=argon2.hash('asdfasdf'),
    tier='super'
  )
]

servers = [
  requests.ServerCreateRequest(
    server_settings=responses.ServerSettings(
      region='central_us',
      game='tribes_ascend_ootb'
    ),
    server_config=GameServerConfig(
      display_name='NA Mixer',
      description='Mixer-Style Rules: No HS/chain, FF on',
      password='test',
      admin_password='testadmin',
      team_assign_type='unbalanced',
      auto_balance=False,
      time_limit=25,
      overtime_limit=10,
      friendly_fire=True,
      maps=['ctf_katabatic', 'ctf_dangerous_crossing']
    )
  ),
  requests.ServerCreateRequest(
    server_settings=responses.ServerSettings(
      region='west_us',
      game='tribes_ascend_ootb'
    ),
    server_config=GameServerConfig.parse(default_json)
  )
]

def populate(db: Session):
  for user in users:
    db.add(user)
    db.commit()

  db.add(models.UserLimits(user_id=user.id))


  db.commit()
  user1 = queries.get_user(db, user.username)

  for server in servers:
    db_server = models.Server(
      user=user1.id,
      name=server.server_config.display_name,
      region=server.server_settings.region,
      server_config=server.server_config.serialize(),
      game=server.server_settings.game,
      updated_at=int(time.time()),
      updated_by=user1.id
    )
    db.add(db_server)

  db.commit()

  tdm = db.query(models.Server).filter(models.Server.name == 'Custom CTF').first()
  tdm.enabled = True
  db.commit()
