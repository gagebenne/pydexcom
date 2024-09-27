"""Errors used in `pydexcom`."""

from enum import Enum


class DexcomErrorEnum(Enum):
    """Base class for all `pydexcom` error strings."""


class AccountErrorEnum(DexcomErrorEnum):
    """`AccountError` strings."""

    FAILED_AUTHENTICATION = "Failed to authenticate"
    MAX_ATTEMPTS = "Maximum authentication attempts exceeded"


class SessionErrorEnum(DexcomErrorEnum):
    """`SessionError` strings."""

    NOT_FOUND = "Session ID not found"
    INVALID = "Session not active or timed out"


class ArgumentErrorEnum(DexcomErrorEnum):
    """`ArgumentError` strings."""

    MINUTES_INVALID = "Minutes must be and integer between 1 and 1440"
    MAX_COUNT_INVALID = "Max count must be and integer between 1 and 288"
    USERNAME_INVALID = "Username must be non-empty string"
    TOO_MANY_USER_ID_PROVIDED = "Only one of account_id, username should be provided"
    NONE_USER_ID_PROVIDED = "At least one of account_id, username should be provided"
    PASSWORD_INVALID = "Password must be non-empty string"  # noqa: S105
    ACCOUNT_ID_INVALID = "Account ID must be UUID"
    ACCOUNT_ID_DEFAULT = "Account ID default"
    SESSION_ID_INVALID = "Session ID must be UUID"
    SESSION_ID_DEFAULT = "Session ID default"
    GLUCOSE_READING_INVALID = "JSON glucose reading incorrectly formatted"


class DexcomError(Exception):
    """Base class for all `pydexcom` errors."""

    def __init__(self, enum: DexcomErrorEnum) -> None:
        """Create `DexcomError` from `DexcomErrorEnum`.

        :param enum: associated `DexcomErrorEnum`
        """
        super().__init__(enum.value)
        self._enum = enum

    @property
    def enum(self) -> DexcomErrorEnum:
        """Get `DexcomErrorEnum` associated with error.

        :return: `DexcomErrorEnum`
        """
        return self._enum


class AccountError(DexcomError):
    """Errors involving Dexcom Share API credentials."""


class SessionError(DexcomError):
    """Errors involving Dexcom Share API session."""


class ArgumentError(DexcomError):
    """Errors involving `pydexcom` arguments."""
