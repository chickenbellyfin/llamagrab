"""
/api/account/*
Enpoints in the Account API are for login & user account management.
"""
from passlib.hash import argon2
from fastapi import Depends, status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm.session import Session
from schema.requests import UpdatePasswordRequest
from schema import requests, responses
import database.queries as db_queries
from database import models

from dependencies import dependencies as deps
import time
from loguru import logger


router = APIRouter()

@router.post('/api/account/login')
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

@router.get('/api/account/user')
async def get_user(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  return responses.User(
    id=user.id,
    username=user.username,
    server_limit=user.server_quota,
    server_count=db_queries.count_servers(db, user),
    role=user.role
  )

@router.post('/api/account/change_password')
async def change_password(
  request: UpdatePasswordRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):

  if not argon2.verify(request.current_password, user.password):
    raise InvalidCredentialsException
  
  user.password = argon2.hash(request.new_password)
  db.add(user) # user is from different db session and needs to be added to this one
  db.commit()

@router.post('/api/account/create')
async def create_account(create_req: requests.AccountCreateRequest, db: Session = Depends(deps.db)):
  
  if db_queries.get_user(db, create_req.username) != None:
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail="User already exists"
    )
  
  token = db.query(models.Invite).filter(models.Invite.token == create_req.invite_token).first()

  if not token or token.used_by != None or token.expires_at < time.time():
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail="Invite link is not valid"
    )
  
  logger.info(f"Creating new user {create_req.username} with invite token {token.token}")
  new_user = models.User(
    username=create_req.username,
    password=argon2.hash(create_req.password)
  )
  db.add(new_user)
  db.commit()
  token.used_by = new_user.id
  db.commit()