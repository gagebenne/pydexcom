"""Errors used in `pydexcom`."""


from enum import Enum


class DexcomErrorEnum(Enum):
    """Base class for all `pydexcom` error strings."""

    pass


class AccountErrorEnum(DexcomErrorEnum):
    """`AccountError` strings."""

    ACCOUNT_NOT_FOUND = "Account not found"
    PASSWORD_INVALID = "Password not valid"
    MAX_ATTEMPTS = "Maximum authentication attempts exceeded"


class SessionErrorEnum(DexcomErrorEnum):
    """`SessionError` strings."""

    NOT_FOUND = "Session ID not found"


class ArgumentErrorEnum(DexcomErrorEnum):
    """`ArgumentError` strings."""

    MINUTES_INVALID = "Minutes must be and integer between 1 and 1440"
    MAX_COUNT_INVALID = "Max count must be and integer between 1 and 288"
    USERNAME_INVALID = "Username must be non-empty string"
    PASSWORD_INVALID = "Password must be non-empty string"
    ACCOUNT_ID_INVALID = "Account ID must be UUID"
    ACCOUNT_ID_DEFAULT = "Account ID default"
    SESSION_ID_INVALID = "Session ID must be UUID"
    SESSION_ID_DEFAULT = "Session ID default"
    GLUCOSE_READING_INVALID = "JSON glucose reading incorrectly formatted"


class DexcomError(Exception):
    """Base class for all `pydexcom` errors."""

    def __init__(self, enum: DexcomErrorEnum):
        """Create `DexcomError` from `DexcomErrorEnum`.

        :param enum: associated `DexcomErrorEnum`
        """
        super().__init__(enum.value)
        self._enum = enum

    @property
    def enum(self) -> DexcomErrorEnum:
        """Get `DexcomErrorEnum` associated with error.

        :return: `DexcomErrorEnum`"""
        return self._enum


class AccountError(DexcomError):
    """Errors involving Dexcom Share API credentials."""

    pass


class SessionError(DexcomError):
    """Errors involving Dexcom Share API session."""

    pass


class ArgumentError(DexcomError):
    """Errors involving `pydexcom` arguments."""

    pass
    pass
