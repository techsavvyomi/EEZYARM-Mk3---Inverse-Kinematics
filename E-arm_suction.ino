#include <math.h>
#include <Servo.h>

Servo elbow;  // create servo object to control a servo
Servo shoulder;
Servo base;
int buttonValue;
int xValue;
int yValue;
int zValue;
int pumpStatus;
int suctionStatus;
int delay_1 = 10;     //delay between loop
int counter = 1;

float el = 215;        //elbow length 
float sl = 133;        //shoulder length
float y_initial = 100;
float z_initial = -120;
float x, y, z;
float alpha, beta, phi, theta, cos_theta, cos_phi;
int shoulder_angle, elbow_angle;


float y_dist = 50;   // range is 0 - 200 mm
float z_dist = 250;   // range is 0 - 350 mm


void setup() {
  Serial.begin(9600);
  shoulder.attach(5);  // attaches the servo on pin 9 to the servo object
  elbow.attach(6); 
  base.attach(9); 
  pinMode(2, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  delay(50);
  
}

void loop() {


     if (Serial.available()) {
    String dataString = Serial.readStringUntil('\n');
    dataString.trim();

    // Split the data string by commas
    int commaIndex = dataString.indexOf(',');
  

    commaIndex = dataString.indexOf(',');
    if (commaIndex != -1) {
      xValue = dataString.substring(0, commaIndex).toInt();
      dataString = dataString.substring(commaIndex + 1);
    }

    commaIndex = dataString.indexOf(',');
    if (commaIndex != -1) {
      yValue = dataString.substring(0, commaIndex).toInt();
      dataString = dataString.substring(commaIndex + 1);
    }

    commaIndex = dataString.indexOf(',');
    if (commaIndex != -1) {
      zValue = dataString.substring(0, commaIndex).toInt();
      dataString = dataString.substring(commaIndex + 1);
    }

    commaIndex = dataString.indexOf(',');
    if (commaIndex != -1) {
      pumpStatus = dataString.substring(0, commaIndex).toInt();
      dataString = dataString.substring(commaIndex + 1);
    }

    suctionStatus = dataString.toInt();

    // Process the received data
    // ...

    // Print the received values for testing
    Serial.print("Button Value: ");
    Serial.println(buttonValue);
    Serial.print("X Value: ");
    Serial.println(xValue);
    Serial.print("Y Value: ");
    Serial.println(yValue);
    Serial.print("Z Value: ");
    Serial.println(zValue);
    Serial.print("Pump Status: ");
    Serial.println(pumpStatus);
    Serial.print("Suction Status: ");
    Serial.println(suctionStatus);
  
    base.write(xValue);
    if (suctionStatus == 1) {
      digitalWrite(12, HIGH);
    } else {
      digitalWrite(12, LOW);
    }
    if (pumpStatus == 1) {
      digitalWrite(11, HIGH);
    } else {
      digitalWrite(11, LOW);
    }
    y_dist=yValue;
    z_dist=zValue;
    y = y_initial + y_dist;
    z = z_initial + z_dist;
  
    x = sqrt(z*z + y*y);
    
    Serial.print(x);
    Serial.print("   ");
    Serial.print(y);
    Serial.print("   ");
    Serial.print(z);
    Serial.print("   ");
    
    alpha = asin(z/x)*(180/PI);     // in degrees
    beta  = acos(z/x)*(180/PI);     // in degrees

    Serial.print(alpha);
    Serial.print("   ");
    Serial.print(beta);
    Serial.print("   ");

    cos_phi   = (sl*sl + x*x - el*el)/(2*sl*x);
    cos_theta = (el*el + x*x - sl*sl)/(2*el*x);

    Serial.print(cos_phi);  
    Serial.print("   ");
    Serial.print(cos_theta);
    Serial.print("   ");
    
    phi   = ((acos(cos_phi))*180)/PI;
    theta = ((acos(cos_theta))*180)/PI;

    Serial.print(phi);
    Serial.print("   ");
    Serial.print(theta);
    Serial.print("   ");

    shoulder_angle = 180-(phi+alpha);
    elbow_angle    = 180-(theta+beta);
    
    Serial.print(shoulder_angle);
    Serial.print("   ");
    Serial.print(elbow_angle);
    Serial.println("   ");

    shoulder.write(shoulder_angle);
    elbow.write(elbow_angle);
    delay(delay_1);
 
    // Perform other actions based on the received data
    // ...
  }
}
  