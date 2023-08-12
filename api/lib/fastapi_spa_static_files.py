# https://stackoverflow.com/a/68363904
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


class SPAStaticFiles(StaticFiles):
  async def get_response(self, path: str, scope):
    is_index = False
    if path == '.' or path == 'index.html':
      is_index = True
    try:
      response = await super().get_response(path, scope)
    except StarletteHTTPException as ex:
      if ex.status_code == 404:
        is_index = True
        response = await super().get_response('.', scope)
      else:
        raise ex

    # for SPAs, index should never be cached
    if is_index:
      response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response