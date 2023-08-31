from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic
from wtforms import Form, StringField, ValidationError, validators

from api.service import exceptions
from api.service.account_service import AccountService
from api.views.htmx import if_htmx


class ChangePasswordForm(Form):
  password = StringField(default='')
  new_password = StringField(default='', validators=[validators.Length(min=8, max=32)])
  confirm_password = StringField(default='')

  def validate_confirm_password(self, field):
    if self.password.data != self.confirm_password.data:
      raise ValidationError('Must match the password.')

def add_views(app: Sanic, accounts: AccountService, **kwargs):

  @app.get('/settings')
  async def get_settings(request: Request):
    return await render('pages/settings.html', block=if_htmx('content'), context={'form': ChangePasswordForm()})

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
    should_submit = not request.args.get('validate_only') == 'true'
    form = ChangePasswordForm(request.form)
    valid = form.validate()
    changed = False
    if valid and should_submit:
      try:
        accounts.set_password(form.password.data, form.new_password.data, request.ctx.user)
        changed = True
        form = ChangePasswordForm() # Clear the form
      except exceptions.UnauthorizedException:
        form.password.errors.append('Incorrect password')
      except:
        pass

    return await render(
      'pages/settings.html', 
      block='change_password',
      context={
        'form': form,
        'valid': valid,
        'changed': changed
      }
    )
