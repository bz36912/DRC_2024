#ifndef GYRO_SENSOR_H
#define GYRO_SENSOR_H

#include "commonlib.h"
#define MPU 0x68 // MPU6050 I2C address
#define AXIS x //if you mounted MPU6050 in a different orientation to me, AXIS may be x, y, z
//for me, turning right reduces angle. Turning left increases angle. If it is opposite for you, 
//consider multiplying the output of Gyro::getAngle() and int Gyro::getAngularVel() by -1

class Vector3D {
  public:
    Vector3D::Vector3D();
    String Vector3D::toString();
    float x;
    float y;
    float z;
};

//gyroSensor.cpp functions
class Gyro {
  private:
    //for angleFromAngularVel()
    unsigned long curTime; //in micro-seconds
    //values
    Vector3D angularVel;
    Vector3D gyroAngle;
    //for calculateError()
    Vector3D angularVelError;

    void Gyro::calculateError();
    int Gyro::readAngularVel();
    void Gyro::angleFromAngularVel(float elapsedTime);
    bool Gyro::isInfOrNan(float value, String msg);

  public:
    Gyro::Gyro();
    int Gyro::updateGyro();
    int Gyro::getAngle();
    int Gyro::boundedAngle(int angle);
    int Gyro::getAngularVel();
    void Gyro::printInfo();
    int Gyro::init(float initAngle);
    int Gyro::deinit();
};

#endif
