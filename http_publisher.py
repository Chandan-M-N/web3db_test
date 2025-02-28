import requests
import time
import json
import random
import matplotlib.pyplot as plt
from datetime import datetime
import argparse
import sys

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Publish and plot custom sensor data via HTTP.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the API host (default: 75.131.29.55)")
    parser.add_argument('--t', '--topic', type=str, default="sensor/heart_rate",
                        help="Specify the type of data (default: sensor/heart_rate)")
    parser.add_argument('--v', '--vitals', type=str, default="value",
                        help="Specify the value names for the data, separated by commas (default: value)")
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

# API endpoint
API_URL = f"http://{selected_host}:5100/add-medical"  # Host and port from command-line argument

# Initialize Matplotlib figure
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
timestamps, y_data = [], [[] for _ in selected_vitals]  # Separate lists for each value name

# Maximum number of data points to display
MAX_POINTS = 20  # You can adjust this value as needed

def send_data():
    """
    Generates random sensor values with timestamps, sends them to the API, and plots the data.
    """
    global timestamps, y_data  # Declare global variables

    while True:
        # Generate sensor data based on value names and ranges
        payload = {
            "topic": selected_topic,
            "payload": {
                "timestamp": time.time(),  # Send timestamp
            },
            
        }

        # Generate random values within the specified ranges for each value name
        for i, vital in enumerate(selected_vitals):
            min_val, max_val = ranges[i]
            payload['payload'][vital] = round(random.uniform(min_val, max_val), 2)
            y_data[i].append(payload['payload'][vital])  # Append the value to its corresponding list
        # Convert timestamp to human-readable format
        timestamp = payload["payload"]["timestamp"]
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        try:
            # Send the POST request
            response = requests.post(API_URL, json=payload)
        
        except Exception as e:
            print(f"Error sending data: {e}")

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

        # Wait before sending the next request
        time.sleep(4)  # Send every 2 seconds

if __name__ == "__main__":
    try:
        send_data()
    except KeyboardInterrupt:
        print("Script terminated by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)