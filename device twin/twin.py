from azure.iot.device import IoTHubDeviceClient
from dotenv import load_dotenv
from os import getenv
import json

load_dotenv()

connection_string = getenv("CONNECTION_STRING")

device_client = IoTHubDeviceClient.create_from_connection_string(connection_string, keep_alive=1000)

# connect the client.
device_client.connect()

# get the twin
twin = device_client.get_twin()
print("Twin document:")
print(json.dumps(twin, indent=2))


# send reported properties
reported = {
    "country": 208,
    "aidMode": "off",
    "smartMode": "normal",
    "disableLogging": False,
    "deviceName": "GENVEX OPT-251",
    "productName": "ECO-350",
    "brand": "GENVEX",
    "version": "0.1",
    "serialId": "DQ000648",
    "reportingInterval": 30,
    "availableMethods": {
        "boostHotWater": False,
        "boostVentilation": False,
        "forcesync": False,
    },
    "lastDeviceResetTime": {
        "reason": 0,
        "time": "2021-03-20T11:06Z"
    },
    "firmware": {"fwVersion": "3.7a5"
     },

}
device_client.patch_twin_reported_properties(reported)

# get the twin
twin = device_client.get_twin()
print("Twin document:")
with open('data.md', 'w') as f:
    json.dump(twin, f, indent=2)
print(json.dumps(twin, indent=2))

