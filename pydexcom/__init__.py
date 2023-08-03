"""The pydexcom module for interacting with Dexcom Share API."""
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

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
    REQUEST_TIMEOUT,
    TREND_ARROWS,
    TREND_DESCRIPTIONS,
)
from .errors import (
    AccountError,
    AccountErrorEnum,
    ArgumentError,
    ArgumentErrorEnum,
    SessionError,
    SessionErrorEnum,
)

__all__ = ["Dexcom", "GlucoseReading"]

_LOGGER = logging.getLogger("pydexcom")


class GlucoseReading:
    """Class for parsing glucose reading from Dexcom Share API."""

    def __init__(self, json_glucose_reading: Dict[str, Any]):
        """Initialize with JSON glucose reading from Dexcom Share API."""
        self._json = json_glucose_reading
        try:
            self._value = int(json_glucose_reading["Value"])
            self._trend_direction: str = json_glucose_reading["Trend"]
            # Dexcom Share API returns string direction now, previously integer trend
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
        """Blood glucose trend information as number 0 - 9 (see constants)."""
        return self._trend

    @property
    def trend_direction(self) -> str:
        """Blood glucose trend information as Dexcom direction."""
        return self._trend_direction

    @property
    def trend_description(self) -> Optional[str]:
        """Blood glucose trend information description (see constants)."""
        return TREND_DESCRIPTIONS[self._trend]

    @property
    def trend_arrow(self) -> str:
        """Blood glucose trend information as unicode arrow (see constants)."""
        return TREND_ARROWS[self._trend]

    @property
    def datetime(self) -> datetime:
        """Blood glucose recorded time as datetime."""
        return self._datetime

    @property
    def json(self) -> Dict[str, Any]:
        """Raw blood glucose record from Dexcom API as a dict."""
        return self._json


class Dexcom:
    """Class for communicating with Dexcom Share API."""

    def __init__(self, username: str, password: str, ous: bool = False):
        """Initialize with JSON glucose reading from Dexcom Share API."""
        self._base_url = DEXCOM_BASE_URL_OUS if ous else DEXCOM_BASE_URL
        self._username = username
        self._password = password
        self._account_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self.__session = requests.Session()
        self._session()

    def _post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send request to Dexcom Share API."""
        response = self.__session.post(
            f"{self._base_url}/{endpoint}",
            params=params,
            json={} if json is None else json,
            timeout=REQUEST_TIMEOUT,
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

    def _handle_response(
        self, response: requests.Response
    ) -> Optional[Union[SessionError, AccountError, ArgumentError]]:
        error: Optional[Union[SessionError, AccountError, ArgumentError]] = None
        if response.json():
            _LOGGER.debug("%s", response.json())
            code = response.json().get("Code", None)
            message = response.json().get("Message", None)
            # if code == "SessionNotValid":
            #     error = SessionError(SessionErrorEnum.NOT_VALID)
            if code == "SessionIdNotFound":
                error = SessionError(SessionErrorEnum.NOT_FOUND)
            # if code == "SSO_AuthenticateAccountNotFound":
            #     error = AccountError(AccountErrorEnum.ACCOUNT_NOT_FOUND)
            elif code == "AccountPasswordInvalid":
                error = AccountError(AccountErrorEnum.PASSWORD_INVALID)
            elif code == "SSO_AuthenticateMaxAttemptsExceeed":
                error = AccountError(AccountErrorEnum.MAX_ATTEMPTS)
            elif code == "InvalidArgument":
                if message and "accountName" in message:
                    error = ArgumentError(ArgumentErrorEnum.USERNAME_INVALID)
                elif message and "password" in message:
                    error = ArgumentError(ArgumentErrorEnum.PASSWORD_INVALID)
                elif message and "UUID" in message:
                    error = ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_INVALID)
            elif code and message:
                _LOGGER.error("%s: %s", code, message)
        return error

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if any([not isinstance(self._session_id, str), not self._session_id]):
            raise ArgumentError(ArgumentErrorEnum.SESSION_ID_INVALID)
        if self._session_id == DEFAULT_UUID:
            raise ArgumentError(ArgumentErrorEnum.SESSION_ID_DEFAULT)

    def _validate_credentials(self) -> None:
        """Validate credentials."""
        if any([not isinstance(self._username, str), not self._username]):
            raise ArgumentError(ArgumentErrorEnum.USERNAME_INVALID)
        if any([not isinstance(self._password, str), not self._password]):
            raise ArgumentError(ArgumentErrorEnum.PASSWORD_INVALID)

    def _validate_account_id(self) -> None:
        """Validate account ID."""
        if any([not isinstance(self._account_id, str), not self._account_id]):
            raise ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_INVALID)
        if self._account_id == DEFAULT_UUID:
            raise ArgumentError(ArgumentErrorEnum.ACCOUNT_ID_DEFAULT)

    def _get_account_id(self) -> str:
        json = {
            "accountName": self._username,
            "password": self._password,
            "applicationId": DEXCOM_APPLICATION_ID,
        }
        account_id: str = self._post(
            DEXCOM_AUTHENTICATE_ENDPOINT,
            json=json,
        )
        return account_id

    def _get_session_id(self) -> str:
        json = {
            "accountId": self._account_id,
            "password": self._password,
            "applicationId": DEXCOM_APPLICATION_ID,
        }
        session_id: str = self._post(
            DEXCOM_LOGIN_ID_ENDPOINT,
            json=json,
        )
        return session_id

    def _session(self) -> None:
        """Create Dexcom Share API session."""
        self._validate_credentials()

        if self._account_id is None:
            self._account_id = self._get_account_id()
            self._validate_account_id()

        self._session_id = self._get_session_id()
        self._validate_session_id()

    def get_glucose_readings(
        self, minutes: int = MAX_MINUTES, max_count: int = MAX_MAX_COUNT
    ) -> List[GlucoseReading]:
        """Get max_count glucose readings within specified minutes."""
        if not isinstance(minutes, int) or any([minutes < 0, minutes > MAX_MINUTES]):
            raise ArgumentError(ArgumentErrorEnum.MINUTES_INVALID)
        if not isinstance(max_count, int) or any(
            [max_count < 0, max_count > MAX_MAX_COUNT]
        ):
            raise ArgumentError(ArgumentErrorEnum.MAX_COUNT_INVALID)

        json_glucose_readings = []

        params = {
            "sessionId": self._session_id,
            "minutes": minutes,
            "maxCount": max_count,
        }

        try:
            # Requesting glucose reading with DEFAULT_UUID returns non-JSON empty string
            self._validate_session_id()

            json_glucose_readings = self._post(
                DEXCOM_GLUCOSE_READINGS_ENDPOINT,
                params=params,
            )
        except SessionError:
            self._session()

            params["sessionId"] = self._session_id

            json_glucose_readings = self._post(
                DEXCOM_GLUCOSE_READINGS_ENDPOINT,
                params=params,
            )

        return [GlucoseReading(json_reading) for json_reading in json_glucose_readings]

    def get_latest_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get latest available glucose reading."""
        glucose_readings = self.get_glucose_readings(max_count=1)
        return glucose_readings[0] if glucose_readings else None

    def get_current_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get current available glucose reading."""
        glucose_readings = self.get_glucose_readings(minutes=10, max_count=1)
        return glucose_readings[0] if glucose_readings else None
