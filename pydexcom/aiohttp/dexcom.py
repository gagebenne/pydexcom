from __future__ import annotations

from typing import Any, override

import aiohttp

from pydexcom.const import HEADERS, MAX_MAX_COUNT, MAX_MINUTES, Region
from pydexcom.dexcom import Dexcom as BaseDexcom
from pydexcom.errors import SessionError
from pydexcom.glucose_reading import GlucoseReading

from .util import _LOGGER


class Dexcom(BaseDexcom):
    @override
    def __init__(
        self,
        *,
        password: str,
        account_id: str | None = None,
        username: str | None = None,
        region: Region = Region.US,
    ) -> None:
        super().__init__(
            password=password,
            account_id=account_id,
            username=username,
            region=region,
        )

        self._session = aiohttp.ClientSession(
            base_url=self._base_url,
            headers=HEADERS,
            raise_for_status=True,
        )

    def _get_glucose_readings(
        self,
        minutes: int = MAX_MINUTES,
        max_count: int = MAX_MAX_COUNT,
    ) -> list[dict[str, Any]]:
        """Retrieve glucose readings from the glucose readings endpoint.

        See `pydexcom.const.DEXCOM_GLUCOSE_READINGS_ENDPOINT`.
        """
        self._validate_minutes_max_count(minutes, max_count)
        _LOGGER.debug("Retrieve glucose readings from the glucose readings endpoint")
        return self._post(
            params={
                "sessionId": self._session_id,
                "minutes": minutes,
                "maxCount": max_count,
            },
        )

    async def get_glucose_readings(
        self,
        minutes: int = MAX_MINUTES,
        max_count: int = MAX_MAX_COUNT,
    ) -> list[GlucoseReading]:
        json_glucose_readings: list[dict[str, Any]] = []

        try:
            self._validate_session_id()
            json_glucose_readings = await self._get_glucose_readings(minutes, max_count)
        except SessionError:
            await self._get_session()
            json_glucose_readings = await self._get_glucose_readings(minutes, max_count)

        return [GlucoseReading(json_reading) for json_reading in json_glucose_readings]

    async def get_latest_glucose_reading(self) -> GlucoseReading | None:
        return next(iter(await self.get_glucose_readings(max_count=1)), None)

    async def get_current_glucose_reading(self) -> GlucoseReading | None:
        return next(
            iter(await self.get_glucose_readings(minutes=10, max_count=1)),
            None,
        )

    @override
    async def _post(self, *args, **kwargs) -> None:
        try:
            async with self._session.post(*args, *kwargs) as response:
                return await response.json()
        except aiohttp.ClientResponseError:
            try:
                if j := await response.json():
                    print(j)
            except aiohttp.ContentTypeError:
                print("unknown")
