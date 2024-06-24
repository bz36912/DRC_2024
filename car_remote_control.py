import serial
import keyboard
import threading
import time

class Uart():
    def __init__(self) -> None:
        self.terminateFlag = False
        self.ser = self._uart_init()
        send_key_thread = threading.Thread(target=self._send_key_command_thread)
        send_key_thread.start()
        checkConnectionThread = threading.Thread(target=self._connection_thread_entry)
        checkConnectionThread.start()

    def _uart_init(self) -> serial.Serial:
        port = "/dev/tty.REMOTE_CTRL"
        # port = "COM10"
        baud = 115200
        ser = serial.Serial(port, baud, timeout=0.1)
        print("Connected to Arduino port: " + port)
        return ser

    def _send_key_command_thread(self):
        print("send_key_command_thread(): start of function")
        oldKey = ""
        lastKeyPressTime = 0
        while True:
            key = keyboard.read_key()
            if key == "q": # quit the program
                self.terminateFlag = True
                print("exiting the _send_key_command_thread()")
                exit()
            elif key != oldKey or time.time() - lastKeyPressTime > 0.2:
                oldKey = key
                lastKeyPressTime = time.time()
                key_in_bytes = bytes(key + "\n", 'utf-8')
                print(key_in_bytes, type(key_in_bytes))
                self.ser.write(key_in_bytes)

    def _connection_thread_entry(self):
        num_missed_ACK = 0
        while (True):
            self.ser.write(bytes("#\n", 'utf-8'))
            time.sleep(0.45)
            num_missed_ACK += 1
            lines = self.ser.readlines()
            for line in lines:
                line = line.decode('utf-8').strip(" \n\r")
                if line == '#': # '#' is echoed back so UART is still connected
                    num_missed_ACK = 0
                else:
                    print(line)                
            
            if num_missed_ACK % 20 == 1:
                print(num_missed_ACK, "no ACK")
            
            if self.terminateFlag:
                print("exiting the _connection_thread_entry()")
                exit()

    def send_command(self, direction:int, maxPWM:int=-1):
        self.ser.write(bytes(f"/ {direction} {maxPWM}\n", 'utf-8'))

if __name__ == "__main__":
    print("start of program")
    uart = Uart()

    # testing uart
    # time.sleep(3)
    # uart.send_command(30, 100) # use this in the GUI
    # time.sleep(3)
    # uart.send_command(-45, 120)
    while True:
        time.sleep(1)
        if uart.terminateFlag: # use this GUI to check if q is pressed to terminate program
            break
    print("end of the program")
