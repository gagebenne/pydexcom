"""Constants used in pydexcom"""

import logging

_LOGGER = logging.getLogger("pydexcom")

DEXCOM_USER_AGENT = "Dexcom Share/3.0.2.11 CFNetwork/711.2.23 Darwin/14.0.0"
DEXCOM_APPLICATION_ID = "d89443d2-327c-4a6f-89e5-496bbb0317db"

DEXCOM_BASE_URL = "https://share2.dexcom.com/ShareWebServices/Services"
DEXCOM_BASE_URL_OUS = "https://shareous1.dexcom.com/ShareWebServices/Services"
DEXCOM_LOGIN_ENDPOINT = "General/LoginPublisherAccountByName"
DEXCOM_AUTHENTICATE_ENDPOINT = "General/AuthenticatePublisherAccount"
DEXCOM_VERIFY_SERIAL_NUMBER_ENDPOINT = (
    "Publisher/CheckMonitoredReceiverAssignmentStatus"
)
DEXCOM_READ_BLOOD_GLUCOSE_ENDPOINT = "Publisher/ReadPublisherLatestGlucoseValues"

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
DEXCOM_TREND_ARROWS = ["", "↑↑", "↑", "↗", "→", "↘", "↓", "↓↓", "?", "-"]

DEFAULT_SESSION_ID = "00000000-0000-0000-0000-000000000000"

ACCOUNT_ERROR_USERNAME_NULL_EMPTY = "Username null or empty"
ACCOUNT_ERROR_PASSWORD_NULL_EMPTY = "Password null or empty"
ACCOUNT_ERROR_ACCOUNT_NOT_FOUND = "Account not found"
ACCOUNT_ERROR_PASSWORD_INVALID = "Password not valid"
ACCOUNT_ERROR_UNKNOWN = "Account error"

SESSION_ERROR_SESSION_ID_NULL = "Session ID null"
SESSION_ERROR_SESSION_ID_DEFAULT = "Session ID default"
SESSION_ERROR_SESSION_NOT_VALID = "Session ID not valid"
SESSION_ERROR_SESSION_NOT_FOUND = "Session ID not found"

ARGUEMENT_ERROR_MINUTES_INVALID = "Minutes must be between 1 and 1440"
ARGUEMENT_ERROR_MAX_COUNT_INVALID = "Max count must be between 1 and 288"
ARGUEMENT_ERROR_SERIAL_NUMBER_NULL_EMPTY = "Serial number null or empty"

MMOL_L_CONVERTION_FACTOR = 0.0555
