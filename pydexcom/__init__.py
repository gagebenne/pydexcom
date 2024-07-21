"""
.. include:: ../README.md
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import requests

from .const import (
    DEFAULT_UUID,
    DEXCOM_APPLICATION_ID,
    DEXCOM_AUTHENTICATE_ENDPOINT,
    DEXCOM_BASE_URL,
    DEXCOM_BASE_URL_OUS,
    DEXCOM_GLUCOSE_READINGS_ENDPOINT,
    DEXCOM_LOGIN_ID_ENDPOINT,
    DEXCOM_TREND_DIRECTIONS,
    MAX_MAX_COUNT,
    MAX_MINUTES,
    MMOL_L_CONVERSION_FACTOR,
    TREND_ARROWS,
    TREND_DESCRIPTIONS,
)
from .errors import (
    AccountError,
    AccountErrorEnum,
    ArgumentError,
    ArgumentErrorEnum,
    DexcomError,
    SessionError,
    SessionErrorEnum,
)

_LOGGER = logging.getLogger("pydexcom")


class GlucoseReading:
    """Class for parsing glucose reading from Dexcom Share API."""

    def __init__(self, json_glucose_reading: Dict[str, Any]):
        """Initialize `GlucoseReading` with JSON glucose reading from Dexcom Share API.

        :param json_glucose_reading: JSON glucose reading from Dexcom Share API
        """
        self._json = json_glucose_reading
        try:
            self._value = int(json_glucose_reading["Value"])
            self._trend_direction: str = json_glucose_reading["Trend"]
            # Dexcom Share API returns `str` direction now, previously `int` trend
            self._trend: int = DEXCOM_TREND_DIRECTIONS[self._trend_direction]
            self._datetime = datetime.fromtimestamp(
                int(re.sub("[^0-9]", "", json_glucose_reading["WT"])) / 1000.0
            )
        except (KeyError, TypeError, ValueError):
            raise ArgumentError(ArgumentErrorEnum.GLUCOSE_READING_INVALID)

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
        """Blood glucose trend information
        (value of `pydexcom.const.DEXCOM_TREND_DIRECTIONS`)."""
        return self._trend

    @property
    def trend_direction(self) -> str:
        """Blood glucose trend direction
        (key of `pydexcom.const.DEXCOM_TREND_DIRECTIONS`)."""
        return self._trend_direction

    @property
    def trend_description(self) -> Optional[str]:
        """Blood glucose trend information description
        (`pydexcom.const.TREND_DESCRIPTIONS`).
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
    def json(self) -> Dict[str, Any]:
        """JSON glucose reading from Dexcom Share API."""
        return self._json

    def __str__(self) -> str:
        return str(self._value)


def valid_uuid(uuid: Optional[str]) -> bool:
    try:
        UUID((str(uuid)))
        return True
    except ValueError:
        return False


class Dexcom:
    """Class for communicating with Dexcom Share API."""

    def __init__(
        self,
        *,
        password: str,
        account_id: Optional[str] = None,
        username: Optional[str] = None,
        ous: bool = False,
    ):
        """
        Initialize `Dexcom` with Dexcom Share credentials.

        :param username: username for the Dexcom Share user, *not follower*.
        :param account_id: account ID for the Dexcom Share user, *not follower*.
        :param password: password for the Dexcom Share user.
        :param ous: whether the Dexcom Share user is outside of the US.
        """
        user_ids = len(
            [user_id for user_id in [account_id, username] if user_id is not None]
        )
        if user_ids == 0:
            raise ArgumentError(ArgumentErrorEnum.NONE_USER_ID_PROVIDED)
        if user_ids != 1:
            raise ArgumentError(ArgumentErrorEnum.TOO_MANY_USER_ID_PROVIDED)

        self._base_url = DEXCOM_BASE_URL_OUS if ous else DEXCOM_BASE_URL
        self._password = password
        self._username: Optional[str] = username
        self._account_id: Optional[str] = account_id
        self._session_id: Optional[str] = None
        self.__session = requests.Session()
        self._session()

    def _post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send post request to Dexcom Share API.

        :param endpoint: URL of the post request
        :param params: `dict` to send in the query string of the post request
        :param json: JSON to send in the body of the post request
        """
        response = self.__session.post(
            f"{self._base_url}/{endpoint}",
            headers={"Accept-Encoding": "application/json"},
            params=params,
            json={} if json is None else json,
        )

        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_error:
            error = self._handle_response(response)
            if error:
                raise error from http_error
            _LOGGER.error("%s", response.text)
            raise http_error

    def _handle_response(self, response: requests.Response) -> Optional[DexcomError]:
        error: Optional[DexcomError] = None
        """
        Parse `requests.Response` for `pydexcom.errors.DexcomError`.

        :param response: `requests.Response` to parse
        """
        if response.json():
            _LOGGER.debug("%s", response.json())
            code = response.json().get("Code", None)
            message = response.json().get("Message", None)
            if code == "SessionIdNotFound":
                error = SessionError(SessionErrorEnum.NOT_FOUND)
            elif code == "SessionNotValid":
                error = SessionError(SessionErrorEnum.INVALID)
            elif code == "AccountPasswordInvalid":  # defunct
                error = AccountError(AccountErrorEnum.FAILED_AUTHENTICATION)
            elif code == "SSO_AuthenticateMaxAttemptsExceeed":
                error = AccountError(AccountErrorEnum.MAX_ATTEMPTS)
            elif code == "SSO_InternalError":
                if message and "Cannot Authenticate by AccountName" in message:
                    error = AccountError(AccountErrorEnum.FAILED_AUTHENTICATION)
                elif message and "Cannot Authenticate by AccountId" in message:
                    error = AccountError(AccountErrorEnum.FAILED_AUTHENTICATION)
            elif code == "InvalidArgument":
                if message and "accountName" in message:
                    error = ArgumentError(ArgumentErrorEnum.USERNAME_INVALID)
                elif message and "password" in message:
                    error = ArgumentError(ArgumentErrorEnum.PASSWORD_INVALID)
                elif message and "UUID" in message:
                    error = ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_INVALID)
            elif code and message:
                _LOGGER.debug("%s: %s", code, message)
        return error

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if any(
            [
                not isinstance(self._session_id, str),
                not self._session_id,
                not valid_uuid(self._session_id),
            ]
        ):
            raise ArgumentError(ArgumentErrorEnum.SESSION_ID_INVALID)
        if self._session_id == DEFAULT_UUID:
            raise ArgumentError(ArgumentErrorEnum.SESSION_ID_DEFAULT)

    def _validate_username(self) -> None:
        """Validate username."""
        if any([not isinstance(self._username, str), not self._username]):
            raise ArgumentError(ArgumentErrorEnum.USERNAME_INVALID)

    def _validate_password(self) -> None:
        """Validate password."""
        if any([not isinstance(self._password, str), not self._password]):
            raise ArgumentError(ArgumentErrorEnum.PASSWORD_INVALID)

    def _validate_account_id(self) -> None:
        """Validate account ID."""
        if any(
            [
                not isinstance(self._account_id, str),
                not self._account_id,
                not valid_uuid(self._account_id),
            ],
        ):
            raise ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_INVALID)
        if self._account_id == DEFAULT_UUID:
            raise ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_DEFAULT)

    def _get_account_id(self) -> str:
        """Retrieve account ID from the authentication endpoint
        (`pydexcom.const.DEXCOM_AUTHENTICATE_ENDPOINT`)."""
        _LOGGER.debug("Retrieve account ID from the authentication endpoint")
        return self._post(
            DEXCOM_AUTHENTICATE_ENDPOINT,
            json={
                "accountName": self._username,
                "password": self._password,
                "applicationId": DEXCOM_APPLICATION_ID,
            },
        )

    def _get_session_id(self) -> str:
        """Retrieve session ID from the login endpoint
        (`pydexcom.const.DEXCOM_LOGIN_ID_ENDPOINT`)."""
        _LOGGER.debug("Retrieve session ID from the login endpoint")
        return self._post(
            DEXCOM_LOGIN_ID_ENDPOINT,
            json={
                "accountId": self._account_id,
                "password": self._password,
                "applicationId": DEXCOM_APPLICATION_ID,
            },
        )

    def _session(self) -> None:
        """Create Dexcom Share API session."""
        self._validate_password()

        if self._account_id is None:
            self._validate_username()
            self._account_id = self._get_account_id()

        self._validate_account_id()
        self._session_id = self._get_session_id()
        self._validate_session_id()

    def _get_glucose_readings(
        self, minutes: int = MAX_MINUTES, max_count: int = MAX_MAX_COUNT
    ) -> List[Dict[str, Any]]:
        """Retrieve glucose readings from the glucose readings endpoint
        (`pydexcom.const.DEXCOM_GLUCOSE_READINGS_ENDPOINT`)."""
        if not isinstance(minutes, int) or any([minutes < 0, minutes > MAX_MINUTES]):
            raise ArgumentError(ArgumentErrorEnum.MINUTES_INVALID)
        if not isinstance(max_count, int) or any(
            [max_count < 0, max_count > MAX_MAX_COUNT]
        ):
            raise ArgumentError(ArgumentErrorEnum.MAX_COUNT_INVALID)

        _LOGGER.debug("Retrieve glucose readings from the glucose readings endpoint")
        return self._post(
            DEXCOM_GLUCOSE_READINGS_ENDPOINT,
            params={
                "sessionId": self._session_id,
                "minutes": minutes,
                "maxCount": max_count,
            },
        )

    def get_glucose_readings(
        self, minutes: int = MAX_MINUTES, max_count: int = MAX_MAX_COUNT
    ) -> List[GlucoseReading]:
        """Get `max_count` glucose readings within specified number of `minutes`.

        Catches one instance of a thrown `pydexcom.errors.SessionError` if session ID
        expired, attempts to get a new session ID and retries.

        :param minutes: Number of minutes to retrieve glucose readings from (1-1440)
        :param max_count: Maximum number of glucose readings to retrieve (1-288)
        """

        json_glucose_readings: List[Dict[str, Any]] = []

        try:
            # Requesting glucose reading with DEFAULT_UUID returns non-JSON empty string
            self._validate_session_id()

            json_glucose_readings = self._get_glucose_readings(minutes, max_count)
        except SessionError:
            # Attempt to update expired session ID
            self._session()

            json_glucose_readings = self._get_glucose_readings(minutes, max_count)

        return [GlucoseReading(json_reading) for json_reading in json_glucose_readings]

    def get_latest_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get latest available glucose reading, within the last 24 hours."""
        glucose_readings = self.get_glucose_readings(max_count=1)
        return glucose_readings[0] if glucose_readings else None

    def get_current_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get current available glucose reading, within the last 10 minutes."""
        glucose_readings = self.get_glucose_readings(minutes=10, max_count=1)
        return glucose_readings[0] if glucose_readings else None
