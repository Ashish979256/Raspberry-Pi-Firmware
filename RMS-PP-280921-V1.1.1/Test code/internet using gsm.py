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
port.write(b'AT+CHTTPACT="13.234.86.197",80'+b'\r\n')
time.sleep(3)
rcv = port.read(200)
print (rcv)

port.write(b'GET /index.html HTTP/1.1'+b'\r\n')

port.write(b'HOST:http://www.holmiumtechnologies.com'+b'\r\n')
port.write(b'User-Agent:MY WEB AGENT'+b'\r\n')

port.write(b'Content-Length:44'+b'\r\n')
port.write(b'<CTRL+Z>'+b'\r\n')

time.sleep(5)
rcv = port.read(2000)
print (rcv)
time.sleep(5)
rcv = port.read(2000)
print (rcv)

time.sleep(5)
rcv = port.read(2000)
print (rcv)





