[![PyPI](https://img.shields.io/pypi/v/pydexcom?style=flat-square)](https://pypi.org/project/pydexcom/)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest.svg?style=flat-square)](https://pypi.org/project/pydexcom/)
[![Pre-commit](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/pre-commit.yaml?style=flat-square&label=pre-commit)](https://github.com/gagebenne/pydexcom/actions/workflows/pre-commit.yaml)
[![Tests](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/test.yaml?style=flat-square&label=tests)](https://github.com/gagebenne/pydexcom/actions/workflows/test.yaml)
[![Docs](https://img.shields.io/github/actions/workflow/status/gagebenne/pydexcom/docs.yaml?style=flat-square&label=docs)](https://gagebenne.github.io/pydexcom/pydexcom.html)

A simple Python API to interact with Dexcom Share service. Used to get *real-time* Dexcom CGM sensor data.

# Quick-start
1. Download the [Dexcom G7 / G6 / G5 / G4](https://www.dexcom.com/apps) mobile app and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

The Dexcom Share service requires setup of at least one follower to enable the share service, but `pydexcom` will use your credentials, not the follower's

> [!CAUTION]
> With the release of the Dexcom G7, users are now able to authenticate with a mobile phone or email address. `pydexcom` currently does not support this, only legacy username-based authentication.
>
> While this is [being resolved](https://github.com/gagebenne/pydexcom/issues/55), please authenticate using your account ID. You can find your account ID by logging in to [uam1.dexcom.com](https://uam1.dexcom.com) for US users or [uam2.dexcom.com](https://uam2.dexcom.com) for users outside of the US. After logging in, note the UUID in the URL -- this is your account ID.

2. Install the `pydexcom` package.

 `pip3 install pydexcom`

3. Profit.

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom(account_id="account_id", password="password") # `ous=True` if outside of US
>>> dexcom = Dexcom(username="username", password="password") # legacy username accounts only
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

1. Use the correct Dexcom Share API instance.

If you are located outside of the United States, be sure to set `ous=True` when initializing `Dexcom` .

2. Use your Dexcom Share credentials, not the follower's credentials.

Use the same credentials used to login to the Dexcom mobile application publishing the glucose readings.

3. Ensure you have at least one follower on Dexcom Share.

The Dexcom Share service requires setup of at least one follower to enable the service, as does this package.

4. Check whether your account credentials involve usernames or emails.

There are two account types the Dexcom Share API uses: legacy username-based accounts, and newer email-based accounts. Be sure to use the correct authentication method.

5. Use alpha-numeric passwords.

Some individuals have had problems with connecting when their Dexcom Share passwords are entirely numeric. If you have connection issues, try changing your password to something with a mix of numbers and letters.

7. Report it!

The Dexcom Share API sometimes changes. If you believe there is an issue with `pydexcom` , feel free to [create an issue](https://github.com/gagebenne/pydexcom/issues/new) if one has not been created yet already.

## Why not use the official Dexcom Developer API?

The official Dexcom API is a great tool to view trends, statistics, and day-by-day data, but is not suitable for real time fetching of glucose readings as it is a retrospective API.

## How can I let you know of suggestions or issues?

By all means submit a pull request if you have a feature you would like to see in the next release. Alternatively, you may [create an issue](https://github.com/gagebenne/pydexcom/issues/new) if you have a suggestion or bug you'd like to report.

## Where is this package being used?

Primarily this package is used in the [Home Assistant Dexcom integration](https://www.home-assistant.io/integrations/dexcom/), but it's fantastic to see community projects involving `pydexcom` :

* [Tracking glucose levels using a Raspberry Pi and e-ink display](https://www.tomshardware.com/news/raspberry-project-diy-dexcom-glucose-tracker)

* [Glucose Readings in a Terminal Prompt](https://harthoover.com/glucose-readings-in-a-terminal-prompt/)
