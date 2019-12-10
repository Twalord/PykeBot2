from utils import pb_logger
import logging

pb_logger.setup_logger()
logger = logging.getLogger('pb_logger')
logger.info("Logger works")
