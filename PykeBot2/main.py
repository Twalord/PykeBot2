"""
Main file used to start PykeBot2.

:author: Jonathan Decker
"""

from PykeBot2.utils import pb_logger
import logging
from PykeBot2.event_loop_master import run_main_loop


def start():
    pb_logger.setup_logger(console_level=logging.DEBUG)
    logger = logging.getLogger("pb_logger")
    logger.info("Logger is running")

    run_main_loop()


if __name__ == "__main__":
    start()
