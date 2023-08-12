

from loguru import logger
from sanic import Request, Sanic, response
from sanic_ext import render

from api.auth import Auth
from api.service.account_service import AccountService
from api.service import exceptions


def add_views(
    app: Sanic,
    auth: Auth,
    accounts: AccountService,
    secure_cookie=True,
):
  @app.on_request
  async def extract_auth(request: Request):
    token = request.cookies.get('llamagrab_token')
    try:
      user = await auth.login_manager.get_current_user(token)
    except Exception as e:
      print(e)
      user = None
    request.ctx.user = user
  
  @app.get('/login')
  async def get_login(request: Request):
    return await render('pages/login.html')
  
  @app.post('/login')
  async def post_login(request: Request):
    # res = response.redirect('/')
    username = request.form.get('username')
    password = request.form.get('password')
    try:
      token = accounts.create_auth_token(username, password)
    except exceptions.UnauthorizedException:
      return await render('login.html', context={'unauthorized': True})
    
    res = response.redirect('/')
    res.add_cookie(key='llamagrab_token', value=token, secure=secure_cookie)
    return res
  
  @app.get('/signup')
  async def get_signup(request: Request):
    return await render('pages/signup.html')
  
  @app.post('/logout')
  async def post_logout(request: Request):
    res = response.redirect('/')
    res.cookies.delete_cookie('llamagrab_token')
    return res