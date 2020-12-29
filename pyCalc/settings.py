import tempfile
from pathlib import Path

from decouple import config

LOG_FILE = config('LOG_FILE', default=None)
if LOG_FILE is None:
    temp_dir = tempfile.gettempdir()
    p = Path(temp_dir) / 'pycalc.log'
    LOG_FILE = str(p)

LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
