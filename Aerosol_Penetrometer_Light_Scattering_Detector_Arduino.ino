///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Author: Sebastian Lifka
// Title: Aerosol_Penetrometer_Light_Scattering_Detector_Arduino
// Created: 14. Sep 2020
// Modified: 11. Dec 2020
// Description: 
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <Wire.h>

const int ledPinBefore = 9;         // PWM pin LED before mask
const int ledPinAfter = 10;         // PWM pin LED after mask
const int analogPinBefore90 = A0;   // Analog read pin before mask 90°
const int analogPinBefore180 = A1;  // Analog read pin before mask 180°
const int analogPinAfter90 = A2;    // Analog read pin after mask 90°
const int analogPinAfter180 = A3;   // Analog read pin after mask 180°
const int baudRate = 9600;
int ledBrightness = 254;            // Initial LED brightness


void setup() {
  pinMode(ledPinBefore, OUTPUT);
  pinMode(ledPinAfter, OUTPUT);
  Serial.begin(baudRate);
}

void loop() {
  String incomingString = readInput();
  delay(150);
  if (incomingString.substring(0,3) == "LED") {  
    ledOnOff(incomingString);
    delay(150);
  }
  else if (incomingString.substring(0,10) == "BRIGHTNESS") {
    setLedBrightness(incomingString);
    delay(150);
  }
  else if (incomingString == "READ_DIODE") {
    readDiode(incomingString);
    delay(150);
  }
  else {
    incomingString = "";
    delay(150);
  }
}

String readInput() {
  int numByte;
  char incomingByte;
  String incomingString = "";
  
  numByte = Serial.available();
  for (int i = 0; i < numByte; i++) {
    incomingByte = Serial.read();
    
    if (incomingByte != '\n') {
      incomingString += incomingByte;
    }
  }
  return incomingString;
}

void ledOnOff(String incomingString) {
  if (incomingString == "LED_Before_1") { 
    analogWrite(ledPinBefore, ledBrightness);
    Serial.println("LED On");
    incomingString = "";
  }
  else if (incomingString == "LED_Before_0") {
    digitalWrite(ledPinBefore, LOW);
    Serial.println("LED Off");
    incomingString = "";
  }
  else if (incomingString == "LED_After_1") { 
    analogWrite(ledPinAfter, ledBrightness);
    Serial.println("LED On");
    incomingString = "";
  }
  else if (incomingString == "LED_After_0") {
    digitalWrite(ledPinAfter, LOW);
    Serial.println("LED Off");
    incomingString = "";
  }
}

void setLedBrightness(String incomingString) {
  String tmpString = incomingString.substring(10);
  ledBrightness = tmpString.toInt();
  analogWrite(ledPinBefore, ledBrightness);
  analogWrite(ledPinAfter, ledBrightness);
  Serial.println(ledBrightness);
  incomingString = "";
}

void readDiode(String incomingString) {
  int diodeValueBefore90 = analogRead(analogPinBefore90);
  int diodeValueBefore180 = analogRead(analogPinBefore180);
  int diodeValueAfter90 = analogRead(analogPinAfter90);
  int diodeValueAfter180 = analogRead(analogPinAfter180);
  float diodeVoltageBefore90 = diodeValueBefore90 * (5.0 / 1023.0);
  float diodeVoltageBefore180 = diodeValueBefore180 * (5.0 / 1023.0);
  float diodeVoltageAfter90 = diodeValueAfter90 * (5.0 / 1023.0);
  float diodeVoltageAfter180 = diodeValueAfter180 * (5.0 / 1023.0);
  Serial.print(diodeVoltageBefore90,3);
  Serial.print(';');
  Serial.print(diodeVoltageBefore180,3);
  Serial.print(';');
  Serial.print(diodeVoltageAfter90,3);
  Serial.print(';');
  Serial.print(diodeVoltageAfter180,3);
  Serial.println();
  
  incomingString = "";
}
