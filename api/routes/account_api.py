"""
/api/account/*
Enpoints in the Account API are for login & user account management.
"""
from typing import List

from fastapi import Depends, FastAPI, Request

from api.auth import Auth
from api.database import models
from api.schema import requests, responses
from api.schema.requests import UpdatePasswordRequest
from api.service.account_service import AccountService
from api.service.server_service import ServerService


def add_routes(
  app: FastAPI,
  auth: Auth,
  accounts: AccountService,
  servers: ServerService
):

  def _to_account_response(user: models.User):
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
        server_count=len(servers.get_owned_servers(user))
      ),
      tribes_username=user.tribes_username
    )


  @app.post('/account/login', tags=['account'])
  async def login(login: requests.LoginRequest):
    """ Login to an account. Returns an access_token which must be included in the authorization
        header for most requests.
        Header is 'Authorization': 'Bearer $access_token'
    """
    access_token = accounts.create_auth_token(login.username, login.password)
    return {
      'access_token': access_token
    }


  @app.get('/account/user', tags=['account'])
  async def get_user(
    user: models.User = Depends(auth.login)):
    """ Get the currently logged in user"""
    # server_count = len(servers.get_owned_servers(user))
    # db_user = db.query(models.User).filter_by(id=user.id).first()
    return _to_account_response(user)


  @app.get('/accounts', include_in_schema=False)
  async def list_accounts(
    user: models.User = Depends(auth.login_admin)) -> List[responses.UserAccount]:
    """Get all user accounts with roles & limits. For admin panel use"""
    return [
      _to_account_response(u)
      for u in accounts.all()
    ]

  @app.get('/users', tags=['account'])
  async def list_users(
    user: models.User = Depends(auth.login)
  ) -> List[responses.User]:
    """Get all usernames & ids"""
    return [
      responses.User(id=u.id, username=u.username)
      for u in accounts.all()
    ]

  @app.post('/account/change_password', tags=['account'])
  async def change_password(
    request: UpdatePasswordRequest,
    user: models.User = Depends(auth.login)):
    """ Changes the account password. Must be logged in"""
    accounts.set_password(request.new_password, request.current_password, user)

  @app.post('/account/set_tribes_name', tags=['account'])
  async def set_tribes_name(
    request: requests.SetTribesUsernameRequest,
    user: models.User = Depends(auth.login)
  ):
    accounts.set_tribes_username(request.tribes_username, user)


  def _get_ip(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

  @app.post('/account/create', include_in_schema=False)
  async def create_account(create_req: requests.AccountCreateRequest, request: Request):
    accounts.create_account(create_req.username, create_req.password, _get_ip(request))


  @app.delete('/account/{user_id_to_delete}', include_in_schema=False)
  async def delete_user(user_id_to_delete: int, user: models.User = Depends(auth.login_super)):
    accounts.delete(user_id_to_delete, user)
  