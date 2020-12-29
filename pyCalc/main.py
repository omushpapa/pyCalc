#! /usr/bin/env python3
import logging

import settings
from gui import TkGUI

logging.basicConfig(handlers=[logging.FileHandler(settings.LOG_FILE)],
                    format=settings.LOG_FORMAT,
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.info(f'initialising')

app = TkGUI()
app.run()
