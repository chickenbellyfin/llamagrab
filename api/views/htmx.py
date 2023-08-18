import json

from sanic import Request
from sanic.response.types import HTTPResponse


def is_htmx():
  return Request.get_current().headers.get("hx-request")


def if_htmx(value):
  return value if is_htmx() else None


def toast(response: HTTPResponse, type: str, message: str):
  response.headers.add(
    "Hx-Trigger", json.dumps({"toast": {"type": type, "message": message}})
  )
