# Usage
When the car is ready, it will print "Ready!" to the serial/UART terminal.
"starting program... Pls wait." doe NOT mean it is ready.

# Error Code (ERROR #)
1. Probably due to EMI/ESD from the motors or power supply interfering with MPU6050's I2C communication. This usually requires hardware fixes, such as adding shunt ceramic capacitor to filter out high-frequency noise or get a high quality power supply.

# To Do
Need to clarify the difference between driving and rotate