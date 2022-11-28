import hashlib
import json

def md5(data) -> str:
  val = json.dumps(data, sort_keys=True)
  return hashlib.md5(val.encode('utf-8')).hexdigest()
