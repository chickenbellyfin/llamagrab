from loguru import logger
from sanic import Request, Sanic

from api.lib.jinja2_fragments import render
from api.service.server_service import ServerService
from api.views.htmx import if_htmx, is_htmx


def add_views(app: Sanic, servers: ServerService, **kwargs):
  @app.get("/admin/servers")
  async def get_servers(request: Request):
    all_servers = servers.get_server_status(servers.get_all_servers())
    return await render(
      "pages/admin/servers.html",
      block=if_htmx('content'),
      context={ "servers": all_servers }
    )

  @app.get("/admin/servers/server_card")
  async def get_server_card_modal(request: Request):
    server = servers.get_server_status(servers.get_server(
      server_id=int(request.headers.get('hx-trigger')),
      user=request.ctx.user
    ))
    return await render(
      "components/server_card_modal.html", 
      context={'server': server, 'admin_mode': True}
    )
