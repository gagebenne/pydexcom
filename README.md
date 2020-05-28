[![Donate](https://img.shields.io/badge/Donate-PayPal-green?style=flat-square)](https://www.paypal.me/gagebenne)
[![PyPI](https://img.shields.io/pypi/v/pydexcom?style=flat-square)](https://www.pypi.org/project/pydexcom)

# pydexcom

A simple Python API to interact with Dexcom Share service. Used to get **real time** Dexcom GCM sensor data.

### Setup

1. Download the [Dexcom G6 / G5 / G4](https://www.dexcom.com/apps) mobile app and [enable the Share service](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow).

    *Note: the service requires setup of at least one follower to enable the share service, but `pydexcom` will use your credentials, not the follower's.*

2. Install the `pydexcom` package.
    ```python
    pip3 install pydexcom
    ```

### Usage

```python
>>> from pydexcom import Dexcom
>>> dexcom = Dexcom("username", "password")
>>> bg = dexcom.get_current_glucose_reading()
>>> bg.value
85

>>> bg.trend
4

>>> bg.trend_description
'steady'

>>> bg.trend_arrow
'→'

>>> bg.time
datetime.datetime(2020, 5, 6, 18, 18, 42)
```

### FAQ

<details>
<summary>What do I need to get started?</a></summary>
<br/>
If you are currently on the Dexcom GCM system, all you need is the appropriate mobile app with the Dexcom Share service enabled.
</details>
<details>
<summary>Where is this package being used?</a></summary>
<br/>
For now this package is just being used in the <a href="https://github.com/home-assistant/core/pull/33852">Dexcom home assistant integration</a>, but is generic enough to be used in lots of applications.
</details>

<details>
<summary>Why not use the <a href="https://developer.dexcom.com/">official Dexcom Developer API?</a></summary>
<br/>
The official Dexcom API is a great tool to view trends, statistics, and day-by-day data, but is not suitable for real time fetching of glucose readings.
</details>
<details>
<summary>How can I let you know of suggestions or issues?</summary>
<br/>
By all means submit a pull request if you have a feature you'd like to see in the next release, alternatively you may leave a issue if you have a suggestion or bug you'd like to alert me of. 
</details>
<details>
<summary>Are there any features in development?</summary>
<br/>
Sure, I'm thinking of implementing a session status checker, or maybe an asynchronus version. That being said, simplicity - getting real time blood glucose information - is most important to this package.
</details>

### Development

##### Dexcom class

| Function                    | Input                                                   | Output                          | Description                                                  |
| --------------------------- | ------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------ |
| \_\_init\_\_                | `username:str`,<br/>`password:str`,<br/>`ous:bool=True` | `Dexcom`                        | Dexcom constructor, stores authentication information        |
| create_session              |                                                         |                                 | Creates Dexcom Share API session by getting session id       |
| verify_serial_number        | `serial_number:str`                                     | `bool`                          | Verifies if a transmitter serial number is assigned to you   |
| get_glucose_readings        | `minutes:int=1440`,<br/>`max_count:int=288`             | `[GlucoseReading]`/<br />`None` | Gets max_count glucose readings within the past minutes, None if no glucose reading in the past 24 hours |
| get_latest_glucose_reading  |                                                         | `GlucoseReading`/<br />`None`   | Gets latest available glucose reading, None if no glucose reading in the past 24 hours |
| get_current_glucose_reading |                                                         | `GlucoseReading`/`None`         | Gets current available glucose reading, None if no glucose reading in the past 6 minutes |

##### Glucose Reading

| Attribute         | Definition                                                   | Example                                     |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------- |
| value             | Blood glucose value in mm/dL or mmol/L.                      | `85`                                        |
| trend             | Blood glucose trend information as number 0 - 9 (see constants). | `4`                                         |
| trend_description | Blood glucose trend information description (see constants). | `'steady'`                                  |
| trend_arrow       | Blood glucose trend information as unicode arrow (see constants). | `'→'`                                       |
| time              | Blood glucose recorded time as `datetime`.                   | `datetime.datetime(2020, 5, 6, 18, 18, 42)` |

##### Constants

| Trend | Trend description             | Trend arrow |
| ----- | ----------------------------- | ----------- |
| 0     | `''`                          | `''`        |
| 1     | `'rising quickly'`            | `'↑↑'`      |
| 2     | `'rising'`                    | `'↑'`       |
| 3     | `'rising slightly'`           | `'↗'`       |
| 4     | `'steady'`                    | `'→'`       |
| 5     | `'falling slightly'`          | `'↘'`       |
| 6     | `'falling'`                   | `'↓'`       |
| 7     | `'falling quickly'`           | `'↓↓'`      |
| 8     | `'unable to determine trend'` | `'?'`       |
| 9     | `'trend unavailable'`         | `'-'`       |
