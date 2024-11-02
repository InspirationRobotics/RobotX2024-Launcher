from typing import Dict, Tuple
import torch
import serial
from comms_core import Logger
from ..mission_node import PositionData
from perception_core import CameraData
import cv2
import time

class TargetLaunchMission(Logger):
    init_perc_cmd = {
        "start": ["center"],
    }

    def __init__(self):
        super().__init__(str(self))
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True) # Load YOLO model
        self.known_width = 20  # Width of the target in real-world units (e.g., inches)
        self.focal_length = 800  # Focal length in pixels (adjust value)
        self.targets = ["red", "green", "blue"]  # List of targets to detect
        self.detected_targets = {target: False for target in self.targets}  # Track detection status
        self.launches_remaining = len(self.targets)  # Launch counter for all targets
        
        # Initialize serial communication
        self.arduino_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Update port as needed
        time.sleep(2)  # Wait for the serial connection to initialize

    def __str__(self):
        return self.__class__.__name__

    def mission_heartbeat(self):
        heartbeat = ["$TXTARGET", "TargetLaunchMission Active"]
        return heartbeat

    def calculate_distance(self, pixel_width: float) -> float:
        if pixel_width > 0:
            return (self.known_width * self.focal_length) / pixel_width # Caclulate distance based on parameters
        else:
            return float('inf') # Target not reached

    def send_command_to_arduino(self, command: int):
        """
        Send a command to the Arduino to activate a specific launcher.
        Command should be between 1 and 4, where 1-3 correspond to the targets and 4 could be a general command.
        """
        if 1 <= command <= 4:
            self.arduino_serial.write(str(command).encode())  # Send the command as bytes
            self.log(f"Sent command {command} to Arduino.")

    def run(self, camera_data: Dict[str, CameraData], position_data: PositionData, occupancy_grid=None) -> Tuple[Dict, Dict, Dict]:
        frame = camera_data["center"].frame  # Use the center camera for detection
        results = self.model(frame)  # Run YOLO inference on the frame
        detections = results.pandas().xyxy[0]  # Convert results to pandas DataFrame
        perc_cmd = {}
        gnc_cmd = {}

        for index, row in detections.iterrows():
            label = row['name']  # Detected class label (e.g., "red", "green", "blue")
            confidence = row['confidence']
            x_min, y_min, x_max, y_max = row['xmin'], row['ymin'], row['xmax'], row['ymax']
            pixel_width = x_max - x_min
            distance = self.calculate_distance(pixel_width)

            self.log(f"Detected {label} with confidence {confidence:.2f} at [{x_min}, {y_min}, {x_max}, {y_max}]")
            self.log(f"Estimated distance to {label} target: {distance:.2f} units")

            if label in self.detected_targets and not self.detected_targets[label]:
                if 2.5 < distance <= 3: # launchers activate within range
                    self.log(f"Target {label} is within shooting range. Activating launcher.")
                    self.send_command_to_arduino(self.targets.index(label) + 1)  # Send command to Arduino
                    self.detected_targets[label] = True  # Mark the target as launched
                    self.launches_remaining -= 1  # Decrement the remaining launches
                    time.sleep(1)  # Short delay to prevent rapid command sending
                break

        if self.launches_remaining <= 0:
            self.log("All targets launched. Ending mission.")
            gnc_cmd['end_mission'] = True  # End the mission when all targets are launched

        return perc_cmd, gnc_cmd

    def end(self):
        self.log("Mission ended. Performing cleanup.")
        self.arduino_serial.close()  # Close the serial connection
