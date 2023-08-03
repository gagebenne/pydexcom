"""Errors used in pydexcom."""


from enum import Enum
from typing import Union


class AccountErrorEnum(Enum):
    """Dexcom AccountError strings."""

    ACCOUNT_NOT_FOUND = "Account not found"
    PASSWORD_INVALID = "Password not valid"
    MAX_ATTEMPTS = "Maximum authentication attempts exceeded"


class SessionErrorEnum(Enum):
    """Dexcom SessionError strings."""

    NULL = "Session ID null"
    DEFAULT = "Session ID default"
    NOT_VALID = "Session ID not valid"
    NOT_FOUND = "Session ID not found"


class ArgumentErrorEnum(Enum):
    """Dexcom ArgumentError strings."""

    MINUTES_INVALID = "Minutes must be and integer between 1 and 1440"
    MAX_COUNT_INVALID = "Max count must be and integer between 1 and 288"
    USERNAME_INVALID = "Username must be non-empty string"
    PASSWORD_INVALID = "Password must be non-empty string"
    ACCOUNT_ID_INVALID = "Account ID must be UUID"
    ACCOUNT_ID_DEFAULT = "Account ID default"
    SESSION_ID_INVALID = "Session ID must be UUID"
    SESSION_ID_DEFAULT = "Session ID default"
    GLUCOSE_READING_INVALID = "JSON glucose reading ill-formatted"


class DexcomError(Exception):
    """Base class for all Dexcom errors."""

    def __init__(
        self, enum: Union[AccountErrorEnum, SessionErrorEnum, ArgumentErrorEnum]
    ):
        super().__init__(enum.value)
        self.enum = enum


class AccountError(DexcomError):
    """Errors involving Dexcom Share API credentials."""

    pass


class SessionError(DexcomError):
    """Errors involving Dexcom Share API session."""

    pass


class ArgumentError(DexcomError):
    """Error involving arguments."""

    pass
