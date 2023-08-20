from loguru import logger
from sanic import Request, Sanic

from api.lib.jinja2_fragments import render
from api.service.server_service import ServerService
from api.views.htmx import if_htmx


def add_views(app: Sanic, servers: ServerService, **kwargs):
  @app.get("/admin/servers")
  async def get_servers(request: Request):
    all_servers = servers.get_server_status(servers.get_all_servers())
    return await render(
      "pages/admin/servers.html",
      block=if_htmx('content'),
      context={"servers": all_servers}
    )
