import serial   
import os, time
from subprocess import call

print("calling internet off ...")
internetOFF=call(["sudo","poff","rnet"])
if not(internetOFF==1):
    time.sleep(3)
# Enable Serial Communication
port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
 
# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key
port.write(b'AT'+b'\r\n')
rcv = port.read(40)
print (rcv)






