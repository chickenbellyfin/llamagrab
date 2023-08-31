from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic

from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views.htmx import if_htmx


def add_views(app: Sanic, accounts: AccountService, servers: ServerService, **kwargs):
  @app.get("/admin/users")
  async def get_users(request: Request):
    all_users = []
    for user in accounts.all():
      user.server_count = len(servers.get_owned_servers(user))
      all_users.append(user)

    return await render(
      "pages/admin/users.html", 
      context={"accounts": all_users},
      block=if_htmx('content')
    )

  async def user_card_modal(user_id: int):
    return await render(
      "components/user_card_modal.html", 
      context={'user':accounts.get(user_id)}
    )
  
  @app.get('/admin/users/user_card')
  async def get_user_card_modal(request: Request):
    return await user_card_modal(int(request.headers.get('hx-trigger')))

  @app.post('/admin/users/user_card/verify')
  async def post_verify_user(request: Request):
    id = int(request.form.get('id'))
    accounts.verify_user(id, request.ctx.user)
    return await user_card_modal(id)

  @app.post('/admin/users/user_card/make_admin')
  async def post_make_admin(request: Request):
    id = int(request.form.get('id'))
    accounts.make_admin(id, request.ctx.user)
    return await user_card_modal(id)

  @app.post('/admin/users/user_card/remove_admin')
  async def post_remove_admin(request: Request):
    id = int(request.form.get('id'))
    accounts.make_not_admin(id, request.ctx.user)
    return await user_card_modal(id)
