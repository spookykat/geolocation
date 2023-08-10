#!/bin/bash

current_datetime=$(date +"%Y-%m-%d;%H:%M:%S;CEST")

# Detect Operating System
OS=$(uname)
case $OS in
  'Linux')
    INTERFACE="wlan0"
    ;;
  'Darwin') # Darwin indicates macOS
    INTERFACE=$(networksetup -listallhardwareports | grep -E '(Wi-Fi|AirPort)' -A 1 | grep -o "en.")
    if [ -z "$INTERFACE" ]; then
        echo "WiFi interface not found."
        exit 1
    fi
    ;;
  *)
    echo "OS not supported."
    exit 1
    ;;
esac

# Scan for WiFi networks and get their MAC addresses
if [ "$OS" == "Linux" ]; then
    result=$(sudo iw "$INTERFACE" scan | grep -oE '([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}' | head -5)
elif [ "$OS" == "Darwin" ]; then
    result=$(sudo /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s | egrep -o '([a-f0-9]{2}:){5}[a-f0-9]{2}' | head -5)
fi

# Convert the result to comma-separated format
formatted_result=$(echo "$result" | tr '\n' ',' | sed 's/,$//')

# Store the formatted result in a variable
mac_addresses=$formatted_result

# Print the variable (optional)
echo "$mac_addresses"

url="https://locationmagic.org/geosubmit?token=&v=1.3&t=$current_datetime&w=$mac_addresses"

# Request the URL with curl
response=$(curl -s "$url")

# Print the response (optional)
echo "Response from the server: $response"

# Fetch the data from the URL
DATA=$(curl -s "https://locationmagic.org/fetch-locations?token=")

# Check the status of the fetched data
STATUS=$(echo $DATA | jq -r '.status')

if [[ $STATUS == "ok" ]]; then
    # Extract the latest coordinates
    LATEST_LOCATION=$(echo $DATA | jq '.locations[-1]')

    LAT=$(echo $LATEST_LOCATION | jq '.lat')
    LON=$(echo $LATEST_LOCATION | jq '.lon')
    
    echo "Latest coordinates are: Latitude: $LAT, Longitude: $LON"
else
    echo "Error fetching location."
fi
