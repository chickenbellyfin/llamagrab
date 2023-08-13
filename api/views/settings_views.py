from sanic import Request, Sanic
from api.service.account_service import AccountService
from api.service import exceptions
from api.lib.jinja2_fragments import render
from loguru import logger

from api.views.util import if_htmx

def add_views(
  app: Sanic,
  accounts: AccountService
):

  @app.get('/settings')
  async def get_settings(request: Request):
    return await render('pages/settings.html', block=if_htmx('content'))

  @app.post('/settings/set_tribes_username')
  async def post_change_tribes_username(request: Request):
    tribes_username = request.form.get('tribes_username')
    accounts.set_tribes_username(tribes_username, request.ctx.user)
    return await render(
      'pages/settings.html',
      block='tribes_username'
    )
  
  @app.post('/settings/change_password')
  async def post_change_password(request: Request):
    current_password = request.form.get('password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_password')

    errors = {}

    if new_password == confirm_new_password:
      try:
        accounts.set_password(new_password, current_password, request.ctx.user)
      except exceptions.UnauthorizedException:
        errors['wrong_password'] = True
      except exceptions.BadArgumentsException:
        errors['invalid_new_password'] = True
    else:
      errors['not_confirmed'] = True
    logger.info(errors)
    return await render(
        'pages/settings.html', 
        block='change_password',
        context={'errors': errors}
    )
