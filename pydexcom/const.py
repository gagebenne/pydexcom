"""Constants used in pydexcom."""

import logging

_LOGGER = logging.getLogger("pydexcom")


# Dexcom Share API base urls
DEXCOM_BASE_URL = "https://share2.dexcom.com/ShareWebServices/Services"
DEXCOM_BASE_URL_OUS = "https://shareous1.dexcom.com/ShareWebServices/Services"

# Dexcom Share API endpoints
DEXCOM_LOGIN_ID_ENDPOINT = "General/LoginPublisherAccountById"
DEXCOM_AUTHENTICATE_ENDPOINT = "General/AuthenticatePublisherAccount"
DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT = (
    "Publisher/CheckMonitoredReceiverAssignmentStatus"
)
DEXCOM_GLUCOSE_READINGS_ENDPOINT = "Publisher/ReadPublisherLatestGlucoseValues"

DEXCOM_APPLICATION_ID = "d89443d2-327c-4a6f-89e5-496bbb0317db"

# Dexcom error strings
ACCOUNT_ERROR_USERNAME_NULL_EMPTY = "Username null or empty"
ACCOUNT_ERROR_PASSWORD_NULL_EMPTY = "Password null or empty"
SESSION_ERROR_ACCOUNT_ID_NULL_EMPTY = "Accound ID null or empty"
SESSION_ERROR_ACCOUNT_ID_DEFAULT = "Accound ID default"
ACCOUNT_ERROR_ACCOUNT_NOT_FOUND = "Account not found"
ACCOUNT_ERROR_PASSWORD_INVALID = "Password not valid"
ACCOUNT_ERROR_MAX_ATTEMPTS = "Maximum authentication attempts exceeded"
ACCOUNT_ERROR_UNKNOWN = "Account error"

SESSION_ERROR_SESSION_ID_NULL = "Session ID null"
SESSION_ERROR_SESSION_ID_DEFAULT = "Session ID default"
SESSION_ERROR_SESSION_NOT_VALID = "Session ID not valid"
SESSION_ERROR_SESSION_NOT_FOUND = "Session ID not found"

ARGUEMENT_ERROR_MINUTES_INVALID = "Minutes must be between 1 and 1440"
ARGUEMENT_ERROR_MAX_COUNT_INVALID = "Max count must be between 1 and 288"
ARGUEMENT_ERROR_SERIAL_NUMBER_NULL_EMPTY = "Serial number null or empty"


# Other
DEXCOM_TREND_DESCRIPTIONS = [
    "",
    "rising quickly",
    "rising",
    "rising slightly",
    "steady",
    "falling slightly",
    "falling",
    "falling quickly",
    "unable to determine trend",
    "trend unavailable",
]

DEXCOM_TREND_DIRECTIONS = {
    "None": 0,  # unconfirmed
    "DoubleUp": 1,
    "SingleUp": 2,
    "FortyFiveUp": 3,
    "Flat": 4,
    "FortyFiveDown": 5,
    "SingleDown": 6,
    "DoubleDown": 7,
    "NotComputable": 8,  # unconfirmed
    "RateOutOfRange": 9,  # unconfirmed
}

DEXCOM_TREND_ARROWS = ["", "↑↑", "↑", "↗", "→", "↘", "↓", "↓↓", "?", "-"]

DEFAULT_SESSION_ID = "00000000-0000-0000-0000-000000000000"

MMOL_L_CONVERTION_FACTOR = 0.0555
