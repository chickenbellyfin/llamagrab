from typing import List, Optional

from pydantic import BaseModel


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

  regions: List[Region]
  loginservers: List[Loginserver]

  class Config:
    extra = 'forbid' # don't allow unkown attributes
