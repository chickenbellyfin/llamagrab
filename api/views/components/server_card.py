from sanic import Request, Sanic
from api.lib.jinja2_fragments import render

from api.service.server_service import ServerService
from api.views.htmx import toast


def add_views(app: Sanic, servers: ServerService, **kwargs):
  
  async def _server_action(request: Request, func, toast_message_format: str):
    server_id = int(request.form.get('id'))
    is_admin = request.form.get("is_admin").lower() == 'true'
    func(server_id, request.ctx.user)
    server = servers.get_server_status(servers.get_server(server_id, request.ctx.user))
    res = await render("components/server_card.html", context={'server': server, 'is_admin': is_admin})
    toast(res, message=toast_message_format % server.name)
    return res

  @app.post('/components/server_card/start')
  async def start_server(request: Request):
    return await _server_action(request, servers.start_server, 'Started %s')
  
  @app.post('/components/server_card/stop')
  async def stop_server(request: Request):
    return await _server_action(request, servers.stop_server, 'Stopped %s')

  @app.post('/components/server_card/restart')
  async def restart_server(request: Request):
    return await _server_action(request, servers.restart_server, 'Restarting %s')
  