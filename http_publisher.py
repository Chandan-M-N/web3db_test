import requests
import time
import json
import random
import matplotlib.pyplot as plt
from datetime import datetime

# API endpoint
API_URL = "http://75.131.29.55:5100/add-medical"

# Initialize Matplotlib figure
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
timestamps, y_data = [], []  # Lists to store timestamps and sensor values

def send_data():
    """
    Generates a random heart rate value with a timestamp, sends it to the API, and plots the data.
    """
    while True:
        # Generate a simulated heart rate value
        sensor_value = round(random.uniform(70, 80), 2)
        timestamp = time.time()  # Get current Unix timestamp

        # Convert timestamp to human-readable format
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

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

        # Update plot data
        timestamps.append(human_readable_time)  # Use human-readable time for x-axis
        y_data.append(sensor_value)

        # Clear the previous plot
        ax.clear()

        # Plot the data
        ax.plot(timestamps, y_data, marker='o', linestyle='-')
        ax.set_xlabel("Time")
        ax.set_ylabel("Heart Rate (BPM)")
        ax.set_title("Published Sensor Data Stream")

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Refresh the plot
        plt.pause(0.5)  # Refresh every 0.5 seconds

        # Wait before sending the next request
        time.sleep(1)  # Send every 2 seconds

if __name__ == "__main__":
    send_data()
