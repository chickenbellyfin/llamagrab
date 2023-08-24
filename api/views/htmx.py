import json

from sanic import Request
from sanic.response.types import HTTPResponse


def is_htmx():
  return Request.get_current().headers.get("hx-request")


def if_htmx(value):
  return value if is_htmx() else None


def toast(response: HTTPResponse, is_success: bool = True, message: str = None):
  toast_type = 'success' if is_success else 'error'
  if not message:
    message = 'Success!' if is_success else 'Error!'
  response.headers.add(
    "Hx-Trigger", json.dumps({"toast": {"type": toast_type, "message": message}})
  )

