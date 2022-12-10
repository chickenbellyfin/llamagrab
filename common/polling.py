import logging
import time
import threading
from typing import Callable

_logger = logging.getLogger("polling")

def fixed_rate(
  func: Callable, 
  interval_secs: float,
  sync: bool = False,
  logger: logging.Logger=_logger
):
  variable_rate(func, interval_secs, 0, sync=sync, logger=logger)

def variable_rate(
  func: Callable, 
  base_rate_secs: float,
  active_rate_secs: float = 0,
  active_rate_timeout_secs: float = -1,
  sync: bool = False,
  logger: logging.Logger=_logger
):
  """ Starts a function which is polled at fixed rate and returns a trigger function.
  When the trigger function is called, the polling function be called immediately and start polling at active_rate_secs.
  (subsequent calls to trigger will not call the function immediately.)
  The function will poll at the higher rate for active_rate_timeout_secs and then return to polling
  at the base_rate. Every call to the trigger function will extend the amount of time that the active_rate_secs is used.

  Patterns:
  variable_rate(f, 60, 5, 20) => once per minute. Trigger calls function every 5 seconds for the next 20 seconds
  variable_rate(f, 10, 0) => trigger calls the function exactly once
  variable_rate(f, 1, 10, 60) => poll every second, when trigger is called poll slowly for the next minute
  variable_rate(f, 30) => poll every 30 seconds, and how many ever times trigger is called

  """
  trigger_event = threading.Event()
  
  def _loop():
    is_active = False
    active_end_time = 0

    while True:
      try:
        func()
      except Exception as e:
        logger.exception(e)
      
      if is_active:
        # active state
        time.sleep(active_rate_secs) # active state does not get interrupted by the trigger
        if time.time() >= active_end_time:
          is_active = False
          trigger_event.wait(base_rate_secs - active_rate_secs)
      else:
        # inactive state
        trigger_event.wait(base_rate_secs)

      # trigger function was called
      if trigger_event.is_set():
        trigger_event.clear()
        is_active = True
        active_end_time = time.time() + active_rate_timeout_secs
  
  if sync:
    _loop()
  else:
    def _trigger():
      trigger_event.set()

    threading.Thread(target=_loop, daemon=True).start()
    return _trigger