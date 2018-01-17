
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

// I set the number of steps to 2000, even though it's 200
// this seems to make it go faster
// the motor is connected to port 1 (M1 & M2)
Adafruit_StepperMotor *myMotor = AFMS.getStepper(2000, 1);




int ledPin = 13; int val = 0;
void setup(){ 
  //pinMode(ledPin,OUTPUT); 
  Serial.begin(9600); 

  //Serial.println("Stepper test!");

  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz
  
  myMotor->setSpeed(1000);  // 60 rpm   
  Serial.write("Setup complete"); 
}
void loop(){ 
    val = Serial.read();      // read the serial port
    if (val > '0') {
      Serial.println(val);
      myMotor->step(40, FORWARD, SINGLE);  
      // release motor so it doesn't get too hot!
      myMotor->release();    
      }
 
}
