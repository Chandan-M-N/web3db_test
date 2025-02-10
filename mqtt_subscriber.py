import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
from datetime import datetime

# MQTT Broker Settings
BROKER = "75.131.29.55"
PORT = 1883
TOPIC = "sensor/data"

# Initialize Matplotlib figure
plt.ion()
fig, ax = plt.subplots()
timestamps, y_data = [], []

def on_message(client, userdata, msg):
    global timestamps, y_data
    
    # Decode the received message
    data = json.loads(msg.payload.decode("utf-8"))
    
    if data.get("type") == "heart_rate":
        sensor_value = data["value"]
        timestamp = data["timestamp"]
        
        # Convert timestamp to human-readable format
        human_readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
        
        # Append new data
        timestamps.append(human_readable_time)
        y_data.append(sensor_value)
        
        # Keep only the last 20 data points for visualization
        timestamps = timestamps[-20:]
        y_data = y_data[-20:]
        
        # Clear and update plot
        ax.clear()
        ax.plot(timestamps, y_data, marker='o', linestyle='-')
        ax.set_xlabel("Time")
        ax.set_ylabel("Heart Rate (BPM)")
        ax.set_title("Received Sensor Data Stream")
        plt.xticks(rotation=45)
        plt.pause(0.5)
        
        print(f"Received: {data}")

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
    
    client.loop_forever()  # Keep listening for messages
