const int relays[] = {10, 11, 12, 9};  // Relay pins for the launchers

void setup() {
    Serial.begin(9600);  // Initialize serial communication at 9600 baud rate
    for (int pin : relays) {
        pinMode(pin, OUTPUT);       // Set relay pins as OUTPUT
        digitalWrite(pin, HIGH);    // Ensure all relays are off initially
    }
    Serial.println("Arduino is ready to receive commands.");
}

void loop() {
    if (Serial.available() > 0) {
        int command = Serial.read() - '0';  // Read command from Jetson (convert char to int)
        
        if (command >= 1 && command <= 4) {  // Check if command is valid (1, 2, 3, or 4)
            activateRelay(command);  // Activate the corresponding relay
        }
    }
}

// Function to activate the relay for the corresponding launcher
void activateRelay(int launcher) {
    int relayIndex = launcher - 1;  // Map command (1-4) to relay index (0-3)
    
    digitalWrite(relays[relayIndex], LOW);   // Turn on the relay (launcher)
    Serial.print("Activating launcher: ");
    Serial.println(launcher);
    
    delay(2000);  // Keep the launcher active for 2 seconds
    
    digitalWrite(relays[relayIndex], HIGH);  // Turn off the relay
    Serial.print("Deactivating launcher: ");
    Serial.println(launcher);
}
