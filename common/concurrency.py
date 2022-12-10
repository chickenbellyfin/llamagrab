import threading

def synchronized(func):
  """ Wrap a function in a threading.Lock so it can only execute one at a time"""
  lock = threading.Lock()
  def wrapped(*args, **kwargs):
    with lock:
      func(*args, **kwargs)
  return wrapped