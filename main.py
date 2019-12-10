from utils import pb_logger
from logging import getLogger

pb_logger.setup_logger()
logger = getLogger('pb_logger')
logger.info("Logger works")
