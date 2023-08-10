import os
import requests
import random
import string
import subprocess
import json
from datetime import datetime
import re

# Get current datetime, hostname, and random string
current_datetime = datetime.now().strftime("%Y-%m-%d;%H:%M:%S;CEST")
hostname_value = os.uname().nodename
random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

payload = {
    "device-form[email]": f"{random_string}@{random_string}.be",
    "device-form[device_name]": "TEST"
}

# Post request to get the token
response = requests.post(
    'https://locationmagic.org/register',
    headers={
        'Host': 'locationmagic.org',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    },
    data=payload,
    proxies={'http': 'http://127.0.0.1:8080'}
)
token = response.json().get('token')
print(token)

# Detect Operating System
OS = os.uname().sysname

if OS == "Linux":
    INTERFACE = "wlan0"
elif OS == "Darwin":
    # Assuming macOS
    cmd_output = subprocess.check_output(["networksetup", "-listallhardwareports"]).decode()
    interface_lines = [line for line in cmd_output.splitlines() if "en" in line]
    INTERFACE = interface_lines[0].split()[-1] if interface_lines else None
    if not INTERFACE:
        print("WiFi interface not found.")
        exit(1)
else:
    print("OS not supported.")
    exit(1)

# Scan for WiFi networks and get their MAC addresses
if OS == "Linux":
    result = subprocess.check_output(["sudo", "iw", INTERFACE, "scan"]).decode()
elif OS == "Darwin":
    result = subprocess.check_output(["sudo", "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"]).decode()

mac_addresses = ','.join([match.group() for match in re.finditer(r'([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}', result)][:5])

print(mac_addresses)

url = f"https://locationmagic.org/geosubmit?token={token}&v=1.3&t={current_datetime}&w={mac_addresses}"

response = requests.get(url)
print(f"Response from the server: {response.text}")

data = requests.get(f"https://locationmagic.org/fetch-locations?token={token}").json()
status = data.get("status")

if status == "ok":
    latest_location = data["locations"][-1]
    lat, lon = latest_location["lat"], latest_location["lon"]
    print(f"Latest coordinates are: Latitude: {lat}, Longitude: {lon}")

    webhook_payload = {
        "latitude": lat,
        "longitude": lon,
        "hostname": hostname_value
    }
    WEBHOOKURL = os.environ.get("WEBHOOKURL")
    if not WEBHOOKURL:
        print("WEBHOOKURL not set in environment variables.")
        exit(1)
    response = requests.post(WEBHOOKURL, headers={"Content-Type": "application/json"}, data=json.dumps(webhook_payload))
else:
    print("Error fetching location.")
