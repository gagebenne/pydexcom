from contextlib import nullcontext as does_not_raise
from datetime import datetime
from typing import Any

import pytest
from vcr import VCR

from pydexcom import (
    DEXCOM_TREND_DIRECTIONS,
    MAX_MAX_COUNT,
    MAX_MINUTES,
    ArgumentError,
    ArgumentErrorEnum,
    Dexcom,
)

from .conftest import ACCOUNT_ID, PASSWORD, TEST_SESSION_ID_EXPIRED, vcr_cassette_path


@pytest.fixture(scope="class")
def dexcom(request: pytest.FixtureRequest, vcr: VCR) -> Dexcom:  # type:ignore
    with vcr.use_cassette(path=vcr_cassette_path(request, fixture=True)):
        return Dexcom(account_id=ACCOUNT_ID, password=PASSWORD)


@pytest.mark.vcr()
class TestGlucoseReading:
    @pytest.mark.parametrize("minutes", [None, "", "15", 0, 0.5, 1441, 10])
    @pytest.mark.parametrize("max_count", [None, "", "2", 0, 0.5, 289, 1])
    def test_get_glucose_readings(
        self, dexcom: Dexcom, minutes: Any, max_count: Any
    ) -> None:
        raises = does_not_raise()
        expected = None

        if not isinstance(minutes, int) or any([minutes < 0, minutes > MAX_MINUTES]):
            raises = pytest.raises(ArgumentError)  # type: ignore
            expected = ArgumentErrorEnum.MINUTES_INVALID
        elif not isinstance(max_count, int) or any(
            [max_count < 0, max_count > MAX_MAX_COUNT]
        ):
            raises = pytest.raises(ArgumentError)  # type: ignore
            expected = ArgumentErrorEnum.MAX_COUNT_INVALID

        with raises as error:
            glucose_readings = dexcom.get_glucose_readings(minutes, max_count)

            assert isinstance(glucose_readings, list)
            assert len(glucose_readings) <= int(max_count)

            for glucose_reading in glucose_readings:
                assert glucose_reading is not None
                assert isinstance(glucose_reading.value, int)
                assert glucose_reading.value >= 0
                assert glucose_reading.value <= 400

                assert isinstance(glucose_reading.trend_direction, str)
                assert glucose_reading.trend_direction in DEXCOM_TREND_DIRECTIONS

                assert isinstance(glucose_reading.trend, int)
                assert glucose_reading.trend in range(len(DEXCOM_TREND_DIRECTIONS))

                assert isinstance(glucose_reading.datetime, datetime)

                assert isinstance(glucose_reading.json, dict)

            return

        assert error.value.enum == expected

    def test_get_latest_glucose_reading(self, dexcom: Dexcom) -> None:
        dexcom.get_latest_glucose_reading()

    def test_get_current_glucose_reading(self, dexcom: Dexcom) -> None:
        dexcom.get_current_glucose_reading()

    def test_get_current_glucose_reading_session_expired(self, dexcom: Dexcom) -> None:
        dexcom._session_id = TEST_SESSION_ID_EXPIRED
        dexcom.get_current_glucose_reading()
