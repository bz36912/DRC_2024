/*To understand the context and purpose of this code, visit:
 * https://www.instructables.com/How-to-Make-a-Robot-Car-Drive-Straight-and-Turn-Ex/
 * This code makes references to steps on this Instructables website
 * written by square1a on 2nd July 2023
 * 
 * Acknowledgement:
 * some of the MPU6050-raw-data-extraction code in gryoSensor.cpp and most in calculateError() are written by Dejan from:
 * https://howtomechatronics.com/tutorials/arduino/arduino-and-mpu6050-accelerometer-and-gyroscope-tutorial/
*/
#include "drivingStraight.h"
Car::Car() {
  this->state = PAUSED_STATE;
  this->targetAngle = 0;
  this->lastConnectionTime = millis();
  this->maxPWM = MAX_SPEED;
}

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(1000);
  Serial.println("starting program... Pls wait.");
  delay(200); // when the reset button is just pressed, it wobbles the gyroscope. So wait till wobble stops.
  Car car = Car(); // includes the gyroscope and motor initialisation
  Serial.println("Ready!");
  
  unsigned long int prevTime = millis(); // for cycling the motor control loop
  // for the debugging LED
  bool LEDState = LOW;
  pinMode(LED, OUTPUT);
  unsigned long int prevLEDTime = millis();

  
  while(1) {
    if (car.gyro.updateGyro() == CRITICAL_FAILURE) {
      car.motor.stopCar();
      PRINT_VAR("MPU6050's I2C communication got critical error. ERROR", 1);
    }
    car.getCommand();
    if (!car.checkAndHandleDisconnect() and millis() - prevTime > FEEDBACK_TIME) {
      prevTime = millis();
      car.adjustMotion();
    }
    
    if (millis() - prevLEDTime > 1000) {
      prevLEDTime = millis();
      LEDState = !LEDState;
      digitalWrite(LED, LEDState); //toggles the LED
    }
  }
}

bool Car::checkAndHandleDisconnect() {
  /**
   * @brief the lastConnectionTime class variable is updated by calling Car::getCommand(), 
   * which reads from the UART buffer. If the UART buffer is empty for a long time, then
   * the UART connection was lost/disconnected.
   * 
   * Return true if a disconnection is detected and the car will be stopped from moving
   * Return false if the car is still connected via UART
   */
  
  if (millis() - this->lastConnectionTime > STOP_AFTER_DISCONNECT_FOR) {
    Serial.println("stop the car due to UART disconnect");
    this->motor.stopCar();
    this->state = PAUSED_STATE;
    delay(1000);
    return true;
  }
  return false;
}

void Car::adjustMotion() {
  int angle = this->gyro.getAngle();
  int angleDiff = this->gyro.boundedAngle(targetAngle - angle);
  int angularVel = this->gyro.getAngularVel();
  
  //setting up proportional control, see Step 3 on the website
  int targetVel = min(round(PROPORTIONAL_COEFFECIENT * (float)angleDiff), MAX_ANGULAR_VELOCITY); //caps the value to a max of 60
  targetVel = max(targetVel, -MAX_ANGULAR_VELOCITY);
  int velDiff = targetVel - angularVel;
  //for debug prints
  this->angleDifference = angleDiff;
  this->velDifference = velDiff;

  switch (this->state) {
    case ROTATE_STATE:
    this->rotate(angleDiff, velDiff);
    break;
    case DRIVE_FORWARD_STATE:
    this->driving(angleDiff, velDiff, this->maxPWM);
    break;
    case PAUSED_STATE:
    this->motor.stopCar(); //remain stationary
    break;
    default:
    print_var_full("unrecognised state", this->state, "Car::adjustMotion");
  }
}

void Car::driving(int angleDiff, int velDiff, int maxPWM) {
  this->maxPWM = maxPWM;
  if (angleDiff == 0){ // it already driving in the correct direction, so no adjustment is needed
    return;
  }

  int increment = abs(velDiff);
  if (velDiff > 0) { // it needs to turn left faster or right slower
    int roomToIncrease = maxPWM - this->motor.getSpeed(RIGHT);
    this->motor.incrementSpeed(min(increment, roomToIncrease), RIGHT);
    if (increment > roomToIncrease) { // if there is left over
      this->motor.incrementSpeed(-(increment - roomToIncrease), LEFT);
    }
  } else {
    int roomToIncrease = maxPWM - this->motor.getSpeed(LEFT);
    this->motor.incrementSpeed(min(increment, roomToIncrease), LEFT);
    if (increment > roomToIncrease) { // if there is left over
      this->motor.incrementSpeed(-(increment - roomToIncrease), RIGHT);
    }
  }
}

void Car::rotate(int angleDiff, int velDiff) {
  if (abs(angleDiff) <= 3){
    this->motor.stopCar();
    return;
  }
  if (angleDiff > 0) { //turn left !!!!might need to switch pin definition
    this->motor.left();
  } else { //turn right
    this->motor.right();
  }

  if (velDiff == 0){
    //do nothing
  } else if (velDiff * angleDiff > 0) { //both velocities are positive or both negative, so in the same direction
    this->motor.incrementSpeed(1, LEFT); //increase motor speed
  } else { //velocities are in the opposite direction
    this->motor.incrementSpeed((int)(-abs(velDiff) / 5 - 1), LEFT);
  }
  this->motor.setSpeedTo(this->motor.getSpeed(LEFT), RIGHT); // in rotate mode, left and right motor have the same speed
}

void Car::parse_cmd_string(String cmdStr) {
  char* str = cmdStr.c_str();
  char* token = strtok(str, " ");
  char* changeInDir = strtok(NULL, " ");
  char* maxPWM = strtok(NULL, " ");
  if (changeInDir != NULL) {
    this->targetAngle = gyro.boundedAngle(this->targetAngle + atoi(changeInDir));
  }
  if (maxPWM != NULL) {
    this->maxPWM = atoi(maxPWM);
  }
}

void Car::getCommand() {
  // Print the values on the serial monitor
  if(Serial.available()){
    String line = Serial.readStringUntil('\n');
    Serial.println(line);
    if (line == "#") {
      this->lastConnectionTime = millis();
      Serial.print("#\n");
    } else if (line.charAt(0) == '/') {
      this->parse_cmd_string(line);
    } else if (line == "w") { //drive forward
      Serial.println("forward");
      this->setState(DRIVE_FORWARD_STATE);
    } else if (line == "a") { //turn left
      this->setState(DRIVE_FORWARD_STATE);
      this->targetAngle = gyro.boundedAngle(this->targetAngle + 30);
      PRINT_VAR("turn left, target", this->targetAngle);
    } else if (line == "d") { //turn right
      this->setState(DRIVE_FORWARD_STATE);
      this->targetAngle = gyro.boundedAngle(this->targetAngle - 30);
      PRINT_VAR("turn right, target", this->targetAngle);
    } else if (line == "p") { //pause the program and stop the car
      Serial.println("paused");
      this->setState(PAUSED_STATE);
    } else if (line == "i") { //print information. When car is stationary, GyroX should approx. = 0.
      this->printInfo();
    }
  }
}

void Car::setState(int newState) {
  switch (newState) {
    case DRIVE_FORWARD_STATE:
    this->motor.forward();
    this->motor.setSpeedTo(MAX_SPEED, RIGHT); 
    //my right motor is weaker than the left motor, so I set right motor to max speed
    this->motor.setSpeedTo(EQUILIBRIUM_SPEED, LEFT);
    break;
    case ROTATE_STATE:
    this->motor.setSpeedTo(MIN_SPEED, RIGHT);
    this->motor.setSpeedTo(MIN_SPEED, LEFT);
    break;
    default:
    //do nothing
    break;
  }
  this->state = newState;
}

// debugging prints
void Car::printInfo() {
  print_class_name("CAR");
  PRINT_VAR("state", this->state_string(this->state));
  PRINT_VAR("targetAngle", this->targetAngle);
  PRINT_VAR("angleDifference", this->angleDifference);
  PRINT_VAR("velDifference", this->velDifference);

  this->motor.printInfo();
  this->gyro.printInfo();
}

String Car::state_string(int state) {
  return state_string_helper(state) + " (" + String(state) + ")";
}

String Car::state_string_helper(int state) {
  switch (state) {
    case ROTATE_STATE:
    return "ROTATE_STATE";
    case DRIVE_FORWARD_STATE:
    return "DRIVE_FORWARD_STATE";
    case PAUSED_STATE:
    return "PAUSED_STATE";
  }
  return "unknown";
}
