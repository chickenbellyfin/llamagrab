from sanic import Request, Sanic
from api.lib.jinja2_fragments import render

from api.service.server_service import ServerService
from api.views.htmx import toast


def add_views(app: Sanic, servers: ServerService, **kwargs):
  
  @app.post('/components/server_card/start')
  async def start_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.start_server(server_id, request.ctx.user)
    server = servers.get_server_status(servers.get_server(server_id, request.ctx.user))
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Started {server.name}')
    return res
  
  @app.post('/components/server_card/stop')
  async def stop_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.stop_server(server_id, request.ctx.user)
    server = servers.get_server_status(servers.get_server(server_id, request.ctx.user))
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Stopped {server.name}')
    return res
  
  @app.post('/components/server_card/restart')
  async def restart_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.restart_server(server_id, request.ctx.user)
    server = servers.get_server_status(servers.get_server(server_id, request.ctx.user))
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Restarting {server.name}')
    return res