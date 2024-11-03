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
        self.known_width = 20  # Width of the target in real-world units (e.g., inches)
        self.focal_length = 800  # Focal length in pixels (adjust value)
        self.launches_remaining = len(self.targets)  # Launch counter for all targets
        self.target = "1" #3 for red, 2 for Green, 1 for Blue.  Aka 2nd color from STC
        self.conf_threshold = 0.6
        # Initialize serial communication
        self.arduino_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Update port as needed
        time.sleep(2)  # Wait for the serial connection to initialize

    def __str__(self):
        return self.__class__.__name__

    def mission_heartbeat(self):
        heartbeat = ["$RXDOK", self.launches_remaining]
        return heartbeat

    def run(self, camera_data: Dict[str, CameraData], position_data: PositionData, occupancy_grid=None) -> Tuple[Dict, Dict, Dict]:
        center_camera_data = camera_data.get("center")
        center_camera_results = center_camera_data.results
        
        if center_camera_results is None:
            return {}, {}
        
        # The target we are looking for is the second color of the Scan The Code pattern
        colors_detected = []
        found = False
        for result in center_camera_results:
            for box in result.boxes:
                if(box.cls.item() == self.target and conf > self.conf_threshold):
                    conf = box.conf.item()
                    cls_id = box.cls.item()
                    x1, y1, x2, y2 = box.xyxy.cpu().numpy().flatten()
                    found = True
                    
        if found:  
                
            # We have found our target
            
            # Now we need to align with it
            #Strafe left, right
            # Or moving forward / backward depending on distance
            pass
            if label in self.detected_targets and not self.detected_targets[label]:
                if 2.5 < distance <= 3: # launchers activate within range
                    self.log(f"Target {label} is within shooting range. Activating launcher.")
                    self.send_command_to_arduino(self.targets.index(label) + 1)  # Send command to Arduino
                    self.detected_targets[label] = True  # Mark the target as launched
                    self.launches_remaining -= 1  # Decrement the remaining launches
                    time.sleep(1)  # Short delay to prevent rapid command sending
                break
            
        else:
            return {}, {}
                

            

        if self.launches_remaining <= 0:
            self.log("All targets launched. Ending mission.")
            gnc_cmd['end_mission'] = True  # End the mission when all targets are launched

        perc_cmd = {}
        gnc_cmd = {"poshold": True}
        return perc_cmd, gnc_cmd

    def end(self):
        self.log("Mission ended. Performing cleanup.")
        self.arduino_serial.close()  # Close the serial connection
        
        
        
        
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
