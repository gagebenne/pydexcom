"""Errors used in pydexcom."""


class DexcomError(Exception):
    """Base class for all Dexcom errors."""

    pass


class AccountError(DexcomError):
    """Errors involving Dexcom Share API credentials."""

    pass


class SessionError(DexcomError):
    """Errors involving Dexcom Share API session."""

    pass


class ArguementError(DexcomError):
    """Error involving arguements."""

    pass
