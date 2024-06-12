// void setup1() {
//   Motor motor = Motor();
//   motor.forward();
//   Serial.begin(BAUD_RATE);
//   motor.setSpeedTo(MAX_SPEED, RIGHT);
// //  motor.setSpeedTo(MIN_SPEED, LEFT);
//   while(1) {
//     for (int aSpeed = 160; aSpeed < 255; aSpeed += 25) {
//       PRINT_VAR("aSpeed", aSpeed);
//       motor.setSpeedTo(aSpeed, LEFT);
//       delay(2000);
//     }

//     PRINT_VAR("aSpeed", MAX_SPEED);
//     motor.setSpeedTo(MAX_SPEED, LEFT);
//     delay(2000);
//   }
// }

// void setup() {
//   pinMode(LEFT_LED, OUTPUT);
//   pinMode(RIGHT_LED, OUTPUT);
//   digitalWrite(LEFT_LED, HIGH);
//   delay(500);
//   digitalWrite(RIGHT_LED, HIGH);
//   delay(500);
//   digitalWrite(RIGHT_LED, LOW);
//   digitalWrite(LEFT_LED, LOW);
  
//   Serial.begin(BAUD_RATE);
//   Serial.println("Press s to start car");
//   while (1) {
//     if(Serial.available()){
//       char c = Serial.read ();
//       if (c == 's') {
//         Serial.println("initialising the car");
//         break;
//       }
//     }
//   }
  
//   Car car = Car();
  
//   int count = 0;
//   while(1) {
//     car.gyro.updateVal();
//     car.getCommand();
//     if (count < NUM_CYCLE_PER_ADJUSTMENT) {
//       count++;
//     } else {
//       count = 0;
//       car.adjustMotion();
//     }
//   }
// }

// Car::Car() {
//   this->paused = false;
//   this->isDriving = false;
//   this->equilibriumSpeed = 248;
//   this->countStraight = 0;
//   this->prevIsDriving = true;
//   this->targetAngle = 0;
// }

// void Car::adjustMotion() {
//   if (!this->paused){
//     if (this->isDriving != this->prevIsDriving){ //a change in state
//       this->prevIsDriving = this->isDriving;
//       this->motor.setSpeedTo(this->equilibriumSpeed, LEFT);
//       this->countStraight = 0;
//       PRINT_VAR("isDriving", this->isDriving);
//       PRINT_VAR("equilibriumSpeed", this->equilibriumSpeed);
//     }
//     //rounding is neccessary, since you never get exact values in reality
//     int deltaAngle = (round(this->targetAngle - this->gyro.getAngle())) % 360;
//     if (deltaAngle > 180) {
//        deltaAngle = -(360 - deltaAngle);
//     }
    
//     if (isDriving) {
//       updateEquilibriumSpeed(deltaAngle);
//       driving(deltaAngle);
//     } else {
//       rotate(deltaAngle);
//     }
//   }
// }

// void Car::updateEquilibriumSpeed(int deltaAngle) {
//   if (abs(deltaAngle) < 3){
//     if (countStraight < 20) {//to find equilibrium speed, 20 consecutive readings needed to indicate car is going straight
//       this->countStraight++;
//     } else {
//       this->countStraight = 0;
//       this->equilibriumSpeed = this->motor.getSpeed(LEFT);
//     }
//   } else {
//     this->countStraight = 0;
//   }
// }

// #define PROPORTIONAL_COEFFECIENT 2 //on the website it is 2, but I adjust it to 1.2 for this code
// void Car::driving(int deltaAngle) {//called by void loop(), which isDriving = true
//   this->motor.forward();
//   if (deltaAngle == 0){
//     return;
//   }
  
//   //setting up proportional control, see Step 3 on the website
//   int targetGyroX = min(PROPORTIONAL_COEFFECIENT * deltaAngle, 60); //caps the value to a max of 60
//   targetGyroX = max(targetGyroX, -60);

//   int deltaVelocity = round(targetGyroX - this->gyro.getGyroX());
//   if (deltaVelocity != 0){ //so the speed needs to be adjusted
//     this->motor.incrementSpeed(deltaVelocity < 0 ? -1 : 1, LEFT);
//     // digitalWrite(deltaVelocity < 0 ? RIGHT_LED : LEFT_LED, HIGH);
//     // digitalWrite(deltaVelocity < 0 ? LEFT_LED : RIGHT_LED, LOW);
//   } else {
//     // digitalWrite(LEFT_LED, LOW);
//     // digitalWrite(RIGHT_LED, LOW);
//   }
//   this->motor.setSpeedTo(MAX_SPEED, RIGHT);
// }

// void Car::rotate(int deltaAngle) {//called by void loop(), which isDriving = false
//   int targetGyroX;
//   if (abs(deltaAngle) <= 3){
//     this->motor.stopCar();
//     return;
//   }
//   if (deltaAngle < 0) { //turn left
//     this->motor.left();
//   } else { //turn right
//     this->motor.right();
//   }

//   //setting up proportional control, see Step 3 on the website
//   targetGyroX = min(PROPORTIONAL_COEFFECIENT * abs(deltaAngle), 60); // caps the value at 60
  
//   int deltaVelocity = round(targetGyroX - abs(this->gyro.getGyroX()));
//   if (deltaVelocity != 0){ //so the speed needs to be adjusted
//     this->motor.incrementSpeed(deltaVelocity > 0 ? 1 : -1, LEFT);
//   }
//   this->motor.setSpeedTo(this->motor.getSpeed(LEFT), RIGHT);
// }

// void Car::getCommand() {
//   // Print the values on the serial monitor
//   if(Serial.available()){
//     char c = Serial.read();
//     if (c == 'w') { //drive forward
//       Serial.println("forward");
//       this->isDriving = true;
//     } else if (c == 'a') { //turn left
//       Serial.println("left");
//       this->targetAngle += 90;
//       if (this->targetAngle > 180) {
//         this->targetAngle -= 360;
//       }
//       PRINT_VAR("targetAngle", this->targetAngle);
//       PRINT_VAR("getAngle()", this->gyro.getAngle());
//       Serial.flush();
//       isDriving = false;
//     } else if (c == 'd') { //turn right
//       Serial.println("right");
//       this->targetAngle -= 90;
//       if (this->targetAngle <= -180) {
//         this->targetAngle += 360;
//       }
//       PRINT_VAR("targetAngle", this->targetAngle);
//       PRINT_VAR("getAngle()", this->gyro.getAngle());
//       Serial.flush();
//       this->isDriving = false;
//     } else if (c == 'q') { //stop or brake
//       Serial.println("stop");
//       this->isDriving = false;
//     } else if (c == 'i') { //print information. When car is stationary, GyroX should approx. = 0.
//       printInfo();
//       this->motor.printInfo();
//       this->gyro.printInfo();
//     } else if (c == 'p') { //pause the program
//       this->paused = !this->paused;
//       this->motor.stopCar();
//       isDriving = false;
//       PRINT_VAR("key p was pressed, paused", this->paused);
//     }
//   }
// }

// void Car::printInfo() {
//   print_class_name("CAR");
//   PRINT_VAR("paused", this->paused);
//   PRINT_VAR("isDriving", this->isDriving);
//   PRINT_VAR("prevIsDriving", this->prevIsDriving);
//   PRINT_VAR("equilibriumSpeed", this->equilibriumSpeed);
//   PRINT_VAR("countStraight", this->countStraight);
//   PRINT_VAR("targetAngle", this->targetAngle);
// }

#if defined(WIRE_HAS_TIMEOUT) // most Arduino IDE version should have timeout for I2C communications
Wire.setWireTimeout(1000, true);
#else // unless the IDE is very old. Note, without timeout, some Wire library functions can block forever, freezing the program
print_var_full("Your version of Arduino IDE does not seem to have timeout for I2C", -1, "Gyro::Gyro");
#endif

#if defined(WIRE_HAS_END)
print_var_full("Your version of Arduino IDE has wire.end()", -1, "Gyro::Gyro");
#else
print_var_full("Your version of Arduino IDE does NOT have wire.end()", -1, "Gyro::Gyro");
#endif