import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime
import json

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



# API endpoint and payload
API_URL = f"http://{selected_host}:5100/fetch-medical"  # Host and port from config.json
if selected_vital == "Heart Rate":
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

# Create the figure and axis once
plt.figure(figsize=(10, 6))
ax = plt.gca()  # Get the current axis
if VITALS_TYPE == "heart_rate":
    line, = ax.plot([], [], marker="o", linestyle="-", color="b", label="Heart Rate (BPM)")
elif VITALS_TYPE == "blood_pressure":
    sys_line, = ax.plot([], [], marker="o", linestyle="-", color="r", label="Systolic (mmHg)")
    dia_line, = ax.plot([], [], marker="o", linestyle="-", color="g", label="Diastolic (mmHg)")
plt.title(f"{VITALS_TYPE.replace('_', ' ').title()} Over Time (From Start Time)")
plt.xlabel("Timestamp")
plt.ylabel(f"{VITALS_TYPE.replace('_', ' ').title()} Values")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.grid(True)
plt.legend()  # Show legend for multiple lines
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

    # Print the new entries
    print("Queried and response is followed by data of new entries:")
    if VITALS_TYPE == "heart_rate":
        for timestamp, value in zip(timestamps, values):
            print(f"Timestamp: {timestamp}, Value: {value}")
    elif VITALS_TYPE == "blood_pressure":
        for timestamp, sys_value, dia_value in zip(timestamps, sys_values, dia_values):
            print(f"Timestamp: {timestamp}, Systolic: {sys_value}, Diastolic: {dia_value}")

    # Update the plot data with new points
    if VITALS_TYPE == "heart_rate":
        line.set_xdata(range(len(timestamps)))  # Use indices for x-axis
        line.set_ydata(values)
    elif VITALS_TYPE == "blood_pressure":
        sys_line.set_xdata(range(len(timestamps)))  # Use indices for x-axis
        sys_line.set_ydata(sys_values)
        dia_line.set_xdata(range(len(timestamps)))  # Use indices for x-axis
        dia_line.set_ydata(dia_values)

    # Adjust the x-axis limits
    ax.set_xlim(0, len(timestamps) - 1)

    # Adjust the y-axis limits
    if VITALS_TYPE == "heart_rate":
        ax.set_ylim(min(values) - 1, max(values) + 1)
    elif VITALS_TYPE == "blood_pressure":
        ax.set_ylim(min(min(sys_values), min(dia_values)) - 1, max(max(sys_values), max(dia_values)) + 1)

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