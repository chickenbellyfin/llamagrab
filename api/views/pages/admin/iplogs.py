from loguru import logger
from sanic import Request, Sanic
from api.iplog import IPLogDatabase

from api.lib.jinja2_fragments import render
from api.views.htmx import if_htmx
from api.views.util import format_date
import time

TWO_WEEKS = 2 * 7 * 24 * 60 * 60

def add_views(app: Sanic, ip_log_db: IPLogDatabase, **kwargs):
  @app.get("/admin/iplogs")
  async def get_iplogs(request: Request):
    iplogs = ip_log_db.get(request.ctx.user, since_ms=(time.time() - TWO_WEEKS) * 1000)
    iplogs.sort(key=lambda t: t.timestamp, reverse=True)
    for entry in iplogs:
      entry.formatted_date = format_date(entry.timestamp/1000)

    return await render(
      "pages/admin/iplogs.html", 
      block=if_htmx('content'), 
      context={'iplogs': iplogs}
    )

