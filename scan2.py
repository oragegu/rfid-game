#!/usr/bin/python3
import serial
from time import sleep
receiver = serial.Serial('/dev/ttyACM0', 19200)
#receiver = serial.Serial('/dev/ttyUSB3', 115200)
#receiver = serial.Serial('/dev/ttyUSB0', 19200)

# Define the frequency range to EU standards <-doesn't work
freq_1_h = (864 >> 8) & 0xff
freq_1_l =  864 & 0xff
freq_2_h = (865 >> 8) & 0xff
freq_2_l =  865 & 0xff
freq_3_h = (868 >> 8) & 0xff
freq_3_l =  868 & 0xff 

#Define channels for ETSI
channel_h = 0x01
channel_l = 0x0A

# Define the address of the RFID tag
add_h = 0x46 # ==ord('F')
add_l = 0x46

# Define the antenna number
antenna = 0x01

# Calculate the BCC value

SOH = 0x01
STX = 0x02
ETX = 0X03
EOT = 0x04
ENQ = 0x05
ACK = 0x06
CR  = 0x0D
NAK = 0x15
SYN = 0x16

''' 
    STX (Start of Text) - typically used to indicate the beginning of a text message.
    SOH (Start of Header) - typically used to indicate the beginning of a header in a message.
    ACK (Acknowledge) - typically used to indicate that a message or command was received and understood by the receiving device.
    NAK (Negative Acknowledge) - typically used to indicate that a message or command was not received or was not understood by the receiving device.
    ENQ (Enquiry) - typically used to request a status or response from the receiving device.
    CR (Carriage Return) - typically used to indicate the end of a line of text and the beginning of a new one.
    EOT (End of Transmission) - typically used to indicate the end of a message or transmission.
'''

def translate_ascii(s):
    s=str(s)
    wrd=""
    #st=[]
    for i in range(0,len(s)-1,2):
        wrd+=(chr(int(s[i]+s[i+1],16))) 
        #st.append(int(s[i]+s[i+1],16))
    #print(st)
    return(wrd)    

def checksum_bb_cmd(ptBuffer:bytes, nLength:int) -> int:
    bChecksum = 0
    for nCounter in range(nLength):
        bChecksum ^= ptBuffer[nCounter]
    if (bChecksum == SOH or bChecksum == EOT or bChecksum == CR):
        bChecksum += 1
    return bChecksum

def order(orders, header=[SOH,add_h,add_l,STX],size=26,prt=True,check=True):
    #consider general order
    bytes_data = header + orders #header + order
    if check:
        bcc = checksum_bb_cmd(bytes_data, len(bytes_data))
        bytes_data += [bcc,CR] # +tail
    else:
        bytes_data += [CR] # +tail
        
    receiver.write(bytes_data)
    receiver.timeout = 1
    rx = receiver.read(size=8*(len(bytes_data)+size)) #arbitrary 26 firmware brings 16 chars
    if prt:    
        print("str(rx):"+str(rx)) #b'\x01FF\x022A01219515420048\x03s\r'
        print("str(rx,utf8):"+str(rx, 'utf-8')) #FF2A01219515420048s
    ack_message = [SOH,add_h,add_l,ACK]
    ack_message += [checksum_bb_cmd([SOH,add_h,add_l,ACK],4), CR]
    receiver.write(ack_message)
    receiver.reset_input_buffer() #flushInput disapeared version 3
    return(rx)

def split_rx(rx, text="answer",skip=0,split="\\"):
    answer= str(rx).split(split)
    if isinstance(answer, list):
        if len(answer)>2:
            return (answer[2][(skip):len(answer[2])])
        if len(answer)>1:
            return (answer[1][(skip):len(answer[1])])
        return (answer[0][(skip):len(answer[0])])
    
    elif isinstance(answer, str):
        return answer[(skip):len(answer[1])]
    return (text+" not even a str")

def check_device():
    bytes_data = [SOH,add_h,add_l,STX]+[ord('2'),ord('A'),ord('0'),ord('1'),ETX]
    bcc = checksum_bb_cmd(bytes_data, len(bytes_data))
    bytes_data += [bcc,CR]
    receiver.write(bytes_data)
    receiver.timeout = 1
    rx = receiver.read(size=8*(len(bytes_data)+26)) #b'\x01FF\x022A01219515420048\x03s\r'
    dev=str(rx).split("\\")[2]
    print("device #",dev[7:len(dev)]) 
    ack_message = [SOH,add_h,add_l,ACK]
    ack_message += [checksum_bb_cmd([SOH,add_h,add_l,ACK],4), CR]
    receiver.write(ack_message)
    receiver.reset_input_buffer()
    
def show_first_read_tag():
    bytes_data = [SOH,ord('F'),ord('F'),ENQ,ENQ,CR] # ENQ =0x05
    receiver.write(bytes_data)
    receiver.timeout = 1
    tag_code=""
    rx = receiver.read(size=39)
    if rx.hex() != '014646023030303030303030303003000d':  # ignore empty response (when no tag scanned)
        tag_code = str(rx[4:36], 'utf-8')
        print("show_first_read_tag: " + tag_code)
        #receiver.write(b'01464606070D') #(SOH,F,F,ACK,bcc=0x07,CR)
        #sleep(0.1)
        #receiver.reset_input_buffer()
        ack_message = [SOH,add_h,add_l,ACK]
        ack_message += [checksum_bb_cmd([SOH,add_h,add_l,ACK],4), CR]
        receiver.write(ack_message)
    receiver.reset_input_buffer()
    return tag_code

def register_x_tags(x: int):
    i=0    
    while(i<x):
        rx=order(header=[SOH], orders=[ord('F'),ord('F'),ENQ,ENQ],check=False)# works
        print("tag: "+ split_rx(rx))
    return rx



def RSSI():
    #to send:
    #SOH <add h> <add l> STX ‘F’ ‘D’ ‘0’ <antenna> <freq 1 h> <freq 1 l>
    #<freq 2 h> <freq 2 l> <freq 3 h> <freq 3 l> ETX <bcc> CR
    bytes_data = [SOH,add_h,add_l,STX] #header
    bytes_data += [ord('F'),ord('D'),ord('0'),antenna,freq_1_h,freq_1_l,freq_2_h,freq_2_l,freq_3_h,freq_3_l,ETX]
    bcc = checksum_bb_cmd(bytes_data, len(bytes_data)) #bcc takes everything
    bytes_data += [bcc,CR] #tail
    #to_be_bcced = [ord('F'),ord('D'), ord('0'), antenna, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l]#was too short
    #bcc = checksum_bb_cmd(to_be_bcced, len(to_be_bcced))
    #bcc = ord('F')^ord('D')^ord('0')^antenna^freq_1_h^freq_1_l^freq_2_h^freq_2_l^freq_3_h^freq_3_l
    #print("RSSI bcc: "+str(bcc)) #<- 122 en boucle spam
    #bytes_data = [0x01,add_h,add_l,0x02,ord('F'),ord('D'), ord('0'), antenna, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l, 0x03, bcc, 0x0d]
    # bytes_data = [0x01,add_h,add_l,0x02,0x46,0x44, 0x30, 0x01, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l, 0x03, 0x00, 0x0d]
    # The frequency to test in MHz in the range 840 – 960
    # MHz. 3-bytes ASCII encoded value
    print("order for rrssi: ")
    print(bytes_data)
    receiver.write(bytes_data)
    receiver.timeout = 3
    #SOH <add h> <add l> STX ‘F’ ‘D’ <I-ch h> <Ich l> <Qch h> <Qch l> 
    # <G h> <G l> ETX <bcc> CR
    rx = receiver.read(size=8*(len(bytes_data)+16)) #larger
    print("RSSI str(rx):"+str(rx)) #b'\x01FF\x022A01219515420048\x03s\r'
    print("RSSI str(rx,utf8):"+str(rx, 'utf-8')) #0102...
    rssi=str(rx).split("\\")
    print (str(rssi))
    if (len(str(rssi)) > 2):  # ignore empty response (when no tag scanned)  
        #rssi=str(rx).split("\\")[2]
        print("rssi part should be 6x2 chars#",rssi[8:len(rssi)]) #STX = 6 chr F and D 2 we start on 9th ch
        #rx.hex() != '014646023030303030303030303003000d' and 
        print("RSSI: rx should not be empty")
        print("RSSI len(rx): "+str(len(str(rx))))
        print("RSSI str(rx): "+str(rx))
        #rssi = str(rx[6:11], 'utf-8')
        #print("RSSI value: "+rssi)
        #receiver.write(b'01464606070D')
        #sleep(1)
        ack_message = [SOH,add_h,add_l,ACK]
        ack_message += [checksum_bb_cmd([SOH,add_h,add_l,ACK],4), CR]
        receiver.write(ack_message)
    receiver.reset_input_buffer()
    return rssi

def Read_reflected_power():
    to_be_bcced = [ord('F'),ord('E'), ord('0'), antenna, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l]
    bcc = checksum_bb_cmd(to_be_bcced, len(to_be_bcced))
    bytes_data = [0x01,add_h,add_l,0x02,ord('F'),ord('E'), ord('0'), antenna, freq_1_h, freq_1_l, freq_2_h, freq_2_l, freq_3_h, freq_3_l, 0x03, bcc, 0x0d]
    # SOH <add h> <add l> STX ‘F’ ‘D’ ‘0’ <antenna> <freq 1 h> <freq 1 l>
    #<freq 2 h> <freq 2 l> <freq 3 h> <freq 3 l> ETX <bcc> CR
    # The frequency to test in MHz in the range 840 – 960
    # MHz. 3-bytes ASCII encoded value
    receiver.write(bytes_data)
    receiver.timeout = 5
    rx = receiver.read(1024)
    #print("printing rx")
    #print(rx)
    #print(":)")
    if rx.hex() != '014646023030303030303030303003000d' and len(str(rx)) > 3:  # ignore empty response (when no tag scanned)
        print("Read_reflected_power: coucou")
        tag_code = str(rx[6:11], 'utf-8')
        print("Read_reflected_power tag code: "+tag_code)
        receiver.write(b'01464606070D')
        sleep(1)
        receiver.reset_input_buffer()

def main():
    x=0
    check_device() #specifif function for device
    
    #general order function, here for firmware
    rx=order([ord('3'),ord('4'),ETX],prt=False) #this is the core of firmware request bytes_data
    print("firmware: "+ translate_ascii(split_rx(rx,skip=5))) #added an hexadec->char conv
    
    #now for temperature:
    rx=order([ord('3'),ord('A'),ETX],prt=False) 
    print("temp: "+ str( int(split_rx(rx,skip=5)[0:2]) + 0.125*int(split_rx(rx,skip=5)[2],16))+ "°C") #

    #status reading ‘3’ ‘6’ ETX
    rx=order([ord('3'),ord('6'),ETX],prt=False) 
    print("status: "+ translate_ascii(split_rx(rx,skip=5))) 
    
    #read  general RAM parametters
    rx=order([ord('2'),ord('A'),ETX],prt=False,size=48) 
    print("parametters: "+ split_rx(rx,skip=0))
    #SOH <add h> <add l> STX '3' 'C' <page h> <page l> ETX <bcc> CR
    
    #read RAM config parameters - 14 if configuration page is 0x80 ... 0x87
    rx=order([ord('3'),ord('C'),0x01,0x87,ETX],prt=True,size=108) 
    print("RAM config pp 1-7: "+ split_rx(rx,skip=0))
    
    #read ROM config parameters - 14 if configuration page is 0x80 ... 0x87
    rx=order([ord('3'),ord('E'),0xC0,0xCF,ETX],prt=True,size=108) 
    print("ROM config pp 1-7: "+ split_rx(rx,skip=0))
    

    
    while(x < 2):
        rx=0
        tag=""
        sleep(0.5)
        #adaptation of the show next tag order
        rx=order(header=[SOH], orders=[ord('F'),ord('F'),ENQ,ENQ],check=False)# works
        #rx=order(orders=[ord('F'),ord('F'),ENQ,ENQ,ETX]) #though properly written this makes a NAK
        print("tag: "+ split_rx(rx)) #
        
        #test of a RF power function p40
        #ETSI channels h: 0x01 and l: 0x0A
        rx=order([ord('D'),ord('A'),ord('0'),antenna,channel_h,channel_l,ETX],prt=False) #
        print("RF power: "+ split_rx(rx)) #
        '''tag: SOH <add h> <add l> STX ‘D’ ‘A’ ‘0’ ‘0’ <power h> <power l> ETX <bcc> CR
        no tag: SOH <add h> <add l> STX ‘D’ ‘A’ ‘0’ ‘1’ ETX <bcc> CR'''

        #RF sensitivity
        '''SOH <add h> <add l> STX ‘D’ ‘B’ ‘0’ <antenna> <channel h> <channel l> ETX <bcc> CR'''
        rx=order([ord('D'),ord('B'),ord('0'),antenna,channel_h,channel_l,ETX],prt=True) #
        print("RF sensitivity: "+ split_rx(rx)) #
        '''tag: SOH <add h> <add l> STX ‘D’ ‘B’ ‘0’ ‘0’ <sens h> <sens l> ETX <bcc> CR'''       

        #Reflected power
        '''SOH <add h> <add l> STX ‘F’ ‘E’ ‘0’ <antenna> <freq 1 h> <freq 1 l>
            <freq 2 h> <freq 2 l> <freq 3 h> <freq 3 l> ETX <bcc> CR'''
        rx=order([ord('F'),ord('E'),ord('0'),antenna,freq_1_h,freq_1_l,freq_2_h,freq_2_l,freq_3_h,freq_3_l,ETX],prt=True) #
        print("Reflected power: "+ split_rx(rx)) #
        '''SOH <add h> <add l> STX ‘F’ ‘E’ <I-ch h> <Ich l> <Qch h> <Qch l> <G h> <G l>
            ETX <bcc> CR'''       

        #RSSI power
        '''SOH <add h> <add l> STX ‘F’ ‘D’ ‘0’ <antenna> <freq 1 h> <freq 1 l>
            <freq 2 h> <freq 2 l> <freq 3 h> <freq 3 l> ETX <bcc> CR'''
        rx=order([ord('F'),ord('D'),ord('0'),antenna,freq_1_h,freq_1_l,freq_2_h,freq_2_l,freq_3_h,freq_3_l,ETX],prt=True) #
        print("RSSI power: "+ split_rx(rx)) #
        '''SOH <add h> <add l> STX ‘F’ ‘D’ <I-ch h> <Ich l> <Qch h> <Qch l> <G h> <G l>
            ETX <bcc> CR'''  

#        tag=show_first_read_tag()
 #       print("print tag; "+tag)
        #print("length of tag")
  #      length = len(str(tag))
        #print(length)
   #     if (len(str(tag))>0):
        #res = RSSI()
        #print("RSSI length: "+str(len(res)))
        #print("res: ")
        #print(res)
        #Read_reflected_power(rx)
        print("in while loop "+ str(x))
        #receiver.write(b'01464606070D')
        #sleep(1)
       # receiver.reset_input_buffer()
        x+=1
        receiver.close()
        #exit
#main()


