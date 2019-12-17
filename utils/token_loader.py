from logging import getLogger
import pathlib
import os

from models.errors import TokenLoadingError

logger = getLogger('pb_logger')


def load_token(name: str, try_env: bool = True, hide_token: bool = True, path_to_token: pathlib.Path = None) -> str:
    """
    :description: Loads the specified token, trying either the given path or the cwd and if set the env variables
    :param name: Name of the token, as in the file_name or the name of the env variable
    :type name: str
    :param try_env: Sets whether environmental variables should be checked if the token is not in the given path, standard is True
    :type try_env: bool
    :param hide_token: Sets whether the token should be hidden from logging, standard is True
    :type hide_token: bool
    :param path_to_token: Path to the folder containing the token, should not include the token itself, standard is the cwd
    :type path_to_token: pathlib.Path
    :return: The token as in the first line of the token file or the value of the env variable of the same name
    :rtype: str
    :raises: TokenLoadingError
    """

    # assert preconditions
    assert isinstance(name, str)
    assert isinstance(try_env, bool)
    assert isinstance(hide_token, bool)
    assert isinstance(path_to_token, pathlib.Path) or path_to_token is None

    if path_to_token is None:
        total_path_to_token = pathlib.Path.cwd() / name
    else:
        total_path_to_token = path_to_token / name

    logger.info(f"Trying to load token {name}")

    # try loading token from file
    token = ""
    token_found = False
    try:
        with total_path_to_token.open() as file:
            token = file.readline()
    except FileNotFoundError:
        logger.info(f"Token {name} not found in {path_to_token}")
    except PermissionError:
        logger.info(f"Permissions missing for reading token {name} in {path_to_token}")

    if len(token) > 0:
        token_found = True

    # if token wasn't found and try_env is true, try loading from env
    if try_env and not token_found:
        logger.info(f"Trying to load token {name} from env")
        try:
            token = os.environ[name]
        except KeyError:
            logger.info(f"Token {name} not found in env")

    if len(token) > 0:
        token_found = True

    if token_found:
        # only prints token to console if hide token is not true
        if not hide_token:
            logger.info(f"Loaded Token {name}:")
            logger.info(f"{token}")
        return token
    else:
        # if the token couldn't be loaded, a TokenLoadingError is raised
        logger.error(f"Failed to load token {name}")
        logger.warning(f"Token needs to be placed in {total_path_to_token} or set as an environmental variable of the "
                       f"same name")
        raise TokenLoadingError(f"Failed to load token {name}")
