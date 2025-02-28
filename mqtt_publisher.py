import paho.mqtt.client as mqtt
import time
import random
import json
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import sys

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Publish and plot custom sensor data.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the MQTT broker host (default: 75.131.29.55)")
    parser.add_argument('--t', '--topic', type=str, default="heart_rate",
                        help="Specify the MQTT topic (default: heart_rate)")
    parser.add_argument('--v', '--vitals', type=str, default="value",
                        help="Specify the value names for the topic, separated by commas (default: value)")
    parser.add_argument('--r', '--range', type=str, default="70,80",
                        help="Specify the range of values for each vital, separated by commas. For multiple vitals, provide ranges like 'min1,max1,min2,max2' (default: 70,80)")
    return parser.parse_args()

# Function to validate and parse ranges
def parse_ranges(range_str, num_vitals):
    try:
        range_values = list(map(float, range_str.split(',')))
    except ValueError:
        raise ValueError("Invalid range values. Ranges must be numeric and separated by commas.")

    if len(range_values) != 2 * num_vitals:
        raise ValueError(f"Number of range values must match the number of vitals. Expected {2 * num_vitals} values, got {len(range_values)}.")

    # Group ranges into pairs of (min, max)
    ranges = []
    for i in range(0, len(range_values), 2):
        min_val, max_val = range_values[i], range_values[i + 1]
        if min_val >= max_val:
            raise ValueError(f"Invalid range: min value {min_val} must be less than max value {max_val}.")
        ranges.append((min_val, max_val))

    return ranges

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_topic = args.t
selected_vitals = args.v.split(',')  # Split value names by comma

try:
    ranges = parse_ranges(args.r, len(selected_vitals))  # Parse and validate ranges
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

print(f"You selected host {selected_host}, topic {selected_topic}, vitals {selected_vitals}, and ranges {ranges}.")

# MQTT Broker Settings
BROKER = selected_host  # Hostname from command-line argument
PORT = 1883
TOPIC = f"sensor/{selected_topic}"

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, y_data = [], [[] for _ in selected_vitals]  # Separate lists for each value name

# Maximum number of data points to display
MAX_POINTS = 20  # You can adjust this value as needed

def publish_data(client):
    while True:
        # Simulate sensor data based on value names
        data = {
            "timestamp": time.time(),
        }

        # Generate random values within the specified ranges for each value name
        for i, vital in enumerate(selected_vitals):
            min_val, max_val = ranges[i]
            data[vital] = round(random.uniform(min_val, max_val), 2)
            y_data[i].append(data[vital])  # Append the value to its corresponding list

        # Convert timestamp to human-readable format
        timestamp = data["timestamp"]
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        # Publish to MQTT broker
        client.publish(TOPIC, json.dumps(data))

        # Update plot data
        timestamps.append(human_readable_time)  # Use human-readable time for x-axis

        # Trim data to only keep the last MAX_POINTS entries
        if len(timestamps) > MAX_POINTS:
            timestamps.pop(0)
            for i in range(len(y_data)):
                if len(y_data[i]) > MAX_POINTS:
                    y_data[i].pop(0)

        # Clear the previous plot
        ax.clear()

        # Plot the data for each value name
        for i, vital in enumerate(selected_vitals):
            ax.plot(timestamps, y_data[i], marker='o', linestyle='-', label=f"{vital}")

        # Set common plot properties
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.set_title(f"{selected_topic.replace('_', ' ').title()} data published to host {selected_host}")
        ax.legend()  # Show legend for multiple lines
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.pause(0.5)  # Refresh every 0.5 seconds

        # Wait before publishing the next data point
        time.sleep(4)

if __name__ == "__main__":
    client = mqtt.Client()
    try:
        client.connect(BROKER, PORT, 60)
        publish_data(client)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)