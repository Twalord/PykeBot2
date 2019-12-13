from utils import pb_logger
import pathlib
import pytest
import logging


def test_setup_logger():

    def release_file(logger_name: str) -> None:
        test_logger = logging.getLogger(logger_name)
        for handler in test_logger.handlers:
            test_logger.removeHandler(handler)

    tmpdir = pathlib.Path.cwd() / "tmpdir"

    # clean up from last test
    if tmpdir.exists():
        for child in tmpdir.glob('*'):
            child.unlink()
        pathlib.Path.rmdir(tmpdir)

    try:
        # test with not existing folder
        pb_logger.setup_logger(logger_name="test1", path_to_logs=tmpdir)
        assert len(list(tmpdir.iterdir())) > 0

        # remove handlers including file handler to release file
        release_file("test1")

    finally:
        if tmpdir.exists():
            for child in tmpdir.glob('*'):
                child.unlink()
            pathlib.Path.rmdir(tmpdir)

    # create folder for next test
    tmpdir.mkdir()

    try:
        # test whether really no log file is created
        pb_logger.setup_logger(logger_name="test2", create_log_files=False, path_to_logs=tmpdir)
        assert len(list(tmpdir.iterdir())) == 0

        # test whether log files are created when folder already exists
        pb_logger.setup_logger(logger_name="test3", path_to_logs=tmpdir)
        assert len(list(tmpdir.iterdir())) > 0

        # remove handlers including file handler to release file
        release_file("test3")

        # test whether recreating the same logger profile raises an assertion
        with pytest.raises(AssertionError):
            pb_logger.setup_logger(logger_name="test1", create_log_files=False)

    finally:
        # remove folder to clean up
        if tmpdir.exists():
            for child in tmpdir.glob('*'):
                child.unlink()
            pathlib.Path.rmdir(tmpdir)
