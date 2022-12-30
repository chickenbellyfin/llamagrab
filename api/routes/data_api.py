
"""
/api/data/*

All endpoints in under the Data API are public, READ-ONLY, and don't require authentication
"""
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

from api.schema.app_config import Loginserver, Region


class RegionListResponse(BaseModel):
  __root__: Dict[str, str]
  class Config:
    schema_extra = {
      'example': {
          'region_code_1': 'Region Name 1',
          'region_code_2': 'Region Name 2',
      }
    }

def add_routes(
  app: FastAPI,
  regions: Dict[str, Region],
  loginservers: List[Loginserver]
):


  @app.get('/data/regions', tags=['data'], response_model=RegionListResponse)
  async def get_regions() -> RegionListResponse:
    """ Return a list of region codes and their human-friendly names"""
    return {
      region.key: region.name
      for region in regions.values()
    }

  @app.get('/data/loginservers', tags=['data'])
  async def get_loginservers():
    """ Return a list of allowed loginservers"""
    return loginservers


  @app.get('/status', tags=['data'])
  async def get_status() -> str:
    """ Health check. Responds with `"ok"` if the service is healthy"""
    return "ok"

