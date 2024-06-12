#ifndef DRIVING_STRAIGHT_H
#define DRIVING_STRAIGHT_H

#include "commonlib.h"
#include "gyroSensor.h"
#include "motorControl.h"

//pinout
#define LED 13

#define BAUD_RATE 115200 //for UART serial communication

//car->state
#define ROTATE_STATE 0
#define DRIVE_FORWARD_STATE 1
#define PAUSED_STATE 2

//proportional control
#define PROPORTIONAL_COEFFECIENT 1.0
#define MAX_ANGULAR_VELOCITY 60
#define FEEDBACK_TIME 20 //in ms

//handling an unintentional UART disconnect or fault
#define STOP_AFTER_DISCONNECT_FOR 1000 // in milli-seconds, which stops the car from moving
#define RESTART_UART_AFTER_DISCONNECT_FOR 3000 // in milli-seconds

//driving_straight_MPU6050_v2_pro.ino functions
class Car {
  private:
    int state;
    int targetAngle;
    int angleDifference;
    int velDifference;
    unsigned long lastConnectionTime;
    void Car::driving(int deltaAngle, int velDiff);
    void Car::rotate(int deltaAngle, int velDiff);
    void Car::setState(int newState);
    String Car::state_string(int state);
    String Car::state_string_helper(int state);

  public:
    void Car::adjustMotion();
    void Car::getCommand();
    bool Car::checkAndHandleDisconnect();
    Car::Car();
    void Car::printInfo();
    Motor motor;
    Gyro gyro;
};

#endif
