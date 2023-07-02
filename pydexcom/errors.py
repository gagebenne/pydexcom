"""Errors used in pydexcom."""


from enum import Enum


class DexcomError(Exception):
    """Base class for all Dexcom errors."""

    pass


class AccountError(DexcomError):
    """Errors involving Dexcom Share API credentials."""

    pass


class AccountErrorEnum(DexcomError):
    """Dexcom AccountError strings."""

    USERNAME_NULL_EMPTY = "Username null or empty"
    PASSWORD_NULL_EMPTY = "Password null or empty"
    ACCOUNT_ID_NULL_EMPTY = "Account ID null or empty"
    ACCOUNT_ID_DEFAULT = "Account ID default"
    ACCOUNT_NOT_FOUND = "Account not found"
    PASSWORD_INVALID = "Password not valid"
    MAX_ATTEMPTS = "Maximum authentication attempts exceeded"


class SessionError(DexcomError):
    """Errors involving Dexcom Share API session."""

    pass


# Dexcom SessionError strings
class SessionErrorEnum(Enum):
    """Dexcom SessionError strings."""

    NULL = "Session ID null"
    DEFAULT = "Session ID default"
    NOT_VALID = "Session ID not valid"
    NOT_FOUND = "Session ID not found"


class ArgumentError(DexcomError):
    """Error involving arguments."""

    pass


class ArgumentErrorEnum(Enum):
    """Dexcom ArgumentError strings."""

    MINUTES_INVALID = "Minutes must be between 1 and 1440"
    MAX_COUNT_INVALID = "Max count must be between 1 and 288"
    SERIAL_NUMBER_NULL_EMPTY = "Serial number null or empty"
