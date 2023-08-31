from datetime import datetime
from typing import Union

from dateutil import parser
from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic

from api.audit import AuditLog
from api.views.htmx import if_htmx


def format_date(date: Union[str, datetime]) -> str:
  if type(date) == str:
    date = parser.parse(date)
  return date.strftime("%a %b %d %Y %H:%M:%S %p")


def add_views(app: Sanic, audit: AuditLog, **kwargs):

  @app.get("/admin/audit")
  async def get_audit_log(request: Request):
    audit_log = audit.get()
    for item in audit_log:
      item.formatted_date = format_date(datetime.fromtimestamp(item.timestamp))
    audit_log.sort(key=lambda i: i.timestamp, reverse=True)
    return await render("pages/admin/audit.html", context={"audit_log": audit_log}, block=if_htmx('content'))
