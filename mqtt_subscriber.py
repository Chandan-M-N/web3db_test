import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Subscribe and plot data from an MQTT topic.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the MQTT broker host (default: 75.131.29.55)")
    parser.add_argument('--t', '--topic', type=str, default="sensor/heart_rate",
                        help="Specify the MQTT topic to subscribe to (default: sensor/heart_rate)")
    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_topic = args.t

print(f"You selected host {selected_host} and topic {selected_topic}.")

# MQTT Broker Settings
BROKER = selected_host  # Hostname from command-line argument
PORT = 1883

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, y_data = [], []  # Lists to store timestamps and sensor values
data_labels = []  # List to store labels for the data being plotted

def on_message(client, userdata, msg):
    global timestamps, y_data, data_labels
    
    # Decode the received message
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        print(f"Received data: {data}")  # Debug: Print received data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    
    # Extract timestamp and convert to human-readable format
    timestamp = data.get("timestamp")
    if not timestamp:
        print("Error: Missing 'timestamp' in received data")
        return
    
    try:
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return
    
    # Append new timestamp
    timestamps.append(human_readable_time)
    
    # Extract data values based on the structure of the payload
    if "value" in data:  # Single value (e.g., heart rate)
        y_data.append([data["value"]])  # Wrap in a list for consistency
        if not data_labels:
            data_labels.append("value")  # Add label if not already present
    else:  # Multiple values (e.g., blood pressure)
        values = []
        for key, value in data.items():
            if key not in ["type", "timestamp"]:  # Skip metadata fields
                values.append(value)
                if key not in data_labels:
                    data_labels.append(key)  # Add label if not already present
        y_data.append(values)
    
    # Keep only the last 20 data points for visualization
    timestamps = timestamps[-20:]
    y_data = y_data[-20:]
    
    # Clear and update plot
    ax.clear()
    
    # Plot all data values
    for i, label in enumerate(data_labels):
        ax.plot(timestamps, [values[i] for values in y_data], marker='o', linestyle='-', label=label)
    
    # Set common plot properties
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title(f"Data received from host {selected_host} for topic: {selected_topic}")
    ax.legend()  # Show legend for multiple lines
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.pause(0.5)  # Refresh every 0.5 seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(selected_topic)
    else:
        print("Failed to connect, return code:", rc)

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, PORT, 60)
        print(f"Starting MQTT subscriber for topic: {selected_topic}")
        client.loop_forever()  # Keep listening for messages
    except Exception as e:
        print(f"Error: {e}")