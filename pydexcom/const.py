"""Constants used in pydexcom"""

import logging

_LOGGER = logging.getLogger("pydexcom")

DEXCOM_USER_AGENT = "Dexcom Share/3.0.2.11 CFNetwork/711.2.23 Darwin/14.0.0"
DEXCOM_APPLICATION_ID = "d89443d2-327c-4a6f-89e5-496bbb0317db"

DEXCOM_BASE_URL = "https://share2.dexcom.com/ShareWebServices/Services"
DEXCOM_LOGIN_ENDPOINT = "General/LoginPublisherAccountByName"
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
