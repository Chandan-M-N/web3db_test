import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Query and plot data from an HTTP API.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the API host (default: 75.131.29.55)")
    parser.add_argument('--t', '--topic', type=str, default="heart_rate",
                        help="Specify the topic to query (default: heart_rate)")
    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_topic = args.t

print(f"You selected host {selected_host} and topic {selected_topic}.")

# API endpoint and payload
API_URL = f"http://{selected_host}:5100/fetch-medical"  # Host and port from command-line argument
PAYLOAD = {"type": selected_topic}  # Dynamic payload based on the selected topic

# Lists to store timestamps and values
timestamps = []
data_values = {}  # Dictionary to store values for each field (e.g., "value", "sys", "dia")

# Track the last plotted med_type_id
last_plotted_id = None

# Get the initial timestamp when the script starts
initial_timestamp = time.time()

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()

def fetch_data():
    """
    Fetches data from the API and updates the timestamps and values lists.
    """
    global last_plotted_id, data_values

    try:
        response = requests.post(API_URL, json=PAYLOAD)
        if response.status_code == 200:
            # Step 1: Parse the outer JSON string
            outer_data = json.loads(response.text)
            if outer_data == "Data does not exists!!":
                print("No data received.")
                return
            # Step 2: Parse the inner JSON string
            if isinstance(outer_data, str):  # Check if the outer data is a string
                inner_data = json.loads(outer_data)  # Parse the inner JSON string
                if isinstance(inner_data, list):  # Ensure the inner data is a list
                    for entry in inner_data:
                        if "timestamp" in entry and "med_type_id" in entry:  # Validate keys
                            # Convert timestamp to a readable format
                            timestamp = float(entry["timestamp"])
                            med_type_id = int(entry["med_type_id"])  # Get the unique med_type_id
                            if timestamp >= initial_timestamp and (last_plotted_id is None or med_type_id > last_plotted_id):
                                timestamp_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                                timestamps.append(timestamp_str)
                                # Extract all fields except "type", "timestamp", and "med_type_id"
                                for key, value in entry.items():
                                    if key not in ["type", "timestamp", "med_type_id"] and value is not None:
                                        if key not in data_values:
                                            data_values[key] = []  # Initialize list for new field
                                        data_values[key].append(float(value))
                                last_plotted_id = med_type_id  # Update the last plotted med_type_id
    except Exception as e:
        print(f"Error fetching data: {e}")

def update_plot():
    """
    Updates the plot with only the new entries.
    """
    if len(timestamps) == 0:
        print("No data to plot.")
        return

    # Clear the previous plot
    ax.clear()

    # Plot the data for each field
    for field, values in data_values.items():
        print(field, values[-1])
        ax.plot(timestamps, values, marker='o', linestyle='-', label=field)

    # Set common plot properties
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title(f"Data queried from host {selected_host} for topic: {selected_topic}")
    ax.legend()  # Show legend for multiple lines
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.pause(0.5)  # Refresh every 0.5 seconds

def main():
    """
    Main function to fetch data every 2 seconds and update the plot.
    """
    try:
        while True:
            fetch_data()
            update_plot()
            time.sleep(2)  # Wait for 2 seconds before the next request
    except KeyboardInterrupt:
        print("Script stopped by user.")

if __name__ == "__main__":
    main()