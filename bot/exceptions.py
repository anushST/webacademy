"""Bot exceptions."""


class NoTokenError(Exception):
    """Raises exception when token is None."""

    pass


class NoLangChosenError(Exception):
    """Raises when languaged didn't chose."""

    pass


class BadRequestError(Exception):
    """Raises if request is bad."""

    pass
