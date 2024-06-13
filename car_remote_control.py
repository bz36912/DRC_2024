import serial
import keyboard
import threading
import time

def uart_init() -> serial.Serial:
    port = "/dev/tty.REMOTE_CTRL"
    baud = 115200
    ser = serial.Serial(port, baud, timeout=0.1)
    print("Connected to Arduino port: " + port)
    return ser

def send_key_command_thread(ser:serial.Serial):
    print("send_key_command_thread(): start of function")
    oldKey = ""
    lastKeyPressTime = 0
    while True:
        key = keyboard.read_key()
        if key == "e":
            print("key e is pressed: program ended")
            exit()
        elif key != oldKey or time.time() - lastKeyPressTime > 1:
            oldKey = key
            lastKeyPressTime = time.time()
            key_in_bytes = bytes(key + "\n", 'utf-8')
            print(key_in_bytes, type(key_in_bytes))
            ser.write(key_in_bytes)

def main():
    print("start of program")
    ser = uart_init()
    send_key_thread = threading.Thread(target=send_key_command_thread, args=(ser,))
    send_key_thread.start()

    num_missed_ACK = 0
    while (True):
        ser.write(bytes("#\n", 'utf-8'))
        time.sleep(0.45)
        found_ACK = False
        lines = ser.readlines()
        for line in lines:
            line = line.decode('utf-8').strip(" \n\r")
            if line == '#':
                found_ACK = True
            else:
                print(line)

        if found_ACK:
            num_missed_ACK = 0
        else:
            num_missed_ACK += 1
        
        if num_missed_ACK % 20 == 1:
            print(num_missed_ACK, "no ACK")

        if not send_key_thread.is_alive():
            print("ending the main thread")
            exit()

if __name__ == "__main__":
    main()  
