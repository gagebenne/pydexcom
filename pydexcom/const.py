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

MMOL_L_CONVERSION_FACTOR = 0.0555

DEXCOM_REQUEST_TIMEOUT = 10  # seconds
