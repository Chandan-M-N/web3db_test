import requests
import time
import json
import random
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



# API endpoint
API_URL = f"http://{selected_host}:5100/add-medical"  # Host and port from config.json
if selected_vital == "Heart Rate":
    VITALS_TYPE = "heart_rate"
else:
    VITALS_TYPE = "blood_pressure"

# Initialize Matplotlib figure
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots()
timestamps, sys_data, dia_data, y_data = [], [], [], []  # Lists to store timestamps and sensor values

def send_data():
    """
    Generates a random sensor value with a timestamp, sends it to the API, and plots the data.
    """
    while True:
        # Generate a simulated sensor value based on vitals type
        if VITALS_TYPE == "heart_rate":
            sensor_value = round(random.uniform(70, 80), 2)  # Simulated heart rate data
            payload = {
                "type": VITALS_TYPE,
                "timestamp": time.time(),  # Send timestamp
                "value": sensor_value
            }
        elif VITALS_TYPE == "blood_pressure":
            sys_value = round(random.uniform(110, 130), 2)  # Simulated systolic pressure
            dia_value = round(random.uniform(70, 90), 2)   # Simulated diastolic pressure
            payload = {
                "type": VITALS_TYPE,
                "timestamp": time.time(),  # Send timestamp
                "sys": sys_value,
                "dia": dia_value
            }
        else:
            raise ValueError(f"Unsupported vitals type: {VITALS_TYPE}")

        # Convert timestamp to human-readable format
        timestamp = payload["timestamp"]
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

        try:
            # Send the POST request
            response = requests.post(API_URL, json=payload)
            
            # Print response status and data
            if response.status_code == 200:
                print(f"Sent: {json.dumps(payload)} | Response: {response.text}")
            else:
                print(f"Failed to send data. Status Code: {response.status_code}")
        
        except Exception as e:
            print(f"Error sending data: {e}")

        # Update plot data
        timestamps.append(human_readable_time)  # Use human-readable time for x-axis

        if VITALS_TYPE == "heart_rate":
            y_data.append(payload["value"])  # Append heart rate value
        elif VITALS_TYPE == "blood_pressure":
            sys_data.append(payload["sys"])  # Append systolic value
            dia_data.append(payload["dia"])  # Append diastolic value

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

        # Wait before sending the next request
        time.sleep(1)  # Send every 1 second

if __name__ == "__main__":
    send_data()