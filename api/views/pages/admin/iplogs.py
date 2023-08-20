from loguru import logger
from sanic import Request, Sanic

from api.lib.jinja2_fragments import render
from api.views.htmx import if_htmx


def add_views(app: Sanic, **kwargs):
  @app.get("/admin/iplogs")
  async def get_iplogs(request: Request):
    return await render("pages/admin/iplogs.html", block=if_htmx('content'))

