
import serial
from time import sleep
receiver = serial.Serial('/dev/ttyACM0', 19200)
#receiver = serial.Serial('/dev/ttyUSB3', 115200)

# Define the frequency range
freq_1_h = 0x03
freq_1_l = 0xE8
freq_2_h = 0x03
freq_2_l = 0xF0
freq_3_h = 0x03
freq_3_l = 0xF8

# Define the address of the RFID tag
add_h = 0x46
add_l = 0x46

# Define the antenna number
antenna = 0x01

# Calculate the BCC value
bcc = add_h ^ add_l ^ ord('F') ^ ord('D') ^ ord('0') ^ antenna ^ freq_1_h ^ freq_1_l ^ freq_2_h ^ freq_2_l ^ freq_3_h ^ freq_3_l

def show_first_read_tag(rx):
    bytes_data = [0x01,add_h,add_l,0x05,0x05,0x0d]
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
    bytes_data = [0x01,add_h,add_l,0x02,0x46,0x44, 0x01, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l, 0x03, 0x7d, 0x0d]
    # SOH <add h> <add l> STX ‘F’ ‘D’ ‘0’ <antenna> <freq 1 h> <freq 1 l>
    #<freq 2 h> <freq 2 l> <freq 3 h> <freq 3 l> ETX <bcc> CR
    # The frequency to test in MHz in the range 840 – 960
    # MHz. 3-bytes ASCII encoded value
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
receiver.close()