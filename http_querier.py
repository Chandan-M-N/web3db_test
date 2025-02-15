import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Query and plot vital signs data via HTTP.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the API host (default: 75.131.29.55)")
    parser.add_argument('--v', '--vital', type=str, default="heart_rate",
                        choices=["heart_rate", "blood_pressure"],
                        help="Specify the vital sign to query (default: heart_rate)")
    return parser.parse_args()

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_vital = args.v

print(f"You selected host {selected_host} and vital {selected_vital}.")

# API endpoint and payload
API_URL = f"http://{selected_host}:5100/fetch-medical"  # Host and port from command-line argument
if selected_vital == "heart_rate":
    VITALS_TYPE = "heart_rate"
else:
    VITALS_TYPE = "blood_pressure"
PAYLOAD = {"type": VITALS_TYPE}  # Dynamic payload based on vitals type

# Lists to store timestamps and values
timestamps = []
values = []
sys_values = []  # For blood pressure systolic values
dia_values = []  # For blood pressure diastolic values

# Track the last plotted med_type_id
last_plotted_id = None

# Get the initial timestamp when the script starts
initial_timestamp = time.time()

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, sys_data, dia_data, y_data = [], [], [], []  # Separate lists for sys, dia, and heart rate values

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
                                if VITALS_TYPE == "heart_rate" and "value" in entry and entry["value"] is not None:
                                    value = float(entry["value"])
                                    timestamps.append(timestamp_str)
                                    values.append(value)
                                elif VITALS_TYPE == "blood_pressure" and "sys" in entry and "dia" in entry and entry["sys"] is not None and entry["dia"] is not None:
                                    sys_value = float(entry["sys"])
                                    dia_value = float(entry["dia"])
                                    timestamps.append(timestamp_str)
                                    sys_values.append(sys_value)
                                    dia_values.append(dia_value)
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

    

    # Plot the data based on vitals type
    if VITALS_TYPE == "heart_rate":
        ax.plot(timestamps, values, marker='o', linestyle='-', label="Heart Rate (BPM)")
        ax.set_ylabel("Heart Rate (BPM)")
    elif VITALS_TYPE == "blood_pressure":
        ax.plot(timestamps, sys_values, marker='o', linestyle='-', label="Systolic (mmHg)")
        ax.plot(timestamps, dia_values, marker='o', linestyle='-', label="Diastolic (mmHg)")
        ax.set_ylabel("Blood Pressure (mmHg)")

    # Set common plot properties
    ax.set_xlabel("Time")
    ax.set_title(f"{VITALS_TYPE.replace('_', ' ').title()} data queried from host {selected_host}")
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