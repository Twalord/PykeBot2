

class TokenLoadingError(Exception):
    """
    :description: Raised when load_token is unable to load a token
    """
    pass


class MainCommandTypeError(Exception):
    """
    :description: Raised when trying to assign a non-existent main command type.
    """
    pass


class SubCommandTypeError(Exception):
    """
    :description: Raised when trying to assign a non-existent sub command type.
    """
    pass
