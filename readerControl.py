import sys
import serial 

# ---- constants ----------------------------------------------------------------------------------

DEVICE_PATH = '/dev/ttyUSB0'

MIN_POWER = -15
MAX_POWER = 32


GREATING = """
    
******************************* RFID UHF READER INTERFACE *************************************

Welcome to the RFID UHF reader interface, to control the reader, press "help" to display the
availables commands.

"""

MAIN_MENU = """

"s" : Start inventory
"a" : Display current settings
"e" : Settings
"q" : Quit

"""

SETTINGS_MENU = """

"z" : Zone
"o" : Output mode
"p" : Output power

"""

SETTINGS_ZONE_MENU = """

"e" : Europa (EU)
"u" : United States (US)

"""

SETTINGS_MODE_MENU = """

"l" : Low power mode
"h" : High power mode

"""

# commands
SSTS = "SSTS k0"
ERZO = "ERZO k0"
EROP = "EROP k0"
EROM = "EROM k0"
ARZO = "ARZO k0"
AROP = "AROP k0"
AROM = "AROM k0"

# -------------------------------------------------------------------------------------------------

def send_cmd(cmd):
    str = '0220'+cmd.encode('utf-8').hex()+'03'
    #print('\n\n{}'.format(str))
    rep = ''
    with serial.Serial(DEVICE_PATH, 115200, timeout=2) as ser:
        ser.write(bytearray.fromhex(str))
        rep = ser.read(300).decode('utf-8')
        print('rep : {}'.format(rep))

def send_cmd_with_args(cmd, arg):
    str = '0220'+cmd.encode('utf-8').hex()+'20'+arg.encode('utf-8').hex()+'03'
    rep = ''
    with serial.Serial(DEVICE_PATH, 115200, timeout=1) as ser:
        ser.write(bytearray.fromhex(str))
        rep = ser.read(32).decode('utf-8')
        print('rep : {}'.format(rep))
        rep = int(rep[7:8])
    if(rep):
        print('\nerror, configuration not set!')
        print('error code : {}'.format(rep))
    else:
        print('\nconfiguration set!')
    return rep

def read_config(cmd):
    str = '0220'+cmd.encode('utf-8').hex()+'03'
    with serial.Serial(DEVICE_PATH, 115200, timeout=1) as ser:
	    ser.write(bytearray.fromhex(str))
	    out = ser.read(32)[9:11].decode('utf-8')
    return out

def setting_power_menu():
    while(True):        
        power = int(input("Enter output power in [dBm] from -15 to 32 :"))
        if(power >= MIN_POWER and power <= MAX_POWER):
            send_cmd_with_args(EROP, str(power))            
            break

def setting_mode_menu():
    while(True):
        print(SETTINGS_MODE_MENU)
        submenu = input("select submenu shortcut :")
        if submenu == 'l':            
            send_cmd_with_args(EROM, 'LP')
            print('Low power mode set')
            break
        if submenu == 'h':            
            send_cmd_with_args(EROM, 'HP')
            print('High power mode set')
            break

def setting_zone_menu():
    while(True):
        print(SETTINGS_ZONE_MENU)
        submenu = input("select submenu shortcut :")
        if submenu == 'e':
            if not send_cmd_with_args(ERZO, 'EU'):
                print('Zone set to "EU"')
            break
        if submenu == 'u':
            if not send_cmd_with_args(ERZO, 'US'):
                print('Zone set to "US"')
            break

def setting_menu():
    while(True):
        print(SETTINGS_MENU)
        submenu = input("select submenu shortcut :")
        if submenu == 'z':
            # send command -> control ack
            print('config zone menu')
            setting_zone_menu()
            break
        if submenu == 'o':
            # send command -> control ack
            print('config output mode menu')
            setting_mode_menu()
            break
        if submenu == 'p':
            # send command -> control ack
            print('config output power menu')
            setting_power_menu()
            break

def read_settings():
    zone = read_config(ARZO)
    mode = read_config(AROM)
    power = read_config(AROP)
    print("""
Current settings : Zone : {} 
Output mode : {} 
Output power : {} [dBm]""".format(zone, mode, power))

def scan():
    send_cmd(SSTS)
    print("\nStart scanning")

def main_menu():
    while(True):
        print(MAIN_MENU)
        submenu = input("select an action to do :")
        if submenu == 's':
            scan()
        if submenu == 'a':
            read_settings()
        if submenu == 'e':
            setting_menu()
        if submenu == 'q':
            break

if __name__ == "__main__":
    main_menu()
