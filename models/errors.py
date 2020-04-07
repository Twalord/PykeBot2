

class TokenLoadingError(Exception):
    """
    :description: Raised when load_token is unable to load a token
    """
    pass


class NotFoundResponseError(Exception):
    """
    :description: Raised when stalker gets Error Code 404 Not found for a request
    """
    pass


class ServerErrorResponseError(Exception):
    """
    :description: Raised when a stalker gets Error Code 5xx for a request
    """
    pass


class InvalidForwardToError(Exception):
    """
    :description: Raised when the forward_to of a query could not be matched
    """
    pass


class InvalidNextStepError(Exception):
    """
    :description: Raised when the next_step of a query could not be matched
    """
    pass


class PayloadCreationError(Exception):
    """
    :description: Raised when attempting to create a payload object and not a subclass
    """
    pass
