[![PyPI](https://img.shields.io/pypi/v/pydexcom?style=flat-square)](https://pypi.org/project/pydexcom/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/pydexcom/)
[![Pre-commit](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/pre-commit.yaml?style=flat-square&label=pre-commit)](https://github.com/gagebenne/pydexcom/actions/workflows/pre-commit.yaml)
[![Tests](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/test.yaml?style=flat-square&label=tests)](https://github.com/gagebenne/pydexcom/actions/workflows/test.yaml)
[![Docs](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/docs.yaml?style=flat-square&label=docs)](https://gagebenne.github.io/pydexcom/pydexcom.html)

A simple Python API to interact with Dexcom Share service. Used to get *real-time* Dexcom CGM sensor data.

# Quick-start
1. Download the [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps) mobile app and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

The Dexcom Share service requires setup of at least one follower to enable the share service, but `pydexcom` will use your (or the dependent's) credentials, not the follower's or manager's.

2. Install the `pydexcom` package.

`pip install pydexcom`

3. Profit.

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(username="username", password="password") # `region="ous"` if outside of US, `region="apac"` if APAC
>>> dexcom = Dexcom(username="+11234567890", password="password") # phone number
>>> dexcom = Dexcom(username="user@email.com", password="password") # email address
>>> dexcom = Dexcom(account_id="12345678-90ab-cdef-1234-567890abcdef", password="password") # account ID (advanced)
>>> glucose_reading = dexcom.get_current_glucose_reading()
>>> print(glucose_reading)
85

>>> glucose_reading.value
85

>>> glucose_reading.mmol_l
4.7

>>> glucose_reading.trend
4

>>> glucose_reading.trend_direction
'Flat'

>>> glucose_reading.trend_description
'steady'

>>> glucose_reading.trend_arrow
'→'

>>> print(bg.datetime)
2023-08-07 20:40:58

>>> glucose_reading.json
{'WT': 'Date(1691455258000)', 'ST': 'Date(1691455258000)', 'DT': 'Date(1691455258000-0400)', 'Value': 85, 'Trend': 'Flat'}
```

# Documentation

[https://gagebenne.github.io/pydexcom/pydexcom.html](https://gagebenne.github.io/pydexcom/pydexcom.html)

# Frequently Asked Questions

## Why is my password not working?

The Dexcom Share API understandably reports limited information during account validation. If anything is incorrect, the API simply reports back invalid password ( `pydexcom.errors.AccountErrorEnum` ). However, there could be many reasons you are getting this error:

**1. Ensure your credentials are valid.**

Validate your Dexcom account credentials by logging on to the Dexcom Account Management website for your region:

For users in the United States: [uam1.dexcom.com](https://uam1.dexcom.com).
For users outside of the United States: [uam2.dexcom.com](https://uam2.dexcom.com).
For users in the Asia-Pacific: [uam.dexcom.jp](https://uam.dexcom.jp).

**2. Use the correct Dexcom Share API endpoint.**

For users in the United States: use the default, or set `region="us"` when initializing `Dexcom`.
For users outside of the United States: be sure to set `region="ous"` when initializing `Dexcom` .
For users in the Asia-Pacific: be sure to set `region="apac"` when initializing `Dexcom`.

**3. Ensure your username is correctly formatted.**

Format phone numbers with a `+`, your country code, then your phone number. For example, a US phone number of `(123)-456-7890` would be supplied as a `username="+11234567890"`.

**4. Use _your_ Dexcom Share credentials, not the _follower's_ credentials.**

Use the same credentials used to login to the Dexcom mobile application publishing the glucose readings.

**5. Ensure you have at least one follower on Dexcom Share.**

The Dexcom Share service requires setup of at least one follower to enable the service, as does this package.

**6. Try using your account ID.**

You can find your account ID by logging in to Dexcom Account Management website for your region. After logging in, note the UUID in the URL -- this is your account ID.

Format account IDs (UUIDs) with hyphens. For example, an account ID of `1234567890abcdef1234567890abcdef` found in the URL after logging in would be supplied as `account_id="12345678-90ab-cdef-1234-567890abcdef"`.

**7. Report it!**

The Dexcom Share API sometimes changes. If you believe there is an issue with `pydexcom` , feel free to [create an issue](https://github.com/gagebenne/pydexcom/issues/new) if one has not been created yet already.

## Why not use the official Dexcom Developer API?

The official Dexcom API is a great tool to view trends, statistics, and day-by-day data, but is not suitable for real time fetching of glucose readings as it is a retrospective API.

## Can I use the Dexcom Stelo with this package?

No, the Dexcom Stelo isn't compatible with the Dexcom Share service, so this package can't retrieve its readings.

## How can I let you know of suggestions or issues?

By all means submit a pull request if you have a feature you would like to see in the next release. Alternatively, you may [create an issue](https://github.com/gagebenne/pydexcom/issues/new) if you have a suggestion or bug you'd like to report.

## Where is this package being used?

Primarily this package is used in the [Home Assistant Dexcom integration](https://www.home-assistant.io/integrations/dexcom/), but it's fantastic to see community projects involving `pydexcom` :

* [Tracking glucose levels using a Raspberry Pi and e-ink display](https://www.tomshardware.com/news/raspberry-project-diy-dexcom-glucose-tracker)

* [Glucose Readings in a Terminal Prompt](https://harthoover.com/glucose-readings-in-a-terminal-prompt/)