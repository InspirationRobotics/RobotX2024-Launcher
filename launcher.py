import serial
import time

# Establish serial communication with Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Confirm correct port
time.sleep(2)  # Wait for Arduino to initialize

# Track which launcher to fire next
launcher_index = 0  # Start with launcher 0
max_launchers = 4  # Total number of launchers

def send_command(launcher_num):
    """Sends the launcher number to the Arduino to activate the launcher."""
    command = f"{launcher_num}\n"  # Format command with newline
    arduino.write(command.encode())  # Send the command
    print(f"Sent command to activate launcher {launcher_num}")

def handle_new_target():
    """Activates the next launcher for each new detected target."""
    global launcher_index  # Use the global variable to track launchers
    if launcher_index < max_launchers:
        send_command(launcher_index)  # Activate the corresponding launcher
        launcher_index += 1  # Move to the next launcher
    else:
        print("All launchers have been activated. Waiting for reset...")

# Example: Main loop to simulate target detection
while True:
    # Replace with your actual target detection logic





    
    detected_distance = 2.9  # Simulate a target detected within 3 meters

    if detected_distance <= 3.0:
        handle_new_target()  # Activate the next launcher
        time.sleep(5)  # Wait to avoid rapid firing of the same launcher

    # Optional: Add a stopping condition if needed
    if launcher_index >= max_launchers:
        print("All targets have been handled.")
        break  # Stop the program if all launchers are fired

    time.sleep(0.5)  # Poll every 500ms
