"""The pydexcom module for interacting with Dexcom Share API."""
import datetime
import re
from typing import Any, Dict, List, Optional

import requests

from .const import (
    _LOGGER,
    ACCOUNT_ERROR_ACCOUNT_ID_DEFAULT,
    ACCOUNT_ERROR_ACCOUNT_ID_NULL_EMPTY,
    ACCOUNT_ERROR_ACCOUNT_NOT_FOUND,
    ACCOUNT_ERROR_MAX_ATTEMPTS,
    ACCOUNT_ERROR_PASSWORD_INVALID,
    ACCOUNT_ERROR_PASSWORD_NULL_EMPTY,
    ACCOUNT_ERROR_USERNAME_NULL_EMPTY,
    ARGUMENT_ERROR_MAX_COUNT_INVALID,
    ARGUMENT_ERROR_MINUTES_INVALID,
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
    SESSION_ERROR_SESSION_ID_DEFAULT,
    SESSION_ERROR_SESSION_ID_NULL,
    SESSION_ERROR_SESSION_NOT_FOUND,
    SESSION_ERROR_SESSION_NOT_VALID,
    SESSION_ERROR_UNKNOWN,
)
from .errors import AccountError, ArgumentError, SessionError


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
        self.base_url = DEXCOM_BASE_URL_OUS if ous else DEXCOM_BASE_URL
        self.username = username
        self.password = password
        self.session_id: Optional[str] = None
        self.account_id: Optional[str] = None
        self.create_session()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """Send request to Dexcom Share API."""
        if json is None:
            json = {}
        try:
            url = f"{self.base_url}/{endpoint}"
            r = requests.request(
                method,
                url,
                params=params,
                json=json,
                timeout=DEXCOM_REQUEST_TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as http_error:
            if r.json():
                code = r.json().get("Code", None)
                message = r.json().get("Message", None)
                if code == "SessionNotValid":
                    raise SessionError(SESSION_ERROR_SESSION_NOT_VALID) from http_error
                if code == "SessionIdNotFound":
                    raise SessionError(SESSION_ERROR_SESSION_NOT_FOUND) from http_error
                if code == "SSO_AuthenticateAccountNotFound":
                    raise AccountError(ACCOUNT_ERROR_ACCOUNT_NOT_FOUND) from http_error
                if code == "AccountPasswordInvalid":
                    raise AccountError(ACCOUNT_ERROR_PASSWORD_INVALID) from http_error
                if code == "SSO_AuthenticateMaxAttemptsExceeed":
                    raise AccountError(ACCOUNT_ERROR_MAX_ATTEMPTS) from http_error
                if code == "InvalidArgument":
                    if message and "accountName" in message:
                        raise AccountError(
                            ACCOUNT_ERROR_USERNAME_NULL_EMPTY
                        ) from http_error
                    if message and "password" in message:
                        raise AccountError(
                            ACCOUNT_ERROR_PASSWORD_NULL_EMPTY
                        ) from http_error
                if code and message:
                    _LOGGER.error("%s: %s", code, message)
                else:
                    _LOGGER.error("%s", r.json())
                raise SessionError(SESSION_ERROR_UNKNOWN) from http_error
            raise http_error

    def _validate_session_id(self) -> None:
        """Validate session ID."""
        if not self.session_id:
            raise SessionError(SESSION_ERROR_SESSION_ID_NULL)
        if self.session_id == DEFAULT_SESSION_ID:
            raise SessionError(SESSION_ERROR_SESSION_ID_DEFAULT)

    def _validate_account(self) -> None:
        """Validate credentials."""
        if not self.username:
            raise AccountError(ACCOUNT_ERROR_USERNAME_NULL_EMPTY)
        if not self.password:
            raise AccountError(ACCOUNT_ERROR_PASSWORD_NULL_EMPTY)

    def _validate_account_id(self) -> None:
        """Validate account ID."""
        if not self.account_id:
            raise AccountError(ACCOUNT_ERROR_ACCOUNT_ID_NULL_EMPTY)
        if self.account_id == DEFAULT_SESSION_ID:
            raise AccountError(ACCOUNT_ERROR_ACCOUNT_ID_DEFAULT)

    def create_session(self) -> None:
        """Create Dexcom Share API session by getting session id."""
        self._validate_account()

        json = {
            "accountName": self.username,
            "password": self.password,
            "applicationId": DEXCOM_APPLICATION_ID,
        }
        # The Dexcom Share API at DEXCOM_AUTHENTICATE_ENDPOINT
        # returns the account ID if credentials are valid -- whether
        # the username is a classic username or email. Using the
        # account ID the DEXCOM_LOGIN_ID_ENDPOINT is used to fetch
        # a session ID.
        endpoint1 = DEXCOM_AUTHENTICATE_ENDPOINT
        endpoint2 = DEXCOM_LOGIN_ID_ENDPOINT

        self.account_id = self._request("post", endpoint1, json=json)
        if not self.account_id:
            raise SessionError(SESSION_ERROR_UNKNOWN)
        try:
            self._validate_account_id()

            json = {
                "accountId": self.account_id,
                "password": self.password,
                "applicationId": DEXCOM_APPLICATION_ID,
            }

            self.session_id = self._request("post", endpoint2, json=json)
            self._validate_session_id()
        except SessionError as session_error:
            raise AccountError("Unknown") from session_error

    def get_glucose_readings(
        self, minutes: int = 1440, max_count: int = 288
    ) -> Optional[List[GlucoseReading]]:
        """Get max_count glucose readings within specified minutes."""
        self._validate_session_id()
        if minutes < 1 or minutes > 1440:
            raise ArgumentError(ARGUMENT_ERROR_MINUTES_INVALID)
        if max_count < 1 or max_count > 288:
            raise ArgumentError(ARGUMENT_ERROR_MAX_COUNT_INVALID)

        params = {
            "sessionId": self.session_id,
            "minutes": minutes,
            "maxCount": max_count,
        }
        try:
            json_glucose_readings = self._request(
                "post", DEXCOM_GLUCOSE_READINGS_ENDPOINT, params=params
            )
        except SessionError:
            self.create_session()

            params = {
                "sessionId": self.session_id,
                "minutes": minutes,
                "maxCount": max_count,
            }

            json_glucose_readings = self._request(
                "post", DEXCOM_GLUCOSE_READINGS_ENDPOINT, params=params
            )

        glucose_readings = []
        if not json_glucose_readings:
            return None
        for json_glucose_reading in json_glucose_readings:
            glucose_readings.append(GlucoseReading(json_glucose_reading))
        if not glucose_readings:
            return None
        return glucose_readings

    def get_latest_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get latest available glucose reading."""
        glucose_readings = self.get_glucose_readings(max_count=1)
        if not glucose_readings:
            return None
        return glucose_readings[0]

    def get_current_glucose_reading(self) -> Optional[GlucoseReading]:
        """Get current available glucose reading."""
        glucose_readings = self.get_glucose_readings(minutes=10, max_count=1)
        if not glucose_readings:
            return None
        return glucose_readings[0]
