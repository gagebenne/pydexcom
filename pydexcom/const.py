"""Constants used in `pydexcom`."""

from typing import Dict, List

DEXCOM_APPLICATION_ID: str = "d89443d2-327c-4a6f-89e5-496bbb0317db"
"""Dexcom application ID."""

DEXCOM_BASE_URL: str = "https://share2.dexcom.com/ShareWebServices/Services"
"""Dexcom Share API base url for US."""

DEXCOM_BASE_URL_OUS: str = "https://shareous1.dexcom.com/ShareWebServices/Services"
"""Dexcom Share API base url for outside of the US."""

DEXCOM_LOGIN_ID_ENDPOINT: str = "General/LoginPublisherAccountById"
"""Dexcom Share API endpoint used to retrieve account ID."""

DEXCOM_AUTHENTICATE_ENDPOINT: str = "General/AuthenticatePublisherAccount"
"""Dexcom Share API endpoint used to retrieve session ID."""

DEXCOM_GLUCOSE_READINGS_ENDPOINT: str = "Publisher/ReadPublisherLatestGlucoseValues"
"""Dexcom Share API endpoint used to retrieve glucose values."""

REQUEST_TIMEOUT: int = 10  # seconds
"""Standard request timeout to use when communicating with Dexcom Share API."""

DEFAULT_UUID: str = "00000000-0000-0000-0000-000000000000"
"""UUID consisting of all zeros, likely error if returned by Dexcom Share API."""

DEXCOM_TREND_DIRECTIONS: Dict[str, int] = {
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
"""Trend directions returned by the Dexcom Share API mapped to `int`."""

TREND_DESCRIPTIONS: List[str] = [
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
"""Trend descriptions ordered identically to `DEXCOM_TREND_DIRECTIONS`."""

TREND_ARROWS: List[str] = ["", "↑↑", "↑", "↗", "→", "↘", "↓", "↓↓", "?", "-"]
"""Trend arrows ordered identically to `DEXCOM_TREND_DIRECTIONS`."""

MAX_MINUTES: int = 1440
"""Maximum minutes to use when retrieving glucose values (1 day)."""

MAX_MAX_COUNT: int = 288
"""Maximum count to use when retrieving glucose values (1 reading per 5 minutes)."""

MMOL_L_CONVERSION_FACTOR: float = 0.0555
"""Conversion factor between mg/dL and mmol/L."""
