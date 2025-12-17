#include <Wire.h>
#include "MPU6050.h"

MPU6050 mpu;

// Motor driver pins
#define RPWM_L  25
#define LPWM_L  26
#define RPWM_R  27
#define LPWM_R  14

int motorSpeed = 120; // reduced from 200 → smoother control

void setup() {
  Serial.begin(9600);
  Wire.begin();
  mpu.initialize();

  pinMode(RPWM_L, OUTPUT);
  pinMode(LPWM_L, OUTPUT);
  pinMode(RPWM_R, OUTPUT);
  pinMode(LPWM_R, OUTPUT);

  stopMotors();
  Serial.println("🤖 ESP32 Line Follower (Low-Speed Mode) Ready!");
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    processCommand(cmd);
  }
}

void processCommand(char cmd) {
  switch (cmd) {
    case 'F': forward(); break;
    case 'B': backward(); break;
    case 'L': left(); break;
    case 'R': right(); break;
    case 'S': stopMotors(); break;
  }
}

void forward() {
  analogWrite(RPWM_L, motorSpeed);
  analogWrite(LPWM_L, 0);
  analogWrite(RPWM_R, motorSpeed);
  analogWrite(LPWM_R, 0);
}

void backward() {
  analogWrite(RPWM_L, 0);
  analogWrite(LPWM_L, motorSpeed);
  analogWrite(RPWM_R, 0);
  analogWrite(LPWM_R, motorSpeed);
}

void left() {
  analogWrite(RPWM_L, 0);
  analogWrite(LPWM_L, motorSpeed - 20);
  analogWrite(RPWM_R, motorSpeed);
  analogWrite(LPWM_R, 0);
}

void right() {
  analogWrite(RPWM_L, motorSpeed);
  analogWrite(LPWM_L, 0);
  analogWrite(RPWM_R, 0);
  analogWrite(LPWM_R, motorSpeed - 20);
}

void stopMotors() {
  analogWrite(RPWM_L, 0);
  analogWrite(LPWM_L, 0);
  analogWrite(RPWM_R, 0);
  analogWrite(LPWM_R, 0);
}