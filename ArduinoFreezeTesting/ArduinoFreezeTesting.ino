
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
Adafruit_StepperMotor *myMotor = AFMS.getStepper(2000, 2);

// put stepper motor at m3
Adafruit_DCMotor *myDCMotor = AFMS.getMotor(1);




int ledPin = 13; int val = 0;
long interval = 50; 
long previousTime = 0; 

void setup(){ 
  //pinMode(ledPin,OUTPUT); 
  Serial.begin(9600); 

  //Serial.println("Stepper test!");

  AFMS.begin();  // create with the default frequency 1.6KHz
  //AFMS.begin(1000);  // OR with a different frequency, say 1KHz
  
  myMotor->setSpeed(1000);  // 60 rpm  


   // setup DC motor     
   myDCMotor->setSpeed(100);
  
  Serial.write("Setup complete"); 
}
void loop(){ 

  unsigned long currentTime = millis(); 

  if(currentTime - previousTime > interval){
      // turn on DC motor
       myDCMotor->run(RELEASE);
  }
      
      val = Serial.read();      // read the serial port
      
      // if 's' is pressed, then only the stepper motor goes
     if (val == 115) {
        Serial.println(val);
        myMotor->step(40, FORWARD, SINGLE);    
        // release motor so it doesn't get too hot!
        myMotor->release();  
        }
  
  
      
      // if 'v' is pressed, only the vibration motor turns on
      else if (val == 118){
        previousTime = currentTime;
          Serial.println(val);
           myDCMotor->run(FORWARD);
           
      }
      
      // if any other key is pressed, both vibration and stepper go
      else if (val > '0') {
         previousTime = currentTime;
        Serial.println(val);
        myMotor->step(40, FORWARD, SINGLE);  
        myDCMotor->run(FORWARD);
        
        // release motor so it doesn't get too hot!
        myMotor->release();  
    
        }

 
}
