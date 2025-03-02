import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Query and plot data from an HTTP API.")
    parser.add_argument('--h', '--host', type=str, default="129.74.152.201",
                        help="Specify the API host (default: 129.74.152.201)")
    parser.add_argument('--t', '--topic', type=str, default="heart_rate",
                        help="Specify the topic to query (default: heart_rate)")
    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_topic = args.t

print(f"You selected host {selected_host} and topic {selected_topic}.")

# API endpoint and payload
API_URL = f"http://{selected_host}:5100/get-medical"  # Host and port from command-line argument
PAYLOAD = {"time": "5 secs","topic": selected_topic}  # Dynamic payload based on the selected topic

# Lists to store timestamps and values
timestamps = []
data_values = {}  # Dictionary to store values for each field (e.g., "value", "sys", "dia")

# Track the last plotted timestamp
last_plotted_timestamp = None

# Get the initial timestamp when the script starts
initial_timestamp = time.time()

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()

# Maximum number of data points to display
MAX_POINTS = 20  # You can adjust this value as needed

def normalize_timestamp(timestamp_value):
    """
    Converts various timestamp formats to a Unix timestamp in seconds.
    """
    try:
        # If it's already a float/int, check the magnitude to determine format
        if isinstance(timestamp_value, (int, float)):
            timestamp = float(timestamp_value)
            # Nanoseconds (19 digits)
            if timestamp > 1e18:
                return timestamp / 1e9
            # Microseconds (16 digits)
            elif timestamp > 1e15:
                return timestamp / 1e6
            # Milliseconds (13 digits)
            elif timestamp > 1e12:
                return timestamp / 1e3
            # Seconds (10 digits) - return as is
            else:
                return timestamp
        # If it's a string, try parsing it
        elif isinstance(timestamp_value, str):
            try:
                # First try parsing as float/int
                return normalize_timestamp(float(timestamp_value))
            except ValueError:
                # If that fails, assume it's a datetime string
                # Add more datetime formats here if needed
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S.%f",
                ]:
                    try:
                        dt = datetime.strptime(timestamp_value, fmt)
                        return dt.timestamp()
                    except ValueError:
                        continue
                raise ValueError(f"Unrecognized timestamp format: {timestamp_value}")
    except Exception as e:
        print(f"Error normalizing timestamp {timestamp_value}: {e}")
        return None

def fetch_data():
    """
    Fetches data from the API and updates the timestamps and values lists.
    """
    global last_plotted_timestamp, data_values, timestamps

    try:
        response = requests.get(API_URL, json=PAYLOAD)
        if response.status_code == 200:
            outer_data = json.loads(response.text)
            if outer_data == "Data does not exists!!":
                return
            if isinstance(outer_data, dict) and "data" in outer_data:
                for entry in outer_data["data"]:
                    if "timestamp" in entry:
                        # Convert timestamp using the new normalize_timestamp function
                        raw_timestamp = entry["timestamp"]
                        normalized_timestamp = normalize_timestamp(raw_timestamp)
                        
                        if normalized_timestamp is None:
                            continue
                            
                        if normalized_timestamp >= initial_timestamp and (last_plotted_timestamp is None or normalized_timestamp > last_plotted_timestamp):
                            timestamp_str = datetime.fromtimestamp(normalized_timestamp).strftime("%H:%M:%S")
                            timestamps.append(timestamp_str)
                            
                            # Iterate over all keys in the entry (except "timestamp")
                            for key, value in entry.items():
                                if key != "timestamp" and value is not None:
                                    if key not in data_values:
                                        data_values[key] = []
                                    data_values[key].append(float(value))
                            
                            last_plotted_timestamp = normalized_timestamp

                            # Trim data to only keep the last MAX_POINTS entries
                            if len(timestamps) > MAX_POINTS:
                                timestamps.pop(0)
                                for key in data_values:
                                    if len(data_values[key]) > MAX_POINTS:
                                        data_values[key].pop(0)
    except Exception as e:
        print(f"Error fetching data: {e}")

def update_plot():
    """
    Updates the plot with only the new entries.
    """
    if len(timestamps) == 0:
        return

    # Clear the previous plot
    ax.clear()

    # Plot the data for each field
    for field, values in data_values.items():
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