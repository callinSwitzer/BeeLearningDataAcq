

#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

// put DC motor at m1
Adafruit_DCMotor *myDCMotor = AFMS.getMotor(1);

// stepper motor
Adafruit_StepperMotor *myMotor = AFMS.getStepper(2000, 2);




int ledPin = 13; 
int val = 0;
long interval = 80; 
long previousTime = 0; 
int ctr = 0; 
unsigned long currentTime;
unsigned long motTime = millis();

void setup(){ 
  Serial.begin(115200); 

  AFMS.begin();  // create with the default frequency 1.6KHz

      // setup stepper
    myMotor->setSpeed(1000);  // 60 rpm  
   
   // setup DC motor     
   myDCMotor->setSpeed(170);
  
  Serial.write("Setup complete"); 
}
void loop(){ 

 currentTime = millis(); 

  if(currentTime - previousTime > interval){
  
      // turn off DC motor
       myDCMotor->run(RELEASE);
  }

  val = Serial.read();      // read the serial port
   
      
  // if 'v' is pressed, only the vibration motor turns on
 if (val == 118){
    // make sure the DC motor doesn't get activated 
    // too often, otherwise it freezes the arduino
    if(millis() - motTime > 300){
      Serial.println(millis() - motTime); 
      motTime = millis(); 
      Serial.println("VIBE_ONLY"); 
      myDCMotor->run(FORWARD); 
      previousTime = currentTime;
    }
  
  }

  // if 's' is pressed, then only the stepper motor goes
  else if (val == 115) {
    Serial.println(val);
    myMotor->step(40, FORWARD, SINGLE);    
    // release motor so it doesn't get too hot!
    myMotor->release();  
    }
 
}
