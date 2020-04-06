"""Errors used in pydexcom"""


class DexcomError(Exception):
    """Base class for all Dexcom errors"""

    pass


class AccountError(DexcomError):
    """Raised when Dexcom Share API indicates invalid account credentials error"""

    pass


class SessionError(DexcomError):
    """Raised when Dexcom Share API / pydexcom indicates invalid session error"""

    pass


class ArguementError(DexcomError):
    """Raised when Dexcom Share API / pydexcom indicates invalid arguement error"""

    pass
