import logging
import tempfile
from pathlib import Path

from decouple import config

LOG_FILE = config('LOG_FILE', default=None)
if LOG_FILE is None:
    temp_dir = tempfile.gettempdir()
    p = Path(temp_dir) / 'pycalc.log'
    LOG_FILE = str(p)

log_level = config('LOG_LEVEL', default='info')
try:
    log_level = log_level.upper()
    logging._checkLevel(log_level)
except ValueError:
    log_level = 'INFO'

LOG_LEVEl = log_level
LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
