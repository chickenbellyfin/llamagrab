from sanic import Request, Sanic
from api.service.account_service import AccountService
from api.service import exceptions
from api.lib.jinja2_fragments import render
from loguru import logger
from api.schema import validations

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
      block='tribes_username',
      context={'success': True}
    )
  

  def get_change_password_errors(request: Request):
    current_password = request.form.get('password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_password')

    errors = {}

    if not validations.check_password(current_password):
      errors['invalid_current'] = True
    if not validations.check_password(new_password):
      errors['invalid_new'] = True
    if new_password != confirm_new_password:
      errors['not_confirmed'] = True
    
    return errors

  
  @app.post('/settings/validate_password_form')
  async def post_validate_pass(request: Request):
    errors = get_change_password_errors(request)
    return await render(
        'pages/settings.html', 
        block='change_password',
        context={
          'errors': errors,
          'valid': len(errors) == 0
        }
    )

  
  @app.post('/settings/change_password')
  async def post_change_password(request: Request):
    current_password = request.form.get('password')
    new_password = request.form.get('new_password')

    errors = get_change_password_errors(request)

    try:
      accounts.set_password(new_password, current_password, request.ctx.user)
    except exceptions.UnauthorizedException:
      errors['wrong_password'] = True
    except exceptions.BadArgumentsException:
      errors['invalid_new'] = True

    if len(errors) == 0:
      request.form.clear()

    return await render(
      'pages/settings.html', 
      block='change_password',
      context={
        'errors': errors,
        'success': len(errors) == 0
      }
    )
