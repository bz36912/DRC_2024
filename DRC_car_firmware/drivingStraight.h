#ifndef DRIVING_STRAIGHT_H
#define DRIVING_STRAIGHT_H

#include "commonlib.h"
#include "gyroSensor.h"
#include "motorControl.h"

//pinout
#define LED 13 // blinking LED to indicate the program is running normally (e.g. no memory or hardware fault)

#define BAUD_RATE 115200 //for UART serial communication

//car->state
#define ROTATE_STATE 0
#define DRIVE_FORWARD_STATE 1
#define PAUSED_STATE 2
#define SWING_LEFT_STATE 3
#define SWING_RIGHT_STATE 4

/**
 * @brief in degrees, turning angle above which the car will go from DRIVE_FORWARD_STATE into 
 * ROTATE_STATE, which spins the car about its axis. Below which the car will steer in 
 * a gentle turn like a real-life car on the road, instead of spinning about it central axis.
 */
#define MAX_DRIVING_ANGLE 60

//proportional control
#define PROPORTIONAL_COEFFECIENT 1.0
#define MAX_ANGULAR_VELOCITY 120
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
    int maxPWM;
    unsigned long lastConnectionTime;
    void Car::driving(int angleDiff, int velDiff, int maxPWM);
    void Car::rotate(int angleDiff, int velDiff);
    void Car::setState(int newState);
    String Car::state_string(int state);
    String Car::state_string_helper(int state);
    void Car::parse_cmd_string(String cmdStr);

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
