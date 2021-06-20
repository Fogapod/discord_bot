class UserFacingError(Exception):
    """
    This must be subclassed by any error that will be shown to user.

    __str__ should take care of formatting.
    """
