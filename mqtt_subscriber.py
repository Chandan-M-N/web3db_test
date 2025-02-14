import paho.mqtt.client as mqtt
import json
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


# MQTT Broker Settings
BROKER = selected_host  # Hostname from config.json
PORT = 1883
if selected_vital == "Heart Rate":
    TOPIC = "sensor/heart_rate"
    VITALS_TYPE = "heart_rate"
else:
    TOPIC = "sensor/blood_pressure"
    VITALS_TYPE = "blood_pressure"

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, sys_data, dia_data, y_data = [], [], [], []  # Lists to store timestamps and sensor values

def on_message(client, userdata, msg):
    global timestamps, y_data, sys_data, dia_data
    
    # Decode the received message
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        print(f"Raw received data: {data}")  # Debug: Print raw received data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return
    
    # Check if the received data type matches the expected vitals type
    if data.get("type") == VITALS_TYPE:
        timestamp = data.get("timestamp")
        if not timestamp:
            print("Error: Missing 'timestamp' in received data")
            return
        
        # Convert timestamp to human-readable format
        try:
            human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        except Exception as e:
            print(f"Error converting timestamp: {e}")
            return
        
        # Append new data based on vitals type
        timestamps.append(human_readable_time)
        print(f"Processed timestamp: {human_readable_time}")  # Debug: Print processed timestamp
        
        if VITALS_TYPE == "heart_rate":
            value = data.get("value")
            if value is None:
                print("Error: Missing 'value' in received data")
                return
            y_data.append(value)  # Append heart rate value
            print(f"Processed heart rate value: {value}")  # Debug: Print processed value
        elif VITALS_TYPE == "blood_pressure":
            sys_value = data.get("sys")
            dia_value = data.get("dia")
            if sys_value is None or dia_value is None:
                print("Error: Missing 'sys' or 'dia' in received data")
                return
            sys_data.append(sys_value)  # Append systolic value
            dia_data.append(dia_value)  # Append diastolic value
            print(f"Processed systolic value: {sys_value}, diastolic value: {dia_value}")  # Debug: Print processed values
        
        # Keep only the last 20 data points for visualization
        timestamps = timestamps[-20:]
        y_data = y_data[-20:]
        sys_data = sys_data[-20:]
        dia_data = dia_data[-20:]
        
        # Clear and update plot
        ax.clear()
        
        if VITALS_TYPE == "heart_rate":
            ax.plot(timestamps, y_data, marker='o', linestyle='-', label="Heart Rate (BPM)")
            ax.set_ylabel("Heart Rate (BPM)")
        elif VITALS_TYPE == "blood_pressure":
            ax.plot(timestamps, sys_data, marker='o', linestyle='-', label="Systolic (mmHg)")
            ax.plot(timestamps, dia_data, marker='o', linestyle='-', label="Diastolic (mmHg)")
            ax.set_ylabel("Blood Pressure (mmHg)")
        
        # Set common plot properties
        ax.set_xlabel("Time")
        ax.set_title(f"Received {VITALS_TYPE.replace('_', ' ').title()} Data Stream")
        ax.legend()  # Show legend for multiple lines
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.pause(0.5)  # Refresh every 0.5 seconds
        
        print(f"Processed and plotted data: {data}")  # Debug: Print processed and plotted data
    else:
        print(f"Ignored data (type mismatch): {data}")  # Debug: Print ignored data

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print("Failed to connect, return code:", rc)

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    
    print(f"Starting MQTT subscriber for topic: {TOPIC}")  # Debug: Print topic
    client.loop_forever()  # Keep listening for messages