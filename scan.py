
import serial
from time import sleep
receiver = serial.Serial('/dev/ttyACM0', 115200)
#receiver = serial.Serial('/dev/ttyUSB3', 115200)

def show_first_read_tag(rx):
    bytes_data = [0x01,0x46,0x46,0x05,0x05,0x0d]
    receiver.write(bytes_data)
    receiver.timeout = 1
    rx = receiver.read(size=39)
    if rx.hex() != '014646023030303030303030303003000d':  # ignore empty response (when no tag scanned)
            tag_code = str(rx[4:36], 'utf-8')
            print(tag_code)
            receiver.write(b'01464606070D')
            sleep(1)
            receiver.flushInput()

def RSSI(rx):
    bytes_data = [0x01,0x46,0x46,0x05,0x05,0x0d]
    receiver.write(bytes_data)
    receiver.timeout = 1
    rx = receiver.read(size=39)
    if rx.hex() != '014646023030303030303030303003000d':  # ignore empty response (when no tag scanned)
            tag_code = str(rx[4:36], 'utf-8')
            print(tag_code)
            receiver.write(b'01464606070D')
            sleep(1)
            receiver.flushInput()

def main():
   
    while(True):
        rx=0
        sleep(0.5)
        show_first_read_tag(rx)

main()
