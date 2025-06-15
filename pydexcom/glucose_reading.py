"""GlucoseReading class implementation."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .const import (
    DEXCOM_TREND_DIRECTIONS,
    MMOL_L_CONVERSION_FACTOR,
    TREND_ARROWS,
    TREND_DESCRIPTIONS,
)
from .errors import (
    ArgumentError,
    ArgumentErrorEnum,
)


class GlucoseReading:
    """Class for parsing glucose reading from Dexcom Share API."""

    def __init__(self, json_glucose_reading: dict[str, Any]) -> None:
        """
        Initialize `GlucoseReading` with JSON glucose reading from Dexcom Share API.

        :param json_glucose_reading: JSON glucose reading from Dexcom Share API
        """
        self._json = json_glucose_reading
        try:
            self._value = int(json_glucose_reading["Value"])
            self._trend_direction: str = json_glucose_reading["Trend"]
            # Dexcom Share API returns `str` direction now, previously `int` trend
            self._trend: int = DEXCOM_TREND_DIRECTIONS[self._trend_direction]

            match = re.match(
                r"Date\((?P<timestamp>\d+)(?P<timezone>[+-]\d{4})\)",
                json_glucose_reading["DT"],
            )
            if match:
                self._datetime = datetime.fromtimestamp(
                    int(match.group("timestamp")) / 1000.0,
                    tz=datetime.strptime(match.group("timezone"), "%z").tzinfo,
                )
        except (KeyError, TypeError, ValueError) as error:
            raise ArgumentError(ArgumentErrorEnum.GLUCOSE_READING_INVALID) from error

    @property
    def value(self) -> int:
        """Blood glucose value in mg/dL."""
        return self._value

    @property
    def mg_dl(self) -> int:
        """Blood glucose value in mg/dL."""
        return self._value

    @property
    def mmol_l(self) -> float:
        """Blood glucose value in mmol/L."""
        return round(self.value * MMOL_L_CONVERSION_FACTOR, 1)

    @property
    def trend(self) -> int:
        """
        Blood glucose trend information.

        Value of `pydexcom.const.DEXCOM_TREND_DIRECTIONS`.
        """
        return self._trend

    @property
    def trend_direction(self) -> str:
        """
        Blood glucose trend direction.

        Key of `pydexcom.const.DEXCOM_TREND_DIRECTIONS`.
        """
        return self._trend_direction

    @property
    def trend_description(self) -> str | None:
        """
        Blood glucose trend information description.

        See `pydexcom.const.TREND_DESCRIPTIONS`.
        """
        return TREND_DESCRIPTIONS[self._trend]

    @property
    def trend_arrow(self) -> str:
        """Blood glucose trend as unicode arrow (`pydexcom.const.TREND_ARROWS`)."""
        return TREND_ARROWS[self._trend]

    @property
    def datetime(self) -> datetime:
        """Glucose reading recorded time as datetime."""
        return self._datetime

    @property
    def json(self) -> dict[str, Any]:
        """JSON glucose reading from Dexcom Share API."""
        return self._json

    def __str__(self) -> str:
        """Blood glucose value as in mg/dL."""
        return str(self._value)
