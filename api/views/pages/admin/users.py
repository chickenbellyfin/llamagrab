from loguru import logger
from sanic import Request, Sanic
from api.lib.jinja2_fragments import render

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
