import logging
from typing import Iterable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi import status as http_status
from prometheus_client import Counter, start_http_server
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

logger = logging.getLogger('common.metrics')

class HTTPMetricsMiddleware(BaseHTTPMiddleware):

  def __init__(self, app, route_prefix=""):
    super().__init__(app)
    self.route_prefix = route_prefix
    self.requests_total = Counter(
      name='http_requests_count', 
      documentation='Total requests',
      labelnames=('method', 'path', 'status_code')
    )

  def _match_route(self, request: Request):  
    # default to the request path, which may contain path params (like /api/5/status)
    path = request.scope.get('path')
    # search for route without path params (like /api/{id}/status)
    for route in request.app.router.routes:
        match, scope = route.matches(request)
        if match == Match.FULL:
          path = route.path
          break
    return f"{self.route_prefix}{path}"
  
  async def dispatch(self, request: Request, call_next) -> Response:
    path = self._match_route(request)
    status_code = 500
    try:
      response = await call_next(request)
      status_code = response.status_code
      return response
    except Exception as e:
      raise e
    finally:
      self.requests_total.labels(method=request.method, path=path, status_code=status_code).inc()


def expose(app: FastAPI, path: str = '/metrics', allowed_ips: Iterable[str] = None):
  logger.info(f"Exposing metrics on {path}, allowed_ips={allowed_ips if allowed_ips is not None else '*'}")
  from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
  @app.get(path)
  async def metrics(request: Request):
    if allowed_ips is not None and request.client.host not in allowed_ips:
      raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)
    response = Response(content=generate_latest())
    response.headers["Content-Type"] = CONTENT_TYPE_LATEST
    return response


def start_server(port: int = 9090):
  start_http_server(port)