from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm.session import Session

from database import models

def test_create_invite_user(test_client: TestClient, logged_in_user):
  response = test_client.post('/api/admin/invite', logged_in_user)
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_create_invite_admin(test_client: TestClient, db_session: Session, logged_in_admin):
  response = test_client.post('/api/admin/invite', logged_in_admin)
  token = response.json()['invite_token']
  db_invite = db_session.query(models.Invite).filter(models.Invite.token == token).first()
  assert response.status_code == status.HTTP_200_OK
  assert token is not None
  assert db_invite.token == token
