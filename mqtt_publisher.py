import paho.mqtt.client as mqtt
import time
import random
import json
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Publish and plot vital signs data.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the MQTT broker host (default: 75.131.29.55)")
    parser.add_argument('--v', '--vital', type=str, default="heart_rate",
                        choices=["heart_rate", "blood_pressure"],
                        help="Specify the vital sign to publish (default: heart_rate)")
    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_vital = args.v

print(f"You selected host {selected_host} and vital {selected_vital}.")

# MQTT Broker Settings
BROKER = selected_host  # Hostname from command-line argument
PORT = 1883
if selected_vital == "heart_rate":
    TOPIC = "sensor/heart_rate"
    VITALS_TYPE = "heart_rate"
else:
    TOPIC = "sensor/blood_pressure"
    VITALS_TYPE = "blood_pressure"

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, sys_data, dia_data, y_data = [], [], [], []  # Separate lists for sys, dia, and heart rate values

def publish_data(client):
    while True:
        # Simulate sensor data based on vitals type
        if VITALS_TYPE == "heart_rate":
            sensor_value = round(random.uniform(70.0, 80.0), 2)  # Simulated heart rate data
            data = {
                "type": VITALS_TYPE,
                "timestamp": time.time(),
                "value": sensor_value
            }
        elif VITALS_TYPE == "blood_pressure":
            sys_value = round(random.uniform(110, 130), 2)  # Simulated systolic pressure
            dia_value = round(random.uniform(70, 90), 2)   # Simulated diastolic pressure
            data = {
                "type": VITALS_TYPE,
                "timestamp": time.time(),
                "sys": sys_value,
                "dia": dia_value
            }
        else:
            raise ValueError(f"Unsupported vitals type: {VITALS_TYPE}")

        # Convert timestamp to human-readable format
        timestamp = data["timestamp"]
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        # Publish to MQTT broker
        client.publish(TOPIC, json.dumps(data))
        print(f"Published: {data}")

        # Update plot data
        timestamps.append(human_readable_time)  # Use human-readable time for x-axis

        if VITALS_TYPE == "heart_rate":
            y_data.append(data["value"])  # Append heart rate value
        elif VITALS_TYPE == "blood_pressure":
            sys_data.append(data["sys"])  # Append systolic value
            dia_data.append(data["dia"])  # Append diastolic value

        # Clear the previous plot
        ax.clear()

        # Plot the data based on vitals type
        if VITALS_TYPE == "heart_rate":
            ax.plot(timestamps, y_data, marker='o', linestyle='-', label="Heart Rate (BPM)")
            ax.set_ylabel("Heart Rate (BPM)")
        elif VITALS_TYPE == "blood_pressure":
            ax.plot(timestamps, sys_data, marker='o', linestyle='-', label="Systolic (mmHg)")
            ax.plot(timestamps, dia_data, marker='o', linestyle='-', label="Diastolic (mmHg)")
            ax.set_ylabel("Blood Pressure (mmHg)")

        # Set common plot properties
        ax.set_xlabel("Time")
        ax.set_title(f"{VITALS_TYPE.replace('_', ' ').title()} data published to host {selected_host}")
        ax.legend()  # Show legend for multiple lines
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.pause(0.5)  # Refresh every 0.5 seconds

        # Wait before publishing the next data point
        time.sleep(2)

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    publish_data(client)