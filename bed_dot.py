import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from datetime import datetime
import time
import argparse
import sys
import random

def parse_arguments():
    parser = argparse.ArgumentParser(description="MQTT Data Pipeline with Plotting")
    parser.add_argument('--h', '--host', type=str, default="75.131.29.55",
                        help="Target MQTT broker host (default: 75.131.29.55)")
    parser.add_argument('--topic', type=str, default="/unknown_org/74:4d:bd:89:2d:f4/vital",
                        help="MQTT topic for both source and target (default: /unknown_org/74:4d:bd:89:2d:f4/vital)")
    return parser.parse_args()

def parse_data(payload):
    """Parse the semicolon-separated data string into a dictionary"""
    data = {}
    first_timestamp = None
    try:
        pairs = payload.strip().split(';')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.strip().split('=')
                # Keep only the first timestamp encountered
                if 'timestamp' in key.lower():
                    if first_timestamp is None:
                        first_timestamp = float(value)
                    continue  # Skip adding this timestamp to data
                try:
                    data[key] = float(value)
                except ValueError:
                    data[key] = value
        
        # Add the first timestamp back to the data
        if first_timestamp is not None:
            data['timestamp'] = first_timestamp
            
        return data
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None

class MQTTDataPipeline:
    def __init__(self, target_host, topic):
        # Source broker settings (fixed)
        self.source_broker = "sensorweb.us"
        self.source_port = 1883
        
        # Target broker settings (from args)
        self.target_broker = target_host
        self.target_port = 1883
        
        # Common topic for both source and target
        self.topic = topic

        # Initialize plotting
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.timestamps = []
        self.data_dict = {}
        self.color_dict = {}

        # MQTT clients
        self.source_client = mqtt.Client()
        self.target_client = mqtt.Client()
        self.source_client.on_connect = self.on_source_connect
        self.source_client.on_message = self.on_message

    def get_random_color(self):
        """Generate a random color"""
        return (random.random(), random.random(), random.random())

    def on_source_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to source broker: {self.source_broker}")
            self.source_client.subscribe(self.topic)
            print(f"Subscribed to topic: {self.topic}")
        else:
            print(f"Failed to connect to source broker, return code: {rc}")

    def on_message(self, client, userdata, message):
        try:
            # Decode the raw payload
            payload = message.payload.decode("utf-8")
            
            # Check if the payload contains 'heartrate'
            if 'heartrate=' in payload:
                # Publish the raw payload to the target broker
                time.sleep(2)
                self.target_client.publish(self.topic, payload)
                
                # Parse the payload
                data = parse_data(payload)
                
                # Update the plot
                if data:
                    self.update_plot(data)
            
        except Exception as e:
            print(f"Error processing message: {e}")

    def update_plot(self, data):
        # Convert nanosecond timestamp to readable format
        timestamp = datetime.fromtimestamp(data['timestamp'] / 1e9).strftime("%H:%M:%S")
        
        # Initialize data structures for new variables
        for key, value in data.items():
            # Only exclude 'timestamp' and ensure the value is numeric
            if key != 'timestamp' and isinstance(value, (int, float)):
                # Initialize data list if key is new
                if key not in self.data_dict:
                    self.data_dict[key] = []
                    self.color_dict[key] = self.get_random_color()
                self.data_dict[key].append(value)

        # Update timestamps
        self.timestamps.append(timestamp)

        # Keep only last 20 data points
        max_points = 20
        if len(self.timestamps) > max_points:
            self.timestamps.pop(0)
            for key in self.data_dict:
                if len(self.data_dict[key]) > max_points:
                    self.data_dict[key].pop(0)

        # Clear and redraw plot
        self.ax.clear()

        # Plot each variable with its assigned color
        for key, values in self.data_dict.items():
            self.ax.plot(self.timestamps, values, marker='o', linestyle='-', 
                        label=key, color=self.color_dict[key])

        # Set plot properties
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Values")
        self.ax.set_title(f"Real-time Vital Signs\nSource: {self.source_broker} → Target: {self.target_broker}")
        
        # Only show legend if there are labels to display
        if self.data_dict:
            self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.pause(0.1)

    def start(self):
        try:
            # Connect to both brokers
            print(f"Connecting to source broker: {self.source_broker}")
            self.source_client.connect(self.source_broker, self.source_port)
            
            print(f"Connecting to target broker: {self.target_broker}")
            self.target_client.connect(self.target_broker, self.target_port)

            # Start the source client loop
            self.source_client.loop_forever()

        except Exception as e:
            print(f"Error in pipeline: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Create and start the pipeline
    pipeline = MQTTDataPipeline(args.h, args.topic)
    pipeline.start()