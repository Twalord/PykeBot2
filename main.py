"""
Main file used to start PykeBot2.

:author: Jonathan Decker
"""

from utils import pb_logger
import logging
from event_loop_master import run_main_loop

pb_logger.setup_logger(console_level=logging.DEBUG)
logger = logging.getLogger('pb_logger')
logger.info("Logger is running")

run_main_loop()
