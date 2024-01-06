#include <AccelStepper.h>

#define DIR_PIN 2 // Connected to DIR pin on the stepper driver
#define PUL_PIN 3 // Connected to PUL pin on the stepper driver

const float STEPS_PER_DEGREE = 200*32/360;

AccelStepper stepper(1, PUL_PIN, DIR_PIN); // (1, PUL_PIN, DIR_PIN) sets the driver interface

unsigned long previousMillis = 0;
const unsigned long interval = 1000; // Interval in milliseconds (1 second)

void setup() {
  // You can remove stepper.setMaxSpeed and stepper.setAcceleration from here
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    rotateDegrees(6, 10000, 10000);
    previousMillis = currentMillis;
  }
}

void rotateDegrees(float degrees, float acceleration, float speed) {
  int steps = degrees * STEPS_PER_DEGREE;

  stepper.setAcceleration(acceleration);
  stepper.setMaxSpeed(speed);
  stepper.move(steps);

  while (stepper.distanceToGo() != 0) {
    stepper.run();
  }
}
