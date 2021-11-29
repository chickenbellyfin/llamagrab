from passlib.hash import argon2
from sqlalchemy.orm.session import Session
from schema.game_server_config import GameServerConfig
from database import models, queries
from schema import requests, responses
from schema.game_server_config import GameServerConfig


with open('../common/default.json') as default_file:
  default_json = default_file.read()

users = [
  models.User(
    username='admin',
    password=argon2.hash('asdfasdf'),
    role='admin',
    server_quota=10)
]

servers = [
  requests.ServerCreateRequest(
    server_settings=responses.ServerSettings(
      region='central_us'
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
    ),
    server_config=GameServerConfig.parse(default_json)
  )
]

def populate(db: Session):
  for user in users:
    db.add(user)

  db.commit()
  user1 = queries.get_user(db, user.username)
  
  for server in servers:
    db_server = models.Server(
      user=user1.id,
      name=server.server_config.display_name,
      region=server.server_settings.region,
      server_config=server.server_config.serialize()
    )
    db.add(db_server)

  db.commit()

  tdm = db.query(models.Server).filter(models.Server.name == 'Custom CTF').first()
  tdm.status = 'running'
  db.commit()