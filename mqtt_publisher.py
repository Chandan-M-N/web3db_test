import paho.mqtt.client as mqtt
import time
import random
import json
import matplotlib.pyplot as plt
from datetime import datetime

def get_user_choice(prompt, options):
    while True:
        choice = input(prompt)
        if choice in options:
            return choice
        print("Invalid input. Please enter a valid option.")

# Ask for host selection
host_options = {"1": "75.131.29.55", "2": "162.192.60.88"}
host_choice = get_user_choice("Which host do you want to send data? Please choose the options:\n1. 75.131.29.55\n2. 162.192.60.88\nEnter your choice: ", host_options.keys())
selected_host = host_options[host_choice]

# Ask for vital selection
vital_options = {"1": "Heart Rate", "2": "Blood Pressure"}
vital_choice = get_user_choice("What vitals do you want to send?\n1. Heart Rate\n2. Blood Pressure\nEnter your choice: ", vital_options.keys())
selected_vital = vital_options[vital_choice]

print(f"You selected host {selected_host} and vital {selected_vital}.")



# MQTT Broker Settings
BROKER = selected_host  # Hostname from config.json
PORT = 1883
if selected_vital == "Heart Rate":
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
        ax.set_title(f"Published {VITALS_TYPE.replace('_', ' ').title()} Data Stream")
        ax.legend()  # Show legend for multiple lines
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.pause(0.5)  # Refresh every 0.5 seconds

        # Wait before publishing the next data point
        time.sleep(1)

if __name__ == "__main__":
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    publish_data(client)