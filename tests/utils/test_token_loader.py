from utils import token_loader
import logging
import pathlib
import pytest
from models.errors import TokenLoadingError
import os


def test_load_token():
    token_value = "test"
    tmp_token_path = pathlib.Path.cwd()
    try:
        tmp_token = open(str(tmp_token_path / "tmp"), "w")
        tmp_token.write(token_value)
        tmp_token.close()
        logger = logging.getLogger("pb_logger")

        # test whether test token is correct
        loaded_token = token_loader.load_token("tmp", path_to_token=tmp_token_path)
        assert loaded_token == token_value

    # test whether loading the wrong token fails
        with pytest.raises(TokenLoadingError):
            token_loader.load_token("test", try_env=False, path_to_token=tmp_token_path)

    finally:
        pathlib.Path.unlink(tmp_token_path / "tmp")

    try:
        # test whether loading from environment works
        os.environ["token"] = token_value
        token_loader.load_token("token", path_to_token=tmp_token_path)

    finally:
        # reset token env var
        os.environ["token"] = ""
