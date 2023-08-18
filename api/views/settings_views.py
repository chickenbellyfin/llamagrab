from loguru import logger
from sanic import Request, Sanic

from api.lib.jinja2_fragments import render
from api.schema import validations
from api.service import exceptions
from api.service.account_service import AccountService
from api.views.htmx import if_htmx


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
      block='tribes_username',
      context={'success': True}
    )
  
  @app.post('/settings/change_password')
  async def post_change_password(request: Request):
    current_password = request.form.get('password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_password')
    should_submit = not request.args.get('validate_only') == 'true'

    errors = set()

    if not validations.check_password(current_password):
      errors.add('invalid_current')
    if not validations.check_password(new_password):
      errors.add('invalid_new')
    if new_password != confirm_new_password:
      errors.add('not_confirmed')

    success = False
    if len(errors) == 0 and should_submit:
      try:
        accounts.set_password(new_password, current_password, request.ctx.user)
        request.form.clear()
        success = True
      except exceptions.UnauthorizedException:
        errors.add('wrong_password')
      except exceptions.BadArgumentsException:
        errors.add('invalid_new')

    return await render(
      'pages/settings.html', 
      block='change_password',
      context={
        'errors': errors,
        'valid': len(errors) == 0,
        'success': success
      }
    )
