from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic, response
from wtforms import Form, StringField, ValidationError, validators

from api.auth import Auth
from api.schema.app_config import AppConfig
from api.service import exceptions
from api.service.account_service import AccountService
from api.views.htmx import if_htmx


class SignupForm(Form):
  username = StringField(default='', validators=[validators.Length(min=4, max=20), validators.Regexp('^[a-zA-Z0-9_]+$')])
  password = StringField(default='', validators=[validators.Length(min=8, max=32)])
  confirm_password = StringField(default='')

  def __init__(self, accounts: AccountService, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.accounts = accounts

  def validate_username(self, field):
    if self.accounts.username_exists(self.username.data):
      raise ValidationError('Username is already taken')

  def validate_confirm_password(self, field):
    if self.password.data != self.confirm_password.data:
      raise ValidationError('Must match the password.')


def add_views(app: Sanic, auth: Auth, accounts: AccountService, config: AppConfig, **kwargs):
  @app.on_request
  async def extract_auth(request: Request):
    token = request.cookies.get('llamagrab_token')
    try:
      user = await auth.login_manager.get_current_user(token)
    except Exception as e:
      logger.error(e)
      user = None
    request.ctx.user = user
  
  @app.get('/login')
  async def get_login(request: Request):
    return await render('pages/login.html', block=if_htmx('content'))
  
  @app.post('/login')
  async def post_login(request: Request):
    username = request.form.get('username')
    password = request.form.get('password')
    try:
      token = accounts.create_auth_token(username, password)
    except exceptions.UnauthorizedException:
      return await render('pages/login.html', context={'unauthorized': True})
    
    res = response.redirect('/')
    res.add_cookie(key='llamagrab_token', value=token, secure=config.secure_cookie)
    return res
  
  @app.get('/signup')
  async def get_signup(request: Request):
    return await render('pages/signup.html', block=if_htmx('content'), context={'form':SignupForm(accounts)})
  
  @app.post('/signup')
  async def post_signup(request: Request):
    should_submit = not request.args.get('validate_only') == 'true'
    form = SignupForm(accounts, request.form)
    valid = form.validate()

    if valid and should_submit:
      try:
        accounts.create_account(form.username.data, form.password.data, request.client_ip)
        return response.redirect('/login?newaccount=true')
      except Exception as e:
        logger.error(f'{e}')   
    return await render('pages/signup.html', block='content', context={'form': form, 'valid': valid})

  
  @app.post('/logout')
  async def post_logout(request: Request):
    res = response.redirect('/')
    #res.delete_cookie('llamagrab_token') # TODO figure out why this doesn't work when secure_cookie=False
    res.add_cookie('llamagrab_token', '', secure=config.secure_cookie)
    return res