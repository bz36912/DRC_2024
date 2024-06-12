/*
 * Acknowledgement:
 * some of the MPU6050-raw-data-extraction code in gryoSensor.cpp and most in calculateError() are written by Dejan from:
 * https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/
*/
#include <Arduino.h>
#include <Wire.h>
#include "gyroSensor.h"

void (*resetFunc)(void) = 0;

Vector3D::Vector3D() {
  this->x = 0;
  this->y = 0;
  this->z = 0;
}

String Vector3D::toString() {
  return "(" + String(this->x, 3) + ", " + String(this->y, 3) + ", " + String(this->z, 3) + ")";
}

Gyro::Gyro() {
  // initialise I2C (using the Wire library) with MPU6050
  Serial.println("inside Gyro::Gyro()");
  Wire.begin();                      // Initialize comunication
  Wire.beginTransmission(MPU);       // Start communication with MPU6050 // MPU=0x68
  Wire.write(0x6B);                  // Talk to the register 6B
  Wire.write(0x00);                  // Make reset - place a 0 into the 6B register
  uint8_t err = Wire.endTransmission(true);        // end the transmission
  if (err) {
    print_var_full("Gyro failed to start properly. Press the RESET button. ERROR", 1, "Gyro::Gyro()");
  } else {
    this->gyroAngle.AXIS = 0; // initialise value
    this->curTime = micros();
    // Call this function if you need to get the IMU error values for your module
    calculateError();
    //reset gyroAngle
    this->gyroAngle = Vector3D();
  }
}

void Gyro::calculateError() {
  //When this function is called, ensure the car is stationary. See Step 2 for more info

  // Read gyroscope values 200 times
  const int NUM_SAMPLES = 200;
  Vector3D angularVelErrorTemp = Vector3D();
  for (int i = 0; i < NUM_SAMPLES; i++) {
    this->readAngularVel();
    angularVelErrorTemp.x += angularVel.x;
    angularVelErrorTemp.y += angularVel.y;
    angularVelErrorTemp.z += angularVel.z;
  }
  
  this->angularVelError.x = angularVelErrorTemp.x / NUM_SAMPLES;
  this->angularVelError.y = angularVelErrorTemp.y / NUM_SAMPLES;
  this->angularVelError.z = angularVelErrorTemp.z / NUM_SAMPLES;
}

/**
 * @brief reads the angular velocity reading from the gyroscope
 * Store the values into the class variable, angularVel
 * 
 * @return int 0 for success, negative values for failure/error
 * -1 (FAILURE) means the function ignore the new reading to clear the error
 * -2 (CRITICAL_FAILURE) means function canNOT fix the error, so the car needs to reset.
 */
int Gyro::readAngularVel() {
  Wire.beginTransmission(MPU);
  Wire.write(0x43);
  uint8_t error = Wire.endTransmission(false);
  if (error) {
    print_var_full("endTransmission error code", error, "Gyro::readAngularVel");
    if (error == 4) {
      return CRITICAL_FAILURE;
    }
    return FAILURE;
  }
  uint8_t len = Wire.requestFrom(MPU, 6, true);
  if (len != 6) {
    print_var_full("requestFrom only received", len, "Gyro::readAngularVel");
    return FAILURE;
  }

  Vector3D temp = Vector3D();
  temp.x = (Wire.read() << 8 | Wire.read()) / 129.18 - this->angularVelError.x; //angularVelError is calculated in the calculateError() function
  temp.y = (Wire.read() << 8 | Wire.read()) / 129.18 - this->angularVelError.y;
  temp.z = (Wire.read() << 8 | Wire.read()) / 129.18 - this->angularVelError.z;
  //if 129.18 does not work, switch it for 131.0

  if (isInfOrNan(temp.x, "X") || isInfOrNan(temp.y, "Y") || isInfOrNan(temp.z, "Z")) {
    print_var_full("nan or infinity found (possible data corruption)", -1, "Gyro::readAngularVel");
    return FAILURE;
  } else {
    this->angularVel.x = temp.x;
    this->angularVel.y = temp.y;
    this->angularVel.z = temp.z;
    return SUCCESS;
  }
}

bool Gyro::isInfOrNan(float value, String msg) {
  if (value != value) {
    PRINT_VAR("found nan in", msg);
    return true;
  } else if (value < -(float)pow(10.0, 9.0)) {
    PRINT_VAR("found -inf in", msg);
    return true;
  } else if (value > (float)pow(10.0, 9.0)) {
    PRINT_VAR("found inf in", msg);
    return true;
  }
  
  return false;
}

void Gyro::angleFromAngularVel(float elapsedTime) {
  // Correct the outputs with the calculated error values
  // Currently the raw values are in degrees per seconds, deg/s, so we need to multiply by seconds (s) to get the angle in degrees
  this->gyroAngle.x += this->angularVel.x * elapsedTime; // deg/s * s = deg
  this->gyroAngle.y += this->angularVel.y * elapsedTime;
  this->gyroAngle.z += this->angularVel.z * elapsedTime;
}

int Gyro::updateGyro() { //has to be called frequently
  int err = this->readAngularVel();
  if (err == CRITICAL_FAILURE) {
   return CRITICAL_FAILURE; 
  } else if (err) {
    return FAILURE;
  }

  unsigned long prevTime = this->curTime;
  this->curTime = micros();
  float elapsedTime = ((float)curTime - (float)prevTime) / (float)1000000; // Divide by 1,000,000 to get seconds
  this->angleFromAngularVel(elapsedTime);
  return SUCCESS;
}

/**
 * @brief keep/normalise the angle values between -180 and 180 degrees. 
 * So 181 becomes 181 - 360 = -179.
 * The makes comparison easier, avoiding mistaking 0 and 360 degrees as different orientations.
 * 
 * @param angle the input angle value
 * @return int the normalised angle value
 */
int Gyro::boundedAngle(int angle) {
  while (angle > 180) {
    angle -= 360;
  }
  while (angle < -180) {
    angle += 360;
  }
  return angle;
}

int Gyro::getAngle() {
  if (isInfOrNan(this->gyroAngle.AXIS, "angle")) {
    print_var_full("the angle value is wrong:", this->gyroAngle.AXIS, "Gyro::getAngle");
  }
  return this->boundedAngle(round(this->gyroAngle.AXIS)); //a number from -180 to 180
}

int Gyro::getAngularVel() {
  return round(this->angularVel.AXIS);
}

// debugging
void Gyro::printInfo() {
  print_class_name("gyro");
  PRINT_VAR("getAngle()", this->getAngle());
  PRINT_VAR("gyroAngle", this->gyroAngle.toString());
  PRINT_VAR("angularVel", this->angularVel.toString());
  Serial.println(); //blank line for readability
  PRINT_VAR("angularVelError", this->angularVelError.toString());
  PRINT_VAR("curTime", this->curTime);
}
