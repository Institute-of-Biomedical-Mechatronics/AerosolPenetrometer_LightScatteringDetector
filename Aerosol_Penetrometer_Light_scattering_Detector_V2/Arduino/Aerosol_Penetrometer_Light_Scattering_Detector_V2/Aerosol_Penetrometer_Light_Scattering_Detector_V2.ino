///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Author: Sebastian Lifka
// Title: ﻿Aerosol_Penetrometer_Light_Scattering_Detector_V2
// Created: 22. Jan 2021
// Modified: 22. Jan 2021
// Description: 
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <Wire.h>
#include <Adafruit_BMP280.h>

#define BMP_SCK  (13)
#define BMP_MISO (12)
#define BMP_MOSI (11)
#define BMP_CS   (10)

Adafruit_BMP280 bmp(BMP_CS); // hardware SPI

int analogPinBefore90 = A0;   // Analog read pin before mask 90°
int analogPinBefore180 = A1;  // Analog read pin before mask 180°
int analogPinAfter90 = A2;    // Analog read pin after mask 90°
int analogPinAfter180 = A3;   // Analog read pin after mask 180°
int baudRate = 9600;

int transistorValueBefore90;
int transistorValueBefore180;
int transistorValueAfter90;
int transistorValueAfter180;
float transistorVoltageBefore90;
float transistorVoltageBefore180;
float transistorVoltageAfter90;
float transistorVoltageAfter180;

float pressureAfter;

String incoming;

void setup() {
  Serial.begin(baudRate);
  bmp.begin();

    /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_1); /* Standby time. */
}

void loop() {
  incoming = readInput();

  if (incoming == "1") {
    transistorValueBefore90 = analogRead(analogPinBefore90);
    transistorValueBefore180 = analogRead(analogPinBefore180);
    transistorValueAfter90 = analogRead(analogPinAfter90);
    transistorValueAfter180 = analogRead(analogPinAfter180);
    
    transistorVoltageBefore90 = transistorValueBefore90 * (5.0 / 1023.0);
    transistorVoltageBefore180 = transistorValueBefore180 * (5.0 / 1023.0);
    transistorVoltageAfter90 = transistorValueAfter90 * (5.0 / 1023.0);
    transistorVoltageAfter180 = transistorValueAfter180 * (5.0 / 1023.0);
  
    pressureAfter = bmp.readPressure();
    pressureAfter = pressureAfter*1e-2;
    
    Serial.print(transistorVoltageBefore90,3);
    Serial.print(';');
    Serial.print(transistorVoltageBefore180,3);
    Serial.print(';');
    Serial.print(transistorVoltageAfter90,3);
    Serial.print(';');
    Serial.print(transistorVoltageAfter180,3);
    Serial.print(';');
    Serial.print(pressureAfter,1);
    Serial.println();

    incoming = "0";
  } else if (incoming == "2") {
    if (!bmp.begin()) {
      Serial.println("No pressure sensor connected!");
    }
    incoming = "0";
  }
  
  delay(50);
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
