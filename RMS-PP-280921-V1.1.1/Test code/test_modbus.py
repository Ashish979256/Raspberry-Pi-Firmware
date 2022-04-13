import pymodbus
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ModbusSerialClient 

#select client type 1 is used to select and 0 is used for not selecting
tcpClient=0
serialClient=1
#---------------------------------------#


#select these according to your work
readReg = 1
writeReg = 0
#----------------------------------#

if(tcpClient==1):
    print("tcp/ip")
    client = ModbusTcpClient('192.168.10.2', port=502)
if(serialClient):
    print("serial")
    client = ModbusSerialClient(method = 'rtu', port = '/dev/ttyAMA0' , baudrate = 9600, timeout = 2, parity = 'N')

print(client.connect())
pymodbus.__doc__
if(readReg ==1):
    print("selected readingRegisters")
    funCode ='3'
    regStart =0
    regLength =10
    slaveId =1
    for i in range(0,100):
        try:
            print("reading register")
            if(funCode=='3'):
                #print("function Code=3")
                #print("regStart =",regStart)
                #print("regLength =",regLength)
                #print("slaveId =",slaveId)
                x = client.read_holding_registers(regStart,regLength,unit = slaveId)
            if(funCode =='4'):
                print("functionCode=4")
                x = client.read_input_registers(regStart,regLength,unit = slaveId)
            #x= client.write_register(62208,1,unit=1)
            if(x.isError()==True):
                print("error")
                
            if (x.isError()!=1):
                print("success")
                print(x)
                #print(x.getRegister(i))
                for i in range(0,regLength):
                    print(x.getRegister(i))
            #print(x.getRegister(1))
            
        except Exception as e:
            print("Error :",e)
        time.sleep(3)

if(writeReg ==1):
    print("selected writing Registers")
    regWriteAddress =48512
    regWriteValue = 1
    regStartRead = 48512
    regLenthRead = 1
    funCodeRead = '4'
    slaveId = 1 
    for i in range(0,100):
        try:
            print("write register")
            x = client.write_register(regWriteAddress,regWriteValue,unit = slaveId)
            #x= client.write_register(62208,1,unit=1)
            print(x)
            if(x.isError()==True):
                print("error")
                
            if (x.isError()!=1):
                print("success")
                
                #print(x.getRegister(i))
            print("read register")
            if(funCodeRead =='3'):
                x = client.read_holding_registers(regStartRead,regLengthRead,unit = slaveId)
            if(funCodeRead=='4'):
                x = client.read_input_registers(regStartRead,regLengthRead,unit = slaveId)
                
            if(x.isError()==True):
                print("error")
                
            if (x.isError()!=1):
                print("success")
            for i in range(0,regLength):
                print(x.getRegister(i))
                #print(x.getRegister(1))
            
        except Exception as e:
            print("Error")
        time.sleep(3)
    
