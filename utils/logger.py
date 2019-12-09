import logging
import logging.config
import pathlib
import time
import os


def setup_logger(console_level=logging.INFO, log_file_level=logging.DEBUG, logs_to_keep=20, create_log_files=True, path_to_logs=None):
    """
    Sets up a logger with formatting, log file creation, settable console and log file logging levels as well as automatic deletion of old log files.
    :param console_level: logging level on console, standard is INFO
    :type console_level: logging level
    :param log_file_level: logging level in log file, standard is DEBUG
    :type log_file_level: logging level
    :param logs_to_keep: number of log files to keep before deleting the oldest one, standard is 20
    :type logs_to_keep: int
    :param create_log_files: Whether to create log files or only log to console
    :type create_log_files: bool
    :param path_to_logs: path to the directory for saving the logs, standard is current working directory / logs
    :type path_to_logs: pathlib.PATH
    :return: None, but the logger may now be accessed via logging.getLogger('pb_logger')
    :rtype: None
    """

    # assert preconditions
    logging_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    assert console_level in logging_levels
    assert log_file_level in logging_levels
    assert isinstance(logs_to_keep, int)
    assert isinstance(create_log_files, bool)
    assert isinstance(path_to_logs, pathlib.Path) or path_to_logs is None

    if path_to_logs is None:
        path_to_logs = pathlib.Path.cwd() / "logs"

    assert os.access(path_to_logs, os.W_OK)
    assert not logging.getLogger('pb_logger').hasHandlers()

    # create logger
    pb_logger = logging.getLogger('pb_logger')
    pb_logger.setLevel(logging.DEBUG)

    # if create_log_files is True, check for logs folder or make one
    if create_log_files:
        if not ((path_to_logs.exists()) and path_to_logs.is_dir()):
            path_to_logs.mkdir()

        # check if old logs need to be deleted
        if not logs_to_keep < 0:
            if len(list((path_to_logs.glob('*.log')))) > logs_to_keep:
                delete_oldest_log(path_to_logs)

        # create file handler
        time_str = time.strftime("%d-%m-%Y_%H-%M-%S")
        log_file_name = f"log_{time_str}.log"
        fh = logging.FileHandler(str(path_to_logs / log_file_name))
        fh.setLevel(log_file_level)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s')
    if create_log_files:
        fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add handlers to logger
    pb_logger.addHandler(fh)
    pb_logger.addHandler(ch)

    pb_logger.info("Finished setting up PykeBot logger")


def delete_oldest_log(path_to_logs):
    """
    Finds and deletes the oldest .log file in the given file path
    :param path_to_logs: file path to the log folder
    :type path_to_logs: pathlib.PATH
    :return: None
    :rtype: None
    """

    # assert preconditions
    assert path_to_logs.exists()
    assert path_to_logs.is_dir()
    assert len(list(path_to_logs.glob('*.log'))) > 0
    assert os.access(path_to_logs, os.W_OK)

    # find oldest log
    mtime, file_path = min((f.stat().st_mtime, f) for f in path_to_logs.glob('*.log'))
    pathlib.Path.unlink(file_path)
    return
