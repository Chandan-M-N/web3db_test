import paho.mqtt.client as mqtt
import time
import random
import json
import matplotlib.pyplot as plt
from datetime import datetime

# MQTT Broker Settings
BROKER = "75.131.29.55"
PORT = 1883
TOPIC = "sensor/data"

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, y_data = [], []  # Use timestamps for x-axis

def publish_data(client):
    while True:
        # Simulate sensor data
        sensor_value = round(random.uniform(70.0, 80.0), 2)  # Simulated heart rate data
        timestamp = time.time()  # Get current Unix timestamp

        # Convert timestamp to human-readable format
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        # Prepare data for publishing
        data = {"type": "heart_rate", "timestamp": timestamp, "value": sensor_value}

        # Publish to MQTT broker
        client.publish(TOPIC, json.dumps(data))
        print(f"Published: {data}")

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

        # Wait before publishing the next data point
        time.sleep(1)

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    publish_data(client)
