from typing import Dict, List, Optional

from pydantic import BaseModel, validator


class Region(BaseModel):
  key: str
  name: str
  host: str
  token: str
  enabled: bool = True

class Loginserver(BaseModel):
  name: str
  url: str

class AppConfig(BaseModel):
  login_secret: str
  serve_static: Optional[str]
  base_path: Optional[str] = 'data/api'
  port: int = 8000

  status_polling_rate_secs: int = 60
  host_manager_port: int = 8999

  # in yaml, it should be a list of Region
  regions: Dict[str, Region]
  loginservers: List[Loginserver]

  allowed_metrics_ips: Optional[List[str]]

  @validator('regions', pre=True)
  def regions_to_dict(cls, raw: List[Region]) -> Dict[str, Region]:
    return {
      region['key']: region for region in raw
    }

  class Config:
    extra = 'forbid' # don't allow unkown attributes
