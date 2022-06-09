
"""
/api/data/*

All endpoints in under the Data API are public, READ-ONLY, and don't require authentication
"""
from fastapi.routing import APIRouter

from src.dependencies import dependencies as deps

router = APIRouter()

@router.get('/data/regions', tags=['data'])
async def get_regions():
  """ Return a list of region codes and their human-friendly names"""
  return deps.regions

@router.get('/status', tags=['data'])
async def get_status():
  """ Health check"""
  return