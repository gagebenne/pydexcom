"""Constants used in `pydexcom`."""

from enum import Enum


class Region(str, Enum):
    """Regions."""

    US = "us"
    OUS = "ous"
    APAC = "apac"


DEXCOM_APPLICATION_ID_US: str = "d89443d2-327c-4a6f-89e5-496bbb0317db"
"""Dexcom application ID for US."""

DEXCOM_APPLICATION_ID_OUS: str = DEXCOM_APPLICATION_ID_US
"""Dexcom application ID for outside of the US."""

DEXCOM_APPLICATION_ID_APAC: str = "d8665ade-9673-4e27-9ff6-92db4ce13d13"
"""Dexcom application ID for APAC."""

DEXCOM_APPLICATION_IDS: dict[Region, str] = {
    Region.US: DEXCOM_APPLICATION_ID_US,
    Region.OUS: DEXCOM_APPLICATION_ID_OUS,
    Region.APAC: DEXCOM_APPLICATION_ID_APAC,
}
"""Dexcom application ID lookup based on `Region`."""

DEXCOM_BASE_URL: str = "https://share2.dexcom.com/ShareWebServices/Services"
"""Dexcom Share API base url for US."""

DEXCOM_BASE_URL_OUS: str = "https://shareous1.dexcom.com/ShareWebServices/Services"
"""Dexcom Share API base url for outside of the US."""

DEXCOM_BASE_URL_APAC: str = "https://share.dexcom.jp/ShareWebServices/Services"
"""Dexcom Share API base url for Asia-Pacific."""

DEXCOM_BASE_URLS: dict[Region, str] = {
    Region.US: DEXCOM_BASE_URL,
    Region.OUS: DEXCOM_BASE_URL_OUS,
    Region.APAC: DEXCOM_BASE_URL_APAC,
}
"""Dexcom Share API base url lookup based on `Region`."""

DEXCOM_LOGIN_ID_ENDPOINT: str = "General/LoginPublisherAccountById"
"""Dexcom Share API endpoint used to retrieve session ID."""

DEXCOM_AUTHENTICATE_ENDPOINT: str = "General/AuthenticatePublisherAccount"
"""Dexcom Share API endpoint used to retrieve account ID."""

DEXCOM_GLUCOSE_READINGS_ENDPOINT: str = "Publisher/ReadPublisherLatestGlucoseValues"
"""Dexcom Share API endpoint used to retrieve glucose values."""

DEFAULT_UUID: str = "00000000-0000-0000-0000-000000000000"
"""UUID consisting of all zeros, likely error if returned by Dexcom Share API."""

DEXCOM_TREND_DIRECTIONS: dict[str, int] = {
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

TREND_DESCRIPTIONS: list[str] = [
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

TREND_ARROWS: list[str] = ["", "↑↑", "↑", "↗", "→", "↘", "↓", "↓↓", "?", "-"]
"""Trend arrows ordered identically to `DEXCOM_TREND_DIRECTIONS`."""

MAX_MINUTES: int = 1440
"""Maximum minutes to use when retrieving glucose values (1 day)."""

MAX_MAX_COUNT: int = 288
"""Maximum count to use when retrieving glucose values (1 reading per 5 minutes)."""

MMOL_L_CONVERSION_FACTOR: float = 0.0555
"""Conversion factor between mg/dL and mmol/L."""
