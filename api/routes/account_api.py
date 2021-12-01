"""
/api/account/*
Enpoints in the Account API are for login & user account management.
"""
from os import stat
from typing import List
from passlib.hash import argon2
from fastapi import Depends, status as http_status, Request
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi_login.exceptions import InvalidCredentialsException
from slowapi.extension import Limiter
from sqlalchemy.orm.session import Session
from schema.requests import UpdatePasswordRequest
from schema import requests, responses
import database.queries as db_queries
from database import models, queries

from dependencies import dependencies as deps
import time
from loguru import logger

router = APIRouter()


def _to_user_response(user: models.User, db: Session):
  return responses.User(
    id=user.id,
    username=user.username,
    tier=user.tier,
    limits=responses.UserLimits(
      server_limit=user.limits.server_limit,
      active_limit=user.limits.active_limit,
      server_count=db_queries.count_servers(db, user)
    )
  )


@router.post('/account/login')
async def login(login: requests.LoginRequest, db: Session = Depends(deps.db)):
  user = db_queries.get_user(db, login.username)

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


@router.get('/account/user')
async def get_user(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  db_user = db.query(models.User).filter_by(id=user.id).first()
  return _to_user_response(db_user, db)


@router.get('/accounts')
async def list_accounts(
  user: models.User = Depends(deps.login_admin),
  db: Session = Depends(deps.db)) -> List[models.User]:
  all_users = db.query(models.User).all()
  return [
    _to_user_response(u, db)
    for u in all_users
  ]

@router.post('/account/change_password')
async def change_password(
  request: UpdatePasswordRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):

  if not argon2.verify(request.current_password, user.password):
    raise InvalidCredentialsException
  
  user.password = argon2.hash(request.new_password)
  db.add(user) # user is from different db session and needs to be added to this one
  db.commit()


@router.post('/account/create')
async def create_account(create_req: requests.AccountCreateRequest, request: Request, db: Session = Depends(deps.db)):

  # only allow 1 account to be created from a client address
  # this only persists during the lifetime of the process but probably good enough
  if request.client.host in deps.created_account:
    logger.error(f'Client @ {request.client.host} tried to create extra account: {create_req.username}')
    raise HTTPException(
      status_code=http_status.HTTP_429_TOO_MANY_REQUESTS
    )
  deps.created_account.add(request.client.host)

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