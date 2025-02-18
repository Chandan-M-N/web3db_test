import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Subscribe and plot data from an MQTT topic.")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Specify the MQTT broker host (default: 75.131.29.55)")
    parser.add_argument('--t', '--topic', type=str, default="sensor/heart_rate",
                        help="Specify the MQTT topic to subscribe to (default: sensor/heart_rate)")
    return parser.parse_args()

def parse_message(payload):
    # First try JSON format
    try:
        if isinstance(payload, bytes):
            data = json.loads(payload.decode("utf-8"))
            return data
    except json.JSONDecodeError:
        # If JSON fails, try key-value format
        try:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
                
            # Split the string by semicolons and create a dictionary
            pairs = payload.split(';')
            data = {}
            current_timestamp = None
            
            for pair in pairs:
                pair = pair.strip()
                if not pair:
                    continue
                    
                key, value = pair.split('=')
                key = key.strip()
                value = value.strip()
                
                # Try to convert numeric values
                try:
                    value = float(value)
                except ValueError:
                    pass  # Keep as string if conversion fails
                
                # Handle timestamp specially
                if key == 'timestamp':
                    current_timestamp = value
                    if 'timestamp' not in data:
                        data['timestamp'] = value
                else:
                    # Store other values with their corresponding timestamp
                    data[key] = value
                    
            return data
            
        except Exception as e:
            print(f"Error parsing key-value format: {e}")
            return None

# Parse command-line arguments
args = parse_arguments()
selected_host = args.h
selected_topic = args.t

print(f"You selected host {selected_host} and topic {selected_topic}.")

# MQTT Broker Settings
BROKER = selected_host
PORT = 1883

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, y_data = [], []  # Lists to store timestamps and sensor values
data_labels = []  # List to store labels for the data being plotted

def on_message(client, userdata, msg):
    global timestamps, y_data, data_labels
    
    # Parse the received message using the new parser
    data = parse_message(msg.payload)
    if not data:
        print("Error: Could not parse message")
        return
    
    print(f"Received data: {data}")  # Debug: Print received data
    
    # Extract timestamp and convert to human-readable format
    timestamp = data.get("timestamp")
    if not timestamp:
        print("Error: Missing 'timestamp' in received data")
        return
    
    try:
        # Convert timestamp to float if it's a string
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        human_readable_time = datetime.fromtimestamp(timestamp/1000 if timestamp > 1e12 else timestamp).strftime("%H:%M:%S")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return
    
    # Append new timestamp
    timestamps.append(human_readable_time)
    
    # Extract data values based on the structure of the payload
    if "value" in data:  # Single value format
        y_data.append([data["value"]])
        if not data_labels:
            data_labels.append("value")
    else:  # Multiple values format
        values = []
        for key, value in data.items():
            if key not in ["type", "timestamp"]:  # Skip metadata fields
                if isinstance(value, (int, float)):  # Only plot numeric values
                    values.append(value)
                    if key not in data_labels:
                        data_labels.append(key)
        if values:  # Only append if we have numeric values
            y_data.append(values)
    
    # Keep only the last 20 data points for visualization
    timestamps = timestamps[-20:]
    y_data = y_data[-20:]
    
    # Clear and update plot
    ax.clear()
    
    # Plot all data values
    for i, label in enumerate(data_labels):
        try:
            values = [values[i] for values in y_data if len(values) > i]
            if values:  # Only plot if we have values for this label
                ax.plot(timestamps[-len(values):], values, marker='o', linestyle='-', label=label)
        except Exception as e:
            print(f"Error plotting {label}: {e}")
    
    # Set common plot properties
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title(f"Data received from host {selected_host} for topic: {selected_topic}")
    ax.legend()  # Show legend for multiple lines
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    plt.pause(0.5)  # Refresh every 0.5 seconds

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(selected_topic)
    else:
        print("Failed to connect, return code:", rc)

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER, PORT, 60)
        print(f"Starting MQTT subscriber for topic: {selected_topic}")
        client.loop_forever()  # Keep listening for messages
    except Exception as e:
        print(f"Error: {e}")