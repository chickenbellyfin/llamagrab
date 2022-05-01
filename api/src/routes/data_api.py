
"""
/api/data/*

All endpoints in under the Data API are public, READ-ONLY, and don't require authentication
"""
from fastapi.routing import APIRouter

from src.dependencies import dependencies as deps

router = APIRouter()

@router.get('/data/regions')
async def get_regions():
  return deps.regions

@router.get('/status')
async def get_status():
  return