from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class NotFoundException(Exception):
  pass

class PermissionsException(Exception):
  pass

class BadArgumentsException(Exception):
  pass

class LimitException(Exception):
  pass

class UnauthorizedException(Exception):
  pass


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    def _json(self, e: Exception, code: int):
      return JSONResponse({'detail': str(e)}, status_code=code)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except NotFoundException as e:
          return self._json(e, status.HTTP_404_NOT_FOUND)
        except PermissionsException as e:
          return self._json(e, status.HTTP_403_FORBIDDEN)
        except BadArgumentsException as e:
          return self._json(e, status.HTTP_400_BAD_REQUEST)
        except LimitException as e:
          return self._json(e, status.HTTP_429_TOO_MANY_REQUESTS)
        except UnauthorizedException as e:
          return self._json(e, status.HTTP_401_UNAUTHORIZED)
