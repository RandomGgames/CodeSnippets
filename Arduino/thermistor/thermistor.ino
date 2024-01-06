const double set_temperature = 50.0;  // ℃
const int relayPin = 2;               // D2

void setup() {
    Serial.begin(9600);
    pinMode(relayPin, OUTPUT);
}

double Thermister(int thermistor_analog_data) {
    double temp;
    temp = log(10000.0 * ((1024.0 / thermistor_analog_data - 1)));
    temp = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * temp * temp)) * temp);
    temp = temp - 273.15;
    temp = 1.07 * temp - 1.787;
    Serial.print(temp);
    Serial.println(" ℃");
    return temp;
}

void enableRelay() {
    digitalWrite(relayPin, HIGH);  // Turn on the relay
    Serial.println("Relay Enabled");
}

void disableRelay() {
    digitalWrite(relayPin, LOW);  // Turn off the relay
    Serial.println("Relay Disabled");
}

int thermistor_analog_data;
void loop() {
    thermistor_analog_data = analogRead(A0);
    double temp = Thermister(thermistor_analog_data);
    // Compare the measured temperature with the set temperature
    if (temp < set_temperature) {
        // If the measured temperature is below the set temperature, enable the relay
        enableRelay();
    } else {
        // If the measured temperature is equal to or above the set temperature, disable the relay
        disableRelay();
    }
    delay(300);
}