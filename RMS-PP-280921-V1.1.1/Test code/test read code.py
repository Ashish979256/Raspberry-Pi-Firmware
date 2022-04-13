import pymodbus
from pymodbus.client.sync import ModbusTcpClient as ModbusClient,ModbusSerialClient
##from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time
import logging
from subprocess import call
from backports import configparser
from ast import literal_eval
##from pymodbus.client.sync import ModbusSerialClient
import numpy
import RPi.GPIO as GPIO
import random




POLL_RATE=0.01 #0.25
SCAN_RATE=0.1    #5

logging.basicConfig(filename = "../logs/error.log",format='%(asctime)s --Line: %(lineno)s--%(message)s', filemode = 'a')
errlogger = logging.getLogger()
errlogger.setLevel(logging.ERROR)

#----GPIO Initialization---#
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#------WMS COnfiguration----------#



#------Config File parameter check------#
errConfigFile = False
try:
    configDGSync = configparser.ConfigParser()
    configDGSync.read('../config/dg_sync.ini')
    if(len(configDGSync.sections()) == 0):
        print("DG Sync Config File is empty")
        call(['cp','../backup/dg_sync.ini','../config/dg_sync.ini'])
        

    plantProfile =  configDGSync['plant']
    print(plantProfile['noOfDG'])
    DGProfile = configDGSync['DGProfile']
    inverter = configDGSync['inverter']
    ControlDGSync = configDGSync['processControl']

    DGs = []
    for dg in list(DGProfile.keys()):
        DGs.append(literal_eval(DGProfile[dg]))
    print("DGs: ",DGs)
    print("\n")
    
    Inverters = []
    for inv in list(inverter.keys()):
        Inverters.append(literal_eval(inverter[inv]))
    print("Inverters: ",Inverters)
    print("\n")

    configZeroExport = configparser.ConfigParser()
    configZeroExport.read('../config/zero_export.ini')
    if(len(configZeroExport.sections()) == 0):
        print("Zero Export Config File is empty")
        call(['cp','../backup/zero_export.ini','../config/zero_export.ini'])
    plantProfile0export = configZeroExport['plant']
    gridProfile = configZeroExport['grid']
    inverter0 = configZeroExport['inverter']
    ControlExport = ['processControl']
    Grids = []
    for grid in list(gridProfile.keys()):
        Grids.append(literal_eval(gridProfile[grid]))
    print("Grids: ",Grids)
    print("\n")

    Inverters0 = []
    for inv0 in list(inverter0.keys()):
        Inverters0.append(literal_eval(inverter0[inv0]))
    print("Inverters0: ",Inverters)
    print("\n")

    configWMS= configparser.ConfigParser()
    configWMS.read('../config/wms.ini')
    if(len(configWMS.sections()) == 0):
        print("WMS Config File is empty")
        call(['cp','../backup/configWMS.ini','../config/configWMS.ini'])
    wms=configWMS['wms']
    wms_devices=[]
    for i in list(wms.keys()):
        wms_devices.append(literal_eval(wms[i]))
    print("wms_device",wms_devices)
    print("\n")
   
    
    
except Exception as errConfig:
    print("Error in retrieving Configuration File")
    errConfigFile = True
    print(errConfig)



#---------Paramter Initialization------------#
noOfDG = int(plantProfile['noOfDG'])
noOfGrid = int(plantProfile0export['noOfGrid'])
noOfInverter = int(plantProfile['noOfInverter'])
noOfInverter0 = int(plantProfile0export['noOfInverter'])
DGStatus = []
stateDG = []
lastDGState = []
GridStatus = []
stateGrid = []
lastGridState = []
IsSyncing = False
IsZeroExport = False
DGLoad = []
GridLoad = []
InvrPower = [0]*noOfInverter
InvrPower0 = [0]*noOfInverter0
flagRunDG = [0,0,0]
flagRunGrid = [0,0,0]
flagMinLoad = 0
StatusSolarMinLoad = 0
#---------------------------------------------#


#--------------GPIO Initialization-----------#
for countDG in range(0,noOfDG):
    DGStatus.append(1)
    lastDGState.append(True)
    stateDG.append(True)
    DGLoad.append(0)
    GPIO.setup(int(DGs[countDG]["PIN"]), GPIO.IN, pull_up_down=GPIO.PUD_UP)

for countGrid in range(0,noOfGrid):
    GridStatus.append(1)
    lastGridState.append(True)
    stateGrid.append(True)
    GridLoad.append(0)
    GPIO.setup(int(Grids[countGrid]["PIN"]), GPIO.IN, pull_up_down=GPIO.PUD_UP)

#--------------------------------------------------#


    




#client = ModbusClient(method = 'rtu', port = '/dev/ttyUSB0', baudrate = 9600, timeout = 2, parity = 'N')
#client = ModbusClient('192.168.0.104')
#print(client.connect())
#x = client.read_holding_registers(0,10,unit = 1)
#print(x.getRegister(0))

#function to retriev logger profile from file

def readWMS():
    DataString=''
    try:
        client = ModbusClient(method = 'rtu', port = '/dev/usb2485', baudrate = 9600, timeout = 2, parity = 'N')
        con=client.connect()
        if(con==True):
            for i in range(0,3):
                functionCode=wms_devices[i]["fc"]
                slaveId=wms_device[i]["slaveId"]
                startAdd=wms_device[i]["startAddress"]
                length= wms_device[i]["length"]
                try:
                    if(functionCode=='4'):
                        x=client.read_input_registers(startAdd,length,unit=slaveId)
                    elif(functionCode=='3'):
                        x=client.read_holding_registers(startAdd,length,unit=slaveId)
                    if(x.isError()):
                        print("Error")
                        return ''                        
                    for i in range(0, length):
                        y=str(x.getRegister(i))
                        DataString = DataString + y + ','
                except Exception as e:
                    print("error")
        else:
            print("No Connection")
            DataString=''
        client.close()
        return DataString
    except Exception as e:
        print("error")
        return ''



def loggerProfileFunction():
    try:
        with open('../config/logger.txt','r') as config_logger:
            logger = config_logger.readline()
        #print(logger)
        if not (logger):
            print("Recovery of Logger Profile")
            with open('../backup/logger.txt', 'r') as f:
                logger = f.readline()
            with open('../config/logger.txt', 'w') as f:
                f.write(logger)
            

        logger_split = logger.split(',')
        deviceCount = int(logger_split[0])
        #print(deviceCount)
        deviceId = logger_split[1]
        #print(deviceId)
        plantId = logger_split[2]
        #print(plantId)
        uploadIntv = int(logger_split[3])
        #print(uploadIntv)
        serialNo = logger_split[4]
        #print(serialNo)
        apn = logger_split[5]
        #print(apn)
        isRMS = logger_split[6]
        isDGSyncRun = logger_split[7]
        is0exportRun = logger_split[8]
        return deviceCount, deviceId, plantId, uploadIntv, serialNo, apn, isRMS, isDGSyncRun, is0exportRun
    except Exception as e:
        errlogger.error(e)
#function to retrieve device profile from file
def deviceProfileFunction(deviceCount):
    try:
        #create a dictionary for deviceProfile
        deviceProfileList = {}

        with open('../config/device.txt','r') as config_device:
            count = 0
            device = config_device.readlines()
            #print(device)
        if not (device):
            print("Recovery of DeviceProfile")
            with open('../backup/device.txt', 'r') as f:
                device = f.readlines()
            call(['cp', '../backup/device.txt','../config/device.txt'])
                
            
        while(count < deviceCount):
                
            
            device_split = device[count].split(',')
            print(device_split)

            deviceNo = device_split[0]
            #print(deviceNo)
            deviceType = device_split[1]
            #print(deviceType)
            funCode = device_split[2]
            #print(funCode)
            slaveId = int(device_split[3])
            #print(slaveId)
            no16Bit = int(device_split[4])
            #print(no16Bit)
            count16Bitregister = 0
            no32Bit = int(device_split[5])
            #print(no32Bit)
            count32Bitregister = 0
            registers16Bit = []
            registers32Bit = []

            index = 6
                
            while(count16Bitregister < no16Bit):
                registers16Bit.append(int(device_split[index]))
                #print(registers16Bit)
                index = index + 1
                count16Bitregister = count16Bitregister + 1

            while(count32Bitregister < no32Bit):
                registers32Bit.append(int(device_split[index])) 
                #print(registers32Bit)
                index = index + 1
                #print("Index: ",index)
                count32Bitregister = count32Bitregister + 1
                #print("Count32bit " ,count32Bitregister)

            
            ip_address = str(device_split[index])
            #print(ip_address)
##            index=index+1
            protocol = str(device_split[index+2])
            if(protocol == 'tcp'):
                port=int(device_split[index])
            elif(protocol == 'serial'):
                port=str(device_split[index])
            

                
            deviceProfileList[count] = [(deviceNo, deviceType, funCode, slaveId, no16Bit, no32Bit, registers16Bit, registers32Bit,ip_address,port,protocol)]
            count = count + 1
        
        print(deviceProfileList)
        return deviceProfileList
    except Exception as e:
        errlogger.error(e)


def get_Data(function, slaveId, no16Bit, no32Bit, registers16Bit, registers32Bit,ip_address,port,protocol):
    try:   
        print("IP Address-",ip_address)
        print("Port-",port)
        print("Protocol-",protocol)
        #print("Function - ",function)
        print("Slave ID - ",slaveId)
        #print("No of 16 Bit - ",no16Bit)
        #print("No of 32 Bit - ",no32Bit)
        #print("Registrers 16 Bit -",registers16Bit)
        #print("Registrers 32 Bit -",registers32Bit)
        DataString = ''
        ip_address=ip_address.replace('\n','')
        #print(ip_address)
        if(protocol == 'tcp'):
            client = ModbusClient(ip_address, port=port)
        elif(protocol == 'serial'):
            client = ModbusSerialClient(method = 'rtu', port = port, baudrate = 9600, timeout = 2, parity = 'N')        
        conn = client.connect()
        print("Connection status:")
        print(conn)

        
        if(conn):
        
            # For Read Holding Register
            print(function)
            if(function == '03'):
                #print("Inside Holding Register")
                if(no16Bit):
                    #Register Address as an argument
                    for count16 in range(0,no16Bit):
                        x = client.read_holding_registers(registers16Bit[count16],1,unit = slaveId, timeout=1)
                        
                        time.sleep(POLL_RATE)
                        
                        #print(x)
                        if(x.isError()):
                            print("Error")
                            return ''
                        
                        y=str(x.getRegister(0))
                        DataString = DataString + y + ','
                        #print("Data: ",DataString)
                    #print("Data 16 Bit: ",DataString)

                if(no32Bit):
                    #Register Address as an argument
                    for count32 in range(0,no32Bit):
                        x = client.read_holding_registers(registers32Bit[count32],2,unit = slaveId, timeout=1)
                        
                        time.sleep(POLL_RATE)
                        
                        if(x.isError()):
                            print("Error")
                            return ''                        
                        y=str(x.getRegister(0))
                        DataString = DataString + y + ','
                        y=str(x.getRegister(1))
                        DataString = DataString + y + ','
                    #print("Data 32 Bit: ",DataString)
            
            # For Read Input Register
            if(function == '04'):
                if(no16Bit):
                    #Register Address as an argument
                    for count16 in range(0,no16Bit):
                        x = client.read_input_registers(registers16Bit[count16],1,unit = slaveId)
                        
                        time.sleep(POLL_RATE)

                        if(x.isError()):
                            print("Error")
                            return ''                        
                        y=str(x.getRegister(0)) 
                        DataString = DataString + y + ','

                if(no32Bit):
                    #Register Address as an argument
                    for count32 in range(0,no32Bit):
                        x = client.read_input_registers(registers32Bit[count32],2,unit = slaveId)

                        time.sleep(POLL_RATE)

                        if(x.isError()):
                            print("Error")
                            return ''                        
                        y=str(x.getRegister(0))
                        DataString = DataString + y + ','
                        y=str(x.getRegister(1)) 
                        DataString = DataString + y + ',' 

            #print("Final String: ",DataString)
        else:
            #If there is no connection Established
            print("No connection")
            DataString = ','
        client.close()
            
        return DataString[:-1]

    except Exception as e:
        #print(e)
        errlogger.error(e)


#--------------Functions required for DGSyncing and ZeroExport------------------#

def RegisterReadValue(regNo, noOfRegister, slaveID, regType):
    regVal = None
    try:
##        client = ModbusClient(ip_address, port=port)
        client = ModbusSerialClient(method = 'rtu', port = '/dev/usb2485', baudrate = 9600, timeout = 2, parity = 'N')
        conn = client.connect()
        print("Client Connection = {} ".format(conn))
        if(conn):
            if(regType == 'u16'):
                if(noOfRegister == 1):
                    print("Reading register {}".format(regNo))
                    x = client.read_holding_registers(regNo,1,unit = slaveID, timeout=1)
                    if(x.isError()):
                        print("Error in reading Register")
                        regVal = None
                    else:
                        value = x.getRegister(0)
                        print("Register Value = {}".format(value))
                        regVal = value
                    
                elif(noOfRegister == 2):
                    finalValue = []
                    print("Reading register {}".format(regNo))
##                    for regCount in range(0,noOfRegister):
                    x = client.read_holding_registers(regNo,2,unit = slaveID, timeout=1)
                    if(x.isError()):
                        print("Error in reading Register")
                        regVal = None
                    else:
                        finalValue.append(x.getRegister(0))
                        finalValue.append(x.getRegister(1))
                        print("Register Value = {}".format(finalValue))
                        regVal = finalValue[0]<<16 | finalValue[1]
                    
            elif(regType == 'float32'):
##                if(noOfRegister == 1):
##                    print("Reading register {}".format(regNo))
##                    x = client.read_holding_registers(regNo,1,unit = slaveID, timeout=1)
##                    if(x.isError()):
##                        print("Error in reading Register")
##                        value = ''
##                    else:
##                        value = x.getRegister(0)
##                        print("Register Value = {}".format(value))
##                    regVal = value
                    
                noOfRegister = 2
                finalValue = []
                print("Reading register {}".format(regNo))
##                for regCount in range(0,noOfRegister):
                x = client.read_holding_registers(regNo,2,unit = slaveID, timeout=1)
                if(x.isError()):
                    print("Error in reading Register")
                    regVal = None
                else:
                    finalValue.append(x.getRegister(0))
                    finalValue.append(x.getRegister(1))
                    print("Register Value = {}".format(finalValue))
                    temp = numpy.array([finalValue[0],finalValue[1]],numpy.uint16)
                    temp.dtype = numpy.float32
            
                    regVal = float(temp[0])
        print("Register Value = ",regVal)
        client.close()
        return regVal
    except Exception as errRead:
        print(errRead)
        return regVal

def RegisterReadDGValue(regNo, noOfRegister, slaveID):
    regVal = None
    try:
##        client = ModbusClient(ip_address, port=port)
        client = ModbusSerialClient(method = 'rtu', port = '/dev/usb2485', baudrate = 9600, timeout = 2, parity = 'N')
        conn = client.connect()
        print("Client Connection = {} ".format(conn))
        if(conn):
            finalValue = []
            print("Reading register {}".format(regNo))
            x = client.read_holding_registers(regNo,2,unit = slaveID, timeout=1)
            if(x.isError()):
                print("Error in reading Register")
                regVal = None
            else:
                finalValue.append(x.getRegister(0))
                finalValue.append(x.getRegister(1))
                print("Register Values = {}".format(finalValue))
                temp = numpy.array([finalValue[0],finalValue[1]],numpy.uint16)
                temp.dtype = numpy.float32
                
                regVal = float(temp[0])
                         
        print("Register Value = ", regVal)
        client.close()
        return regVal
    except Exception as errRead:
        print(errRead)
        return regVal

def Load(capacity):
    result = round(random.uniform(5,30),2)
    return result

def RegisterWriteValue(regNo, noOfRegister, value, slaveID, regType):
    regVal = False
    try:
        print(value)
        print("Writing register {}".format(regNo))
        client = ModbusSerialClient(method = 'rtu', port = '/dev/usb2485', baudrate = 9600, timeout = 2, parity = 'N')
        conn = client.connect()
        if(conn):
            if(regType == 'u16'):
                rq = client.write_register(regNo, value, unit = slaveID)
                time.sleep(0.5)
                rr = client.read_holding_registers(regNo, 1, unit = slaveID)
                print(rr.registers)
                try:
                    assert(rq.function_code < 0x80)
                    assert(rr.registers[0] == value)
                    print("successwrite")
                    regVal = True
                except AssertionError:
                    print("Data not able to write")
                    regVal = False
                    
            elif(regType == 'float32'):
                print("float 32 type register")
                temp = numpy.array([value],numpy.float32)
                temp.dtype = numpy.uint16
                u16Value = [temp[0],temp[1]]
                print("uint16 value = ", u16Value)
                rq = client.write_registers(regNo, u16Value, unit = slaveID)
                time.sleep(0.5)
                rr = client.read_holding_registers(regNo, 2, unit = slaveID)
                print(rr.registers)
                try:
                    assert(rq.function_code < 0x80)
                    assert(rr.registers == u16Value)
                    print("successwrite")
                    regVal = True
                except AssertionError:
                    print("Data not able to write")
                    regVal = False
        client.close()  
        return regVal
    except Exception as errRead:
        print("Error writing value")
        print(errRead)
        return regVal

def EmgShutDownSolar(process):
    try:
        print("Emergency Shutdown Solar.....")
        if(process == 'dgsync'):      
            for invCount in range(0,noOfInverter):
                regNo = int(Inverters[invCount]["registerPowerLimit"])
                noOfRegister = 1
                slaveID = int(Inverters[invCount]["slaveId"])
                regType = Inverters[invCount]["registerType"]
                Load = RegisterReadValue(regNo, noOfRegister, slaveID, regType)
                Load = Load / Inverters[invCount]["scalePowerLimit"]
                InvrPower[invCount] = Load
                if not(Load == 0):
                    Load = 0
                    RegisterWriteValue(regNo, noOfRegister, Load,slaveID, regType)
        if(process == '0export'):      
            for invCount in range(0,noOfInverter0):
                regNo = int(Inverters0[invCount]["registerPowerLimit"])
                noOfRegister = 1
                slaveID = int(Inverters0[invCount]["slaveId"])
                regType = Inverters0[invCount]["registerType"]
                Load = RegisterReadValue(regNo, noOfRegister, slaveID, regType)
                Load = Load / Inverters0[invCount]["scalePowerLimit"]
                InvrPower0[invCount] = Load
                if not(Load == 0):
                    Load = 0
                    RegisterWriteValue(regNo, noOfRegister, Load,slaveID, regType)
    except Exception as emgErr:
        print(emgErr)
        print("Error in EmgShutdownSolar function")
            

def DecreaseSolarGen(delta,process):
    try:
        print("Reducing Solar Generation......")
        print("Delta = ",delta)
        print("Process = ",process)
        TotalSolarCapacity = 0
        if(process=='dgsync'):
            for i in range(0, noOfInverter):
                TotalSolarCapacity = TotalSolarCapacity + Inverters[i]["inverterCapacity"]
            for j in range(0, noOfInverter):
                shareLoad = float((delta*100)/TotalSolarCapacity)
                noOfReg = 1
                regAddress = int(Inverters[j]["registerPowerLimit"])
                regType = Inverters[j]["registerType"]
                Load = RegisterReadValue(regAddress, noOfReg, Inverters[j]["slaveId"], regType)
                Load = Load / Inverters[j]["scalePowerLimit"]
                if not(Load == None):
                    InvrPower[j] = Load
                    Load = Load - shareLoad

                    if(Load > 0 and Load <= 100):
                        Load = Load * Inverters[j]["scalePowerLimit"]
                        if(regType == 'u16'):
                            Load = int(Load)
                        elif(regType == 'float32'):
                            Load = float(Load)
                        print("Load = ",Load)
                        RegisterWriteValue(regAddress, noOfReg, Load,Inverters[j]["slaveId"], regType)
                else:
                    print("read value is None Type")
        elif(process == '0export'):
            for i in range(0, noOfInverter0):
                TotalSolarCapacity = TotalSolarCapacity + Inverters0[i]["inverterCapacity"]
            for j in range(0, noOfInverter0):
                shareLoad = float((delta*100)/TotalSolarCapacity)
                noOfReg = 1
                regAddress = int(Inverters0[j]["registerPowerLimit"])
                regType = Inverters0[j]["registerType"]
                Load = RegisterReadValue(regAddress, noOfReg, Inverters0[j]["slaveId"], regType)
                Load = Load / Inverters0[j]["scalePowerLimit"]
                if not(Load == None):
                    InvrPower0[j] = Load
                    Load = Load - shareLoad

                    if(Load > 0 and Load <= 100):
                        Load = Load * Inverters0[j]["scalePowerLimit"]
                        if(regType == 'u16'):
                            Load = int(Load)
                        elif(regType == 'float32'):
                            Load = float(Load)
                        print("Load = ",Load)
                        RegisterWriteValue(regAddress, noOfReg, Load,Inverters0[j]["slaveId"], regType)
                else:
                    print("read value is None Type")
    except Exception as errDcr:
        print(errDcr)
        print("Error in DecreaseSolarGen function")

def IncreaseSolarGen(delta,process):
    print("Increasing Solar Generation......")
    print("Delta: {}".format(delta))
    print("Process = ",process)
    try:
        TotalSolarCapacity = 0
        if(process == 'dgsync'):
            for i in range(0, noOfInverter):
                TotalSolarCapacity = TotalSolarCapacity + Inverters[i]["inverterCapacity"]
            for j in range(0, noOfInverter):
                shareLoad = float((delta * 100)/TotalSolarCapacity)
                noOfReg = 1
                regAddress = int(Inverters[j]["registerPowerLimit"])
                regType = Inverters[j]["registerType"]
                Load = RegisterReadValue(regAddress, noOfReg, Inverters[j]["slaveId"], regType)
                Load = Load / Inverters[j]["scalePowerLimit"]
                if not(Load == None):
                    InvrPower[j] = Load
                    print("ShareLoad {}".format(shareLoad))
                    Load = Load + shareLoad

                    if(Load > 100):
                        Load = 100
                    if(Load <= 100):
                        Load = Load * Inverters[j]["scalePowerLimit"]
                        
                        if(regType == 'u16'):
                            Load = int(Load)
                        elif(regType == 'float32'):
                            Load = float(Load)
                        print("Load = ",Load)
                        RegisterWriteValue(regAddress, noOfReg,Load, Inverters[j]["slaveId"], regType)
                    else:
                        print("do nothing")
                else:
                    print("Read Value is None")

        elif(process=='0export'):
            for i in range(0, noOfInverter0):
                TotalSolarCapacity = TotalSolarCapacity + Inverters0[i]["inverterCapacity"]
            for j in range(0, noOfInverter0):
                shareLoad = float((delta * 100)/TotalSolarCapacity)
                noOfReg = 1
                regAddress = int(Inverters0[j]["registerPowerLimit"])
                regType = Inverters0[j]["registerType"]
                Load = RegisterReadValue(regAddress, noOfReg, Inverters0[j]["slaveId"], regType)
                Load = Load / Inverters0[j]["scalePowerLimit"]
                if not(Load == None):
                    InvrPower0[j] = Load
                    print("ShareLoad {}".format(shareLoad))
                    Load = Load + shareLoad

                    if(Load > 100):
                        Load = 100
                    if(Load <= 100):
                        Load = Load * Inverters0[j]["scalePowerLimit"]
                        
                        if(regType == 'u16'):
                            Load = int(Load)
                        elif(regType == 'float32'):
                            Load = float(Load)
                        print("Load = ",Load)
                        RegisterWriteValue(regAddress, noOfReg,Load, Inverters0[j]["slaveId"], regType)
                    else:
                        print("do nothing")
                else:
                    print("Read Value is None")
    except Exception as errI:
        print(errI)
        print("Error in function Increase Solar Gen")


    
def setSloarMinLoad(process):
    print("Setting Solar to Minimum Load........")
    try:
        if(process == 'dgsync'):
            for inv in range(0,noOfInverter):
                slaveID = Inverters[inv]["slaveId"]
                inverterCapacity = Inverters[inv]["inverterCapacity"]
                registerPowerEnable = Inverters[inv]["registerPowerEnable"]
                registerPowerLimit = Inverters[inv]["registerPowerLimit"]
                enableValue = int(Inverters[inv]["enableValue"])
                disableValue = Inverters[inv]["disableValue"]

                print("slaveID = {}\n inVerterCapacity = {}\n registerPowerEnable = {}\n EnableValue = {}\n Disable Value = {}\n"
                      .format(slaveID,inverterCapacity,registerPowerEnable,enableValue,disableValue))
                
                regType = Inverters[inv]["registerType"]
                lastTime = time.time()
                for TimeDiff in range(0,5):
                    value = RegisterReadValue(registerPowerEnable,1,slaveID,'u16')
                    print("Read Value : ",value)
                    if not(value == None):
                        break
                    TimeDiff = time.time() - lastTime
    ##            if(value == None):
                    
                InvrPower[inv] = 10
                writeValue = Inverters[inv]["inverterCapacity"]*0.1 * Inverters[inv]["scalePowerLimit"]
                
                if(regType == 'u16'):
                    noOfReg = 1
                    writeValue = int(writeValue)
                elif(regType == 'float32'):
                    noOfReg = 2
                    writeValue = float(writeValue)
                    
                setDynamic = RegisterWriteValue(registerPowerEnable, 1,enableValue, Inverters[inv]["slaveId"], 'u16')    
                setMinLoad = RegisterWriteValue(registerPowerLimit, noOfReg,writeValue, Inverters[inv]["slaveId"], regType)
                

                if(setMinLoad):
                    print("Succesfully set Solar MinLoad")
                if(setDynamic):
                    print("Successfully Set Power Enable")

        elif(process == '0export'):
            for inv in range(0,noOfInverter0):
                slaveID = Inverters0[inv]["slaveId"]
                inverterCapacity = Inverters0[inv]["inverterCapacity"]
                registerPowerEnable = Inverters0[inv]["registerPowerEnable"]
                registerPowerLimit = Inverters0[inv]["registerPowerLimit"]
                enableValue = Inverters0[inv]["enableValue"]
                disableValue = Inverters0[inv]["disableValue"]

                print("slaveID = {}\n inVerterCapacity = {}\n registerPowerEnable = {}\n EnableValue = {}\n Disable Value = {}\n"
                      .format(slaveID,inverterCapacity,registerPowerEnable,enableValue,disableValue))
                
                regType = Inverters0[inv]["registerType"]
                lastTime = time.time()
                for TimeDiff in range(0,5):
                    value = RegisterReadValue(registerPowerEnable,1,slaveID,'u16')
                    print("Read Value : ",value)
                    if not(value == None):
                        break
                    TimeDiff = time.time() - lastTime
    ##            if(value == None):
                    
                InvrPower0[inv] = 10
                writeValue = Inverters0[inv]["inverterCapacity"]*0.1 * Inverters0[inv]["scalePowerLimit"]
                
                if(regType == 'u16'):
                    noOfReg = 1
                    writeValue = int(writeValue)
                elif(regType == 'float32'):
                    noOfReg = 2
                    writeValue = float(writeValue)
                    
                setDynamic = RegisterWriteValue(registerPowerEnable, noOfReg,10, Inverters0[inv]["slaveId"], regType)    
                setMinLoad = RegisterWriteValue(registerPowerLimit, noOfReg,writeValue, Inverters0[inv]["slaveId"], regType)
                

                if(setMinLoad):
                    print("Succesfully set Solar MinLoad")
                if(setDynamic):
                    print("Successfully Set Power Enable")            
    except Exception as errS:
        print(errS)
        print("Error in function Set Solar Min Load")

    
def ProcessDGSync(DGArray):
    try:
        print("Processing DG Sync..........")
        process = 'dgsync'
        safeLoadMinPer = float(plantProfile["safeLoadMinLimit"])
        safeLoadMaxPer = float(plantProfile["safeLoadMaxLimit"])
        criticalLoadPer = float(plantProfile["criticalLoadLimit"])
        print("Plant  Profile Parameter:-  ")
        print("SafeLoad Min Percentage: {} \n SafeLoad Max Percentage: {} \n Critical Load Percentage: {}"
              .format(safeLoadMinPer,
                      safeLoadMaxPer,
                      criticalLoadPer))
        
        TotalDGCapacity = 0
        for i in range(0,noOfDG):
            if(DGArray[i] == 1):
                TotalDGCapacity = TotalDGCapacity + float(DGs[i]["capacity"])
                print("DG Number {} Capacity = ".format(i,float(DGs[i]["capacity"])))
                
        print("Total DG Capacity = {}".format(TotalDGCapacity))
        dgLoadValue = 0
        for DGNumber in range(0,noOfDG):
            if(DGArray[DGNumber] == 1):
                dgLoadAddress = int(DGs[DGNumber]["registerActivePower"])
                slaveID = int(DGs[DGNumber]["slaveID"])
        
                print("DG Number {} profile: ".format(DGNumber))
                print("DG Load Address = {} \n SlaveID = {}".format(dgLoadAddress,slaveID))
     
                safeLoadMinValue = round(float((TotalDGCapacity) * (safeLoadMinPer/100)),2)
                safeLoadMaxValue = round(float((TotalDGCapacity) * (safeLoadMaxPer/100)),2)
                criticalLoadValue = round(float((TotalDGCapacity) * (criticalLoadPer/100)),2)

                print("SafeLoadMinValue: {} \t SafeLoadMaxValue: {} \t CriticalLoadValue {}"
                      .format(safeLoadMinValue,
                              safeLoadMaxValue,
                              criticalLoadValue))
                      #below line to be uncommented for real values
##                dgLoadValue = dgLoadValue + round(float(RegisterReadDGValue(dgLoadAddress,2,slaveID)),2)
                      
        dgLoadValue = Load(TotalDGCapacity) # Random Value for testing. To be  commented for real values
        DGLoad[0] = dgLoadValue
        print("DGLoadValue= {}".format(dgLoadValue))
        if(dgLoadValue <= criticalLoadValue):
            print("DG Load is Critical !!")
            EmgShutDownSolar(process)
        elif(dgLoadValue < safeLoadMinValue):
            print("DG Load is below Safe Load Minimum Value !!")
            Delta = safeLoadMinValue - dgLoadValue
            DecreaseSolarGen(Delta,process)
        elif(dgLoadValue > safeLoadMaxValue):
            print("DG Load is greater than Safe Load Maximum Value !!")
            Delta = dgLoadValue - safeLoadMaxValue 
            IncreaseSolarGen(Delta,process)
        else:
            print("DG Load is in Range. No Action Necessary")
    except Exception as errProcessSync:
        print("Error in function Process DGSync")
        print(errProcessSync)


def Process0Export(GridArray):
    try:
        process = '0export'
        print("Processing Zero Export..........")
        safeLoadMinPer = float(plantProfile0export["safeLoadMinLimit"])
        safeLoadMaxPer = float(plantProfile0export["safeLoadMaxLimit"])
        criticalLoadPer = float(plantProfile0export["criticalLoadLimit"])
        print("Plant  Profile Parameter:-  ")
        print("SafeLoad Min Percentage: {} \n SafeLoad Max Percentage: {} \n Critical Load Percentage: {}"
              .format(safeLoadMinPer,
                      safeLoadMaxPer,
                      criticalLoadPer))
        
        TotalGridCapacity = 0
        for i in range(0,noOfGrid):
            if(GridArray[i] == 1):
                TotalGridCapacity = TotalGridCapacity + float(Grids[i]["sanctionLoad"])
                print("Grid Number {} Capacity = ".format(i,float(Grids[i]["sanctionLoad"])))
                
        print("Total Grid Capacity = {}".format(TotalGridCapacity))
        GridLoadValue = 0
        for GridNumber in range(0,noOfGrid):
            if(GridArray[GridNumber] == 1):
                GridLoadAddress = int(Grids[GridNumber]["registerActivePower"])
                slaveID = int(Grids[GridNumber]["slaveID"])
        
                print("Grid Number {} profile: ".format(GridNumber))
                print("Grid Load Address = {} \n SlaveID = {}".format(GridLoadAddress,slaveID))
     
                safeLoadMinValue = round(float((TotalGridCapacity) * (safeLoadMinPer/100)),2)
                safeLoadMaxValue = round(float((TotalGridCapacity) * (safeLoadMaxPer/100)),2)
                criticalLoadValue = round(float((TotalGridCapacity) * (criticalLoadPer/100)),2)

                print("SafeLoadMinValue: {} \t SafeLoadMaxValue: {} \t CriticalLoadValue {}"
                      .format(safeLoadMinValue,
                              safeLoadMaxValue,
                              criticalLoadValue))
                      #below line to be uncommented for real values
##                GridLoadValue = GridLoadValue + round(float(RegisterReadDGValue(GridLoadAddress,2,slaveID)),2)
                      
        GridLoadValue = Load(TotalGridCapacity) # Random Value for testing. To be  commented for real values
        GridLoad[0] = GridLoadValue
        print("GridLoadValue= {}".format(GridLoadValue))
        if(GridLoadValue <= criticalLoadValue):
            print("Grid Load is Critical !!")
            EmgShutDownSolar(process)
        elif(GridLoadValue < safeLoadMinValue):
            print("Grid Load is below Safe Load Minimum Value !!")
            Delta = safeLoadMinValue - GridLoadValue
            DecreaseSolarGen(Delta,process)
        elif(GridLoadValue > safeLoadMaxValue):
            print("Grid Load is greater than Safe Load Maximum Value !!")
            Delta = GridLoadValue - safeLoadMaxValue 
            IncreaseSolarGen(Delta,process)
        else:
            print("Grid Load is in Range. No Action Necessary")
    except Exception as errZeroExport:
        print("Error in function Process ZeroExport")
        print(errZeroExport)

        
#--------------------------End of Functions in DGSync and ZeroExport------------------------------------#
            




def main(LoggerProfile, DeviceProfile):
    try:
        print("Processing RMS.........")
        
        deviceCount = len(DeviceProfile)
        i = 0
        
        while(i < deviceCount):
            #print("IP Address- ",DeviceProfile.get(i)[0][8])
            print("Reading Devices")
            if(str(DeviceProfile.get(i)[0][1]) == '101'):
                Device_Data=readWMS()
            if(str(DeviceProfile.get(i)[0][1]) == '151'):
                dgStatus = ''
                dgLoad = ''
                Invdata = ''
                
                for cntDg in range(0,noOfDG):
                    dgStatus = dgStatus + str(DGStatus[cntDg]) + ','
                    dgLoad  = dgLoad + str(DGLoad[cntDg]) + ','
                for cntInv in range(0,noOfInverter):
                    Invdata = Invdata + str(InvrPower[cntInv]) + ','
                Device_Data = dgStatus + dgLoad + Invdata
                
            elif(str(DeviceProfile.get(i)[0][1]) == '155'):
                gridStatus = ''
                gridLoad = ''
                Invdata = ''
                
                for cntgrid in range(0,noOfGrid):
                    gridStatus = gridStatus + str(GridStatus[cntgrid]) + ','
                    gridLoad  = gridLoad + str(GridLoad[cntgrid]) + ','
                for cntInv in range(0,noOfInverter0):
                    Invdata = Invdata + str(InvrPower0[cntInv]) + ','
                Device_Data = gridStatus + gridLoad + Invdata 
            else:
                #read data from the slave device as per the device profile
                Device_Data = get_Data(DeviceProfile.get(i)[0][2], DeviceProfile.get(i)[0][3], DeviceProfile.get(i)[0][4], DeviceProfile.get(i)[0][5], DeviceProfile.get(i)[0][6], DeviceProfile.get(i)[0][7], DeviceProfile.get(i)[0][8], DeviceProfile.get(i)[0][9], DeviceProfile.get(i)[0][10])
            #print(Device_Data)
            #print("Length of device data ",len(Device_Data))
            time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            #print(time_stamp)
            #print(str(LoggerProfile[1]))
            #print(str(LoggerProfile[2]))
            #print(DeviceProfile.get(i)[0][1])
            #print(str(DeviceProfile.get(i)[0][0]))
            buffer_data = str(LoggerProfile[1]) + ',' + str(LoggerProfile[2]) + ',' + str(DeviceProfile.get(i)[0][1]) + ',' + str(DeviceProfile.get(i)[0][0]) + ','
            #print(buffer_data)
            if(len(Device_Data) > 0):
                print("correct")
                buffer_data = buffer_data + '0' + ',' + time_stamp + ',' + Device_Data + '\n'
            else:
                print("Incorrect")
                buffer_data = buffer_data + '1' + ',' + time_stamp + '\n'
            print("Buffer_Data ", buffer_data)
            with open('../records/records_csv.csv','a') as file:
                file.write(buffer_data)  
            i = i + 1

            #client.close()
            time.sleep(SCAN_RATE)
            
    except Exception as e:
        errlogger.error(e)


if __name__=="__main__":
    try:    
        #client=ModbusClient('192.168.0.104')
        #print(client.connect())
        LoggerProfileReturn = loggerProfileFunction()
        print("Logger Profile: ",LoggerProfileReturn)
        DeviceProfileReturn = deviceProfileFunction(LoggerProfileReturn[0])
        print("Device Profile " ,DeviceProfileReturn)
        #Run First Time
        if(LoggerProfileReturn[8] == '1'):
            main(LoggerProfileReturn, DeviceProfileReturn)
        lasttime = time.time()
        while True:

            if(LoggerProfileReturn[6] == '1'):
                print("Checking DG Sync............")
                try:
                    for CountDG in range(0,noOfDG):
                        PinDG = int(DGs[CountDG]["PIN"])
                        print("PIN DG: {}".format(PinDG))
                        stateDG[CountDG] = GPIO.input(PinDG)
                        print("GPIO State:")
                        print(stateDG[CountDG])
                        #lastDGState[CountDG] = True
                        print("Current Status of DG {}".format(stateDG[CountDG]))
                        if(stateDG[CountDG] == False):
                            DGStatus[CountDG] = 0

                        if((stateDG[CountDG] == False) and (lastDGState[CountDG] == True)):
                            flagMinLoad = 1
                        if((stateDG[CountDG] == False) and (lastDGState[CountDG] == False)):
                            flagRunDG[CountDG] = 1
                ##            ProcessDGSync(CountDG)
                        else:
                            print("Run Solar Normally")
                            flagRunDG[CountDG] = 0
                        lastDGState[CountDG] = stateDG[CountDG]
                    
                ##    time.sleep(5)
                    if(flagRunDG[0] ==1 or flagRunDG[1] ==1 or flagRunDG[2] ==1 ):
                        IsSyncing = True
                        if(flagMinLoad == 1 and StatusSolarMinLoad ==0):
                            setSloarMinLoad('dgsync')
                            StatusSolarMinLoad = 1        
                        #setSloarMinLoad()
                        ProcessDGSync(flagRunDG)
                except Exception as errCheck1:
                    print(errCheck1)


            if(LoggerProfileReturn[7] == '1'):
                print("Checking Zero Export")
                
                try:
                    for CountGrid in range(0,noOfGrid):
                        PinGrid = int(Grids[CountGrid]["PIN"])
                        print("PIN Grid: {}".format(PinGrid))
                        stateGrid[CountGrid] = GPIO.input(PinGrid)
                        print("GPIO State:")
                        print(stateGrid[CountGrid])
                        #lastGridState[CountGrid] = True
                        print("Current Status of Grid {}".format(stateGrid[CountGrid]))
                        if(stateGrid[CountGrid] == False):
                            GridStatus[CountGrid] = 0

                        if((stateGrid[CountGrid] == False) and (lastGridState[CountGrid] == True)):
                            flagMinLoad = 1
                        if((stateGrid[CountGrid] == False) and (lastGridState[CountGrid] == False)):
                            flagRunGrid[CountGrid] = 1
                ##            ProcessGridSync(CountGrid)
                        else:
                            print("Run Solar Normally")
                            flagRunGrid[CountGrid] = 0
                        lastGridState[CountGrid] = stateGrid[CountGrid]

                    if(flagRunGrid[0] ==1 or flagRunGrid[1] ==1 or flagRunGrid[2] ==1 ):
                        IsZeroExport = True
                        if(flagMinLoad == 1 and StatusSolarMinLoad ==0):
                            setSloarMinLoad('0export')
                            StatusSolarMinLoad = 1        
                        #setSloarMinLoad()
                        Process0Export(flagRunGrid)
                        
                ##    elif(flagRunDG[0] ==0 and flagRunDG[1] ==0 and flagRunDG[2] ==0):
                ##        StatusSolarMinLoad = 0
                ##        flagMinLoad = 0
                except Exception as errCheck2:
                    print(errCheck2)

            if(LoggerProfileReturn[8] == '1'):                
                if((time.time() - lasttime) > LoggerProfileReturn[3]):
    ##                lasttime = time.time()
                    main(LoggerProfileReturn, DeviceProfileReturn)
                    lasttime = time.time()
            
    except Exception as e:
        errlogger.error(e)
