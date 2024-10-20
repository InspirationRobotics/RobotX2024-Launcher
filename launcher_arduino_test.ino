int relayPins[4] = {2, 3, 4, 5};  // Pins connected to relay module

void setup() {
  Serial.begin(9600);  // Start the serial communication at 9600 baud rate
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);  // Ensure relays are off initially
  }
}

void loop() {
  if (Serial.available() > 0) {  // Check if data is available from Jetson Orin
    int launcher = Serial.parseInt();  // Read the launcher number (0-3)
    if (launcher >= 0 && launcher < 4) {
      activateLauncher(launcher);
    }
  }
}

void activateLauncher(int launcher) {
  digitalWrite(relayPins[launcher], HIGH);  // Turn on the relay to fire launcher
  delay(2000);  // Adjust the delay as needed for solenoid activation
  digitalWrite(relayPins[launcher], LOW);  // Turn off the relay
}
