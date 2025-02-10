import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json

# API endpoint and payload
API_URL = "http://75.131.29.55:5100/fetch-medical"
PAYLOAD = {"type": "heart_rate"}

# Lists to store timestamps and values
timestamps = []
values = []

# Track the last plotted med_type_id
last_plotted_id = None

# Get the initial timestamp when the script starts
initial_timestamp = time.time()

# Create the figure and axis once
plt.figure(figsize=(10, 6))
ax = plt.gca()  # Get the current axis
line, = ax.plot([], [], marker="o", linestyle="-", color="b")  # Create an empty line plot
plt.title("Heart Rate Over Time (From Start Time)")
plt.xlabel("Timestamp")
plt.ylabel("Heart Rate (BPM)")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.grid(True)
plt.tight_layout()

def fetch_data():
    """
    Fetches data from the API and updates the timestamps and values lists.
    """
    global last_plotted_id  # Use the global variable to track the last plotted med_type_id

    try:
        response = requests.post(API_URL, json=PAYLOAD)
        if response.status_code == 200:
            # Step 1: Parse the outer JSON string
            outer_data = json.loads(response.text)

            # Step 2: Parse the inner JSON string
            if isinstance(outer_data, str):  # Check if the outer data is a string
                inner_data = json.loads(outer_data)  # Parse the inner JSON string
                if isinstance(inner_data, list):  # Ensure the inner data is a list
                    for entry in inner_data:
                        if "timestamp" in entry and "value" in entry and "med_type_id" in entry:  # Validate keys
                            # Convert timestamp to a readable format
                            timestamp = float(entry["timestamp"])
                            med_type_id = int(entry["med_type_id"])  # Get the unique med_type_id
                            if timestamp >= initial_timestamp and (last_plotted_id is None or med_type_id > last_plotted_id):
                                timestamp_str = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                                value = float(entry["value"])
                                timestamps.append(timestamp_str)
                                values.append(value)
                                last_plotted_id = med_type_id  # Update the last plotted med_type_id
    except Exception as e:
        print(f"Error fetching data: {e}")

def update_plot():
    """
    Updates the plot with only the new entries.
    """
    if len(timestamps) == 0 or len(values) == 0:
        print("No data to plot.")
        return

    # Print the new entries
    print("Queried and response is followed by data of new entries:")
    for timestamp, value in zip(timestamps, values):
        print(f"Timestamp: {timestamp}, Value: {value}")

    # Update the plot data with new points
    line.set_xdata(range(len(timestamps)))  # Use indices for x-axis
    line.set_ydata(values)

    # Adjust the x-axis limits
    ax.set_xlim(0, len(timestamps) - 1)

    # Adjust the y-axis limits
    ax.set_ylim(min(values) - 1, max(values) + 1)

    # Set x-axis tick labels to timestamps
    ax.set_xticks(range(len(timestamps)))
    ax.set_xticklabels(timestamps, rotation=45)

    # Redraw the plot
    plt.draw()
    plt.pause(0.1)

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
