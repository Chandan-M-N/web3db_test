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

# Create the figure and axis once
plt.figure(figsize=(10, 6))
ax = plt.gca()  # Get the current axis
line, = ax.plot([], [], marker="o", linestyle="-", color="b")  # Create an empty line plot
plt.title("Heart Rate Over Time (Last 10 Entries)")
plt.xlabel("Timestamp")
plt.ylabel("Heart Rate (BPM)")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.grid(True)
plt.tight_layout()

def fetch_data():
    """
    Fetches data from the API and updates the timestamps and values lists.
    """
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
                        if "timestamp" in entry and "value" in entry:  # Validate keys
                            # Convert timestamp to a readable format
                            timestamp = datetime.fromtimestamp(float(entry["timestamp"])).strftime("%H:%M:%S")
                            value = float(entry["value"])
                            timestamps.append(timestamp)
                            values.append(value)
    except Exception as e:
        print(f"Error fetching data: {e}")

def update_plot():
    """
    Updates the plot with the latest 10 entries.
    """
    if len(timestamps) == 0 or len(values) == 0:
        print("No data to plot.")
        return

    # Get the last 10 entries
    last_10_timestamps = timestamps[-10:]
    last_10_values = values[-10:]

    # Print the last 10 entries
    print("Queried and response is followed by data:")
    for timestamp, value in zip(last_10_timestamps, last_10_values):
        print(f"Timestamp: {timestamp}, Value: {value}")

    # Update the plot data
    line.set_xdata(range(len(last_10_timestamps)))  # Use indices for x-axis
    line.set_ydata(last_10_values)

    # Adjust the x-axis limits
    ax.set_xlim(0, len(last_10_timestamps) - 1)

    # Adjust the y-axis limits
    ax.set_ylim(min(last_10_values) - 1, max(last_10_values) + 1)

    # Set x-axis tick labels to timestamps
    ax.set_xticks(range(len(last_10_timestamps)))
    ax.set_xticklabels(last_10_timestamps, rotation=45)

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
