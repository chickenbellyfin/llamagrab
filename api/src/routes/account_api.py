"""
/api/account/*
Enpoints in the Account API are for login & user account management.
"""
from typing import List

from fastapi import Depends, Request
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi_login.exceptions import InvalidCredentialsException
from loguru import logger
from passlib.hash import argon2
from sqlalchemy.orm.session import Session
from src.database import models
from src.database import queries as db_queries
from src.dependencies import dependencies as deps
from src.schema import requests, responses
from src.schema.requests import UpdatePasswordRequest
from src import flags

router = APIRouter()


def _to_account_response(user: models.User, db: Session):
  """
  Response for admin view of accounts
  """
  return responses.UserAccount(
    id=user.id,
    username=user.username,
    tier=user.tier,
    limits=responses.UserLimits(
      server_limit=user.limits.server_limit,
      active_limit=user.limits.active_limit,
      server_count=db_queries.count_servers(db, user)
    ),
    tribes_username=user.tribes_username
  )


@router.post('/account/login', tags=['account'])
async def login(login: requests.LoginRequest, db: Session = Depends(deps.db)):
  """ Login to an account. Returns an access_token which must be included in the authorization
      header for most requests.
      Header is 'Authorization': 'Bearer $access_token'
  """
  user = db_queries.get_user(db, login.username)

  deps.check_account_disabled_flags(user)

  if not user:
    raise InvalidCredentialsException
  elif not argon2.verify(login.password, user.password):
    raise InvalidCredentialsException

  access_token = deps.login_manager.create_access_token(data=dict(sub=login.username))
  # API will expect header:
  # Authorization: Bearer <access_token>
  return {
    'access_token': access_token
  }


@router.get('/account/user', tags=['account'])
async def get_user(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  """ Get the currently logged in user"""
  db_user = db.query(models.User).filter_by(id=user.id).first()
  return _to_account_response(db_user, db)


@router.get('/accounts', include_in_schema=False)
async def list_accounts(
  user: models.User = Depends(deps.login_admin),
  db: Session = Depends(deps.db)) -> List[responses.UserAccount]:
  """Get all user accounts with roles & limits. For admin panel use"""
  all_users = db.query(models.User).all()
  return [
    _to_account_response(u, db)
    for u in all_users
  ]

@router.get('/users', tags=['account'])
async def list_users(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)
) -> List[responses.User]:
  """Get all usernames & ids"""
  all_users = db.query(models.User).all()
  return [
    responses.User(id=u.id, username=u.username)
    for u in all_users
  ]

@router.post('/account/change_password', tags=['account'])
async def change_password(
  request: UpdatePasswordRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  """ Changes the account password. Must be logged in"""
  if not argon2.verify(request.current_password, user.password):
    raise InvalidCredentialsException

  user.password = argon2.hash(request.new_password)
  db.merge(user) # user is from different db session and needs to be added to this one
  db.commit()


@router.post('/account/set_tribes_name', tags=['account'])
async def set_tribes_name(
  request: requests.SetTribesUsernameRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  user.tribes_username = request.tribes_username
  db.merge(user)
  db.commit()


def _get_ip(request: Request):
  forwarded = request.headers.get("X-Forwarded-For")
  if forwarded:
      return forwarded.split(",")[0]
  return request.client.host

@router.post('/account/create', include_in_schema=False)
async def create_account(create_req: requests.AccountCreateRequest, request: Request, db: Session = Depends(deps.db)):
  client_host = _get_ip(request)
  
  if flags.get_flag(db, 'disable_new_accounts'):
    logger.info(f"Blocked new account from IP {client_host} because flag disable_new_accounts is enabled")
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  # only allow 1 account to be created from a client address
  # this only persists during the lifetime of the process but probably good enough
  if client_host in deps.created_account:
    logger.error(f'Client @ {client_host} tried to create extra account: {create_req.username}')
    raise HTTPException(
      status_code=http_status.HTTP_429_TOO_MANY_REQUESTS
    )

  if db_queries.get_user(db, create_req.username) != None:
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail="User already exists"
    )

  logger.info(f"Creating new user {create_req.username}")
  new_user = models.User(
    username=create_req.username,
    password=argon2.hash(create_req.password)
  )
  db.add(new_user)
  db.commit()
  db.add(models.UserLimits(user_id=new_user.id, server_limit=1, active_limit=1))
  db.commit()
  logger.info(f'Client @ {client_host} created account: {new_user.username}')
  # record client created an account
  deps.created_account.add(client_host)

@router.delete('/account/{user_id}', include_in_schema=False)
async def delete_user(user_id: int, admin: models.User = Depends(deps.login_super), db: Session = Depends(deps.db)):
  user_to_delete = db_queries.user_by_id(db, user_id)

  if not user_to_delete:
    raise HTTPException(
      status_code=http_status.HTTP_404_NOT_FOUND
    )
  else:
    servers_to_delete = db_queries.get_servers(db, user_to_delete)
    for server in servers_to_delete:
      db.delete(server)
    db.query(models.ServerEditor).filter(models.ServerEditor.user_id == user_to_delete.id).delete()
    db.delete(user_to_delete)
    db.commit()
  deps.host_manager().sync()
