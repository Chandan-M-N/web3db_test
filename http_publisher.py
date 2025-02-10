import requests
import time
import json
import random
from datetime import datetime

# API endpoint
API_URL = "http://75.131.29.55:5100/add-medical"

def send_data():
    """
    Generates a random heart rate value with a timestamp and sends it to the API.
    """
    while True:
        # Generate a simulated heart rate value
        sensor_value = round(random.uniform(70, 80), 2)
        timestamp = time.time()  # Get current Unix timestamp

        # Prepare the payload
        payload = {
            "type": "heart_rate",
            "timestamp": timestamp,  # Send timestamp
            "value": sensor_value
        }

        try:
            # Send the POST request
            response = requests.post(API_URL, json=payload)
            
            # Print response status and data
            if response.status_code == 200:
                print(f"Sent: {json.dumps(payload)} | Response: {response.text}")
            else:
                print(f"Failed to send data. Status Code: {response.status_code}")
        
        except Exception as e:
            print(f"Error sending data: {e}")

        # Wait before sending the next request
        time.sleep(2)  # Send every 2 seconds

if __name__ == "__main__":
    send_data()
