"""The pydexcom module for interacting with Dexcom Share API."""
import datetime
import re
from typing import Any, Dict, List, Optional, Union

import requests

__all__ = ["Dexcom", "GlucoseReading"]

from .const import (
    _LOGGER,
    DEFAULT_SESSION_ID,
    DEXCOM_APPLICATION_ID,
    DEXCOM_AUTHENTICATE_ENDPOINT,
    DEXCOM_BASE_URL,
    DEXCOM_BASE_URL_OUS,
    DEXCOM_GLUCOSE_READINGS_ENDPOINT,
    DEXCOM_LOGIN_ID_ENDPOINT,
    DEXCOM_REQUEST_TIMEOUT,
    DEXCOM_TREND_ARROWS,
    DEXCOM_TREND_DESCRIPTIONS,
    DEXCOM_TREND_DIRECTIONS,
    MMOL_L_CONVERSION_FACTOR,
)
from .errors import (
    AccountError,
    AccountErrorEnum,
    ArgumentError,
    ArgumentErrorEnum,
    SessionError,
    SessionErrorEnum,
)


class GlucoseReading:
    """Class for parsing glucose reading from Dexcom Share API."""

    def __init__(self, json_glucose_reading: Dict[str, Any]):
        """Initialize with JSON glucose reading from Dexcom Share API."""
        self._json = json_glucose_reading
        self._value = int(json_glucose_reading["Value"])
        self._trend_direction: str = json_glucose_reading["Trend"]
        # API returns `str` direction now, previously `int` trend
        self._trend: int = DEXCOM_TREND_DIRECTIONS.get(
            self._trend_direction,
            0,
        )
        self._time = datetime.datetime.fromtimestamp(
            int(re.sub("[^0-9]", "", json_glucose_reading["WT"])) / 1000.0
        )

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
    def trend_description(self) -> Optional[str]:
        """Blood glucose trend information description (see constants)."""
        try:
            return DEXCOM_TREND_DESCRIPTIONS[self._trend]
        except IndexError:
            return None

    @property
    def trend_arrow(self) -> Optional[str]:
        """Blood glucose trend information as unicode arrow (see constants)."""
        try:
            return DEXCOM_TREND_ARROWS[self._trend]
        except IndexError:
            return None

    @property
    def time(self) -> datetime.datetime:
        """Blood glucose recorded time as datetime."""
        return self._time

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
        if json is None:
            json = {}
        try:
            url = f"{self._base_url}/{endpoint}"
            response = self.__session.post(
                url,
                params=params,
                json=json,
                timeout=DEXCOM_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_error:
            if response.json():
                _LOGGER.debug("%s", response.json())
                code = response.json().get("Code", None)
                message = response.json().get("Message", None)
                error: Optional[Union[SessionError, AccountError]] = None
                if code == "SessionNotValid":
                    error = SessionError(SessionErrorEnum.NOT_VALID)
                if code == "SessionIdNotFound":
                    error = SessionError(SessionErrorEnum.NOT_FOUND)
                if code == "SSO_AuthenticateAccountNotFound":
                    error = AccountError(AccountErrorEnum.ACCOUNT_NOT_FOUND)
                if code == "AccountPasswordInvalid":
                    error = AccountError(AccountErrorEnum.PASSWORD_INVALID)
                if code == "SSO_AuthenticateMaxAttemptsExceeed":
                    error = AccountError(AccountErrorEnum.MAX_ATTEMPTS)
                if code == "InvalidArgument":
                    if message and "accountName" in message:
                        error = AccountError(AccountErrorEnum.USERNAME_NULL_EMPTY)
                    if message and "password" in message:
                        error = AccountError(AccountErrorEnum.PASSWORD_NULL_EMPTY)
                if error:
                    raise error from http_error
                if code and message:
                    _LOGGER.error("%s: %s", code, message)
            _LOGGER.error("%s", response.text)
            raise http_error

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if not self._session_id:
            raise SessionError(SessionErrorEnum.NULL)
        if self._session_id == DEFAULT_SESSION_ID:
            raise SessionError(SessionErrorEnum.DEFAULT)

    def _validate_credentials(self) -> None:
        """Validate credentials."""
        if not self._username:
            raise AccountError(AccountErrorEnum.USERNAME_NULL_EMPTY)
        if not self._password:
            raise AccountError(AccountErrorEnum.PASSWORD_NULL_EMPTY)

    def _validate_account_id(self) -> None:
        """Validate account ID."""
        if not self._account_id:
            raise AccountError(AccountErrorEnum.ACCOUNT_ID_NULL_EMPTY)
        if self._account_id == DEFAULT_SESSION_ID:
            raise AccountError(AccountErrorEnum.ACCOUNT_ID_DEFAULT)

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
        self, minutes: int = 1440, max_count: int = 288
    ) -> Optional[List[GlucoseReading]]:
        """Get max_count glucose readings within specified minutes."""
        if type(minutes) != int or minutes < 1 or minutes > 1440:
            raise ArgumentError(ArgumentErrorEnum.MINUTES_INVALID)
        if type(max_count) != int or max_count < 1 or max_count > 288:
            raise ArgumentError(ArgumentErrorEnum.MAX_COUNT_INVALID)

        # Requesting glucose reading with DEFAULT_SESION_ID
        # returns non-JSON empty string
        self._validate_session_id()

        json_glucose_readings = []

        params = {
            "sessionId": self._session_id,
            "minutes": minutes,
            "maxCount": max_count,
        }

        try:
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

        return [GlucoseReading(reading) for reading in json_glucose_readings]

    def get_latest_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get latest available glucose reading."""
        glucose_readings = self.get_glucose_readings(max_count=1)
        return glucose_readings[0] if glucose_readings else None

    def get_current_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get current available glucose reading."""
        glucose_readings = self.get_glucose_readings(minutes=10, max_count=1)
        return glucose_readings[0] if glucose_readings else None
