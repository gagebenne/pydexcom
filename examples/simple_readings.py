import board
import wifi
import ssl
import socketpool
import time
import adafruit_requests as requests
from pydexcom import Dexcom

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

socket = socketpool.SocketPool(wifi.radio)
requests = requests.Session(socket, ssl.create_default_context())

dexcom = Dexcom(secrets["dexcom_user"], secrets["dexcom_password"],request_session=requests) # add ous=True if outside of US

while True:
    bg = dexcom.get_current_glucose_reading()
    print("BG: ", bg.mg_dl, bg.trend_arrow)
    time.sleep(300)
    