import threading
import time
from typing import Callable

from loguru import logger


def synchronized(func):
  """ Wrap a function in a threading.Lock so it can only execute one at a time"""
  lock = threading.Lock()
  def wrapped(*args, **kwargs):
    with lock:
      func(*args, **kwargs)
  return wrapped


def start_polling(func: Callable, interval_secs: int):
  """ Start a daemon thread to call a function at a specified rate"""
  def _loop():
    while True:
      try:
        func()
      except Exception as e:
        logger.exception(e)
      finally:
        time.sleep(interval_secs)

    
  threading.Thread(target=_loop, daemon=True).start()


