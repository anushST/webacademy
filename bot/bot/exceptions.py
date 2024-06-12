"""Exceptions of bot package."""


class NoTokenError(Exception):
    """Raises exception when token is None."""

    pass


class NoLangChosenError(Exception):
    """Raises when languaged didn't choose."""

    pass


class BadRequestError(Exception):
    """Raises if request is bad."""

    pass


class ObjectDoesNotExistError(Exception):
    """Raises when object doesn't exist in table."""

    pass


class FieldDoesNotExistError(Exception):
    """Raises when field in database doesn't exist."""

    pass


class ValidationError(Exception):
    """Raises when validation didn't pass."""

    pass


class LangNotChosenError(Exception):
    """Raises when language not chosen."""

    pass
