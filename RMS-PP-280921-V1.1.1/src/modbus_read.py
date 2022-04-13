import numpy
import RPi.GPIO as GPIO
import pymodbus
from pymodbus.client.sync import ModbusTcpClient 
from pymodbus.client.sync import ModbusSerialClient 
import time
import logging
from subprocess import call
from subprocess import *
from gpiozero import MCP3208
import configparser
from ast import literal_eval

import sys
import random
import math
import warnings
import socket
import requests
import urllib.request
import os
from datetime import datetime
warnings.simplefilter('ignore')

#default modbus setting
baudRate = 9600
timeout =0.25   #(in sec)
pollRate = 0.25   # this is the timein seconds between two packets
parity = 'N'

TIME_URL='http://www.holmiumtechnologies.com/rms/api/timestamp/sync'
DATA_URL='http://13.234.86.197/phpApi/rms/api/timestamp/sync?'
SERVER_URL='http://www.holmiumtechnologies.com'
#---------------parameters to check Last upload row file in Idle state or active state -----------------------------#

fileIdleCount=0     #for counting when file read is in idle state
timeCheckIdle = time.time()
LastUploadRowPre =1 #for counting when file read is in idle state
timeCheckIdle = time.time()  #for checking file idle at definite time interval of 5 mon or 300 sec.
#-----------------------------------------------------------------------------------------------------------------------#
try:    
    workingDir=os.getcwd()
    print(workingDir)
    parentDir=os.path.dirname(workingDir)
    #os.chdir(parentDir)
    print(parentDir)
except:
    print("Error in setting parent directory")


#-----Error Flag-----#
flagError=True



#----GPIO Initialization---#

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#------Config File parameter check------#
errConfigFile = False
countConfig = 0               #this count is used to count the failures in configuration file
today   = datetime.today()
year    = str(today.year)
month   = str(today.month)
day     = str(today.day)
hour    = str(today.hour)


def setLogFormat():
    try:
        print("\n*_*_*_checking year date month log format _*_*_* ")
        today   = datetime.today()
        year    = str(today.year)
        month   = str(today.month)
        day     = str(today.day)
        hour    = str(today.hour)
        now     = datetime.now()

        timestamp = now.strftime("%d/%m/%Y")
        dayFilePath=parentDir+'/logs/modbus_read/'+year+'/'+month+'/'+day+'.txt'
        print(dayFilePath)

        try:
            fileExist=os.path.exists(dayFilePath)
            if (not(fileExist)):
                print("making year and month directory")
                path=parentDir+'/logs/modbus_read/'
                os.chdir(path)
                path=path+year+'/'
                if(os.path.isdir(path)):
                    print("year foder available")
                    os.chdir(path)
                    path=path+month+'/'
                    if(os.path.isdir(path)):
                        print("Month folder available")
                        os.chdir(path)
                        if(open(dayFilePath,'xt')):
                            print("file create successful at location",dayFilePath)
                    else:
                        os.mkdir(path)
                        os.chdir(path)
                        #create the file here
                        if(open(dayFilePath,'xt')):
                            print("File created successful at location:",dayFilePath)
                else:
                    os.mkdir(year)
                    os.chdir(path)
                    os.mkdir(month)
                    os.chdir(month)
                    if(open(dayFilePath,'xt')):
                        print("File created successful at location:",dayFilePath)
            else:
                print("file exist")
               
        except Exception as e:            
            print(e)
            
            
    except Exception as e:
        print(e)
        


try:
    setLogFormat()
    path = parentDir+'/logs/modbus_read/'+year+'/'+month+'/'+day+'.txt'
    logging.basicConfig(filename = path,format='%(asctime)s --%(levelname)s--Line: %(lineno)s--%(message)s', filemode = 'a')
    errlogger = logging.getLogger()
    errlogger.setLevel(logging.INFO)
    errlogger.info("set configuration for error log successfully")
    print("set configuration for error log successfully")
    
except Exception as e:
    print(e)
    for i in range(0,4):
        time.sleep(5)
        try:
            if os.execl(sys.executable, sys.executable, *sys.argv):
                break
            else:
                print("retrying again...")
                os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
           print(e)


def setRecordFormat():  
    try:
        print("\n*_*_*_checking year date month hour format _*_*_* ")
        errlogger.info("checking year month hour format")
        
        today   = datetime.today()
        year    = str(today.year)
        month   = str(today.month)
        day     = str(today.day)
        hour    = str(today.hour)
        hourFilePath=parentDir+'/records/'+year+'/'+month+'/'+day+'/'+hour+'.csv'
        print(hourFilePath)

        try:
            fileExist=os.path.exists(hourFilePath)
            if (not(fileExist)):
                print("making year and month directory")
                path=parentDir+'/records/'
                os.chdir(path)
                path=path+year+'/'
                if(os.path.isdir(path)):
                    print("year foder available")
                    os.chdir(path)
                    path=path+month+'/'
                    if(os.path.isdir(path)):
                        print("Month folder available")
                        os.chdir(path)
                        path=path+day+'/'
                        if(os.path.isdir(path)):
                            print(" Day folder available")
                            os.chdir(path)
                            path=path+hour+'/'
                            
                            if(open(hourFilePath,'xt')):
                                print("file create successful at location",hourFilePath)
                        else:
                            print("day folder not available")
                            os.mkdir(path)
                            os.chdir(path)
                            os.mkdir(day)
                            path = path + day+'/'
                            os.chdir(path)
                            #create the file here
                            if(open(hourFilePath,'xt')):
                                print("File created successful at location:",hourFilePath)
                            
                    else:
                        print("month folder not available")
                        os.mkdir(path)
                        os.chdir(path)
                        #create the file here
                        if(open(hourFilePath,'xt')):
                            print("File created successful at location:",hourFilePath)
                else:
                    print("year folder not avilable")
                    os.mkdir(year)
                    os.chdir(path)
                    os.mkdir(month)
                    path = path +month+'/'
                    os.chdir(path)
                    os.mkdir(day)
                    path = path + day+'/'
                    os.chdir(path)
                    if(open(hourFilePath,'xt')):
                        print("File created successful at location:",hourFilePath)
            else:
                print("file exist")
               
        except Exception as e:            
            print("Error in setRecordFormat function",e)
            errlogger.error(e)
            
    except Exception as e:
        print("set Record format error : ",e)
        errlogger.error("setRecordFormat error %s",e)
        

def updateData(buffer_data):
    try:    
        #print("\nentered in update data")
        today   = datetime.today()
        year    = str(today.year)
        month   = str(today.month)
        day     = str(today.day)
        hour    = str(today.hour)
        dataFilePath=parentDir+'/records/'+year+'/'+month+'/'+day+'/'+hour+'.csv'    
        try:
            if(os.path.exists(dataFilePath)):
                with open(dataFilePath,'at') as file:
                    file.write(buffer_data)
                    print("Data write Successful")
                    print("\n")
                    file.close()
            else:
                setRecordFormat()
                with open(dataFilePath,'at') as file:
                    file.write(buffer_data)
                    print("Data write Successful")
                    print("\n")
                    file.close()
        except Exception as e:
            print("Erro in Data write: ",e)
            errlogger.error("Error in data  write :%s",e)
           
        
    except Exception as e:
        print("update Data error : ",e)
        errlogger.error("updateData function error %s",e)
       




def manufacProfile():
    global countConfig
    try:
        print("\n\t\tEntered in manufacProfile")
        
        errlogger.info("Entered in manufacProfile")
        
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/manufacture.ini')
            if(len(config.sections()) == 0):
                print("manufacture Config File is empty")
                print(call(['cp',parentDir+'/backup/manufacture.ini',parentDir+'/config/manufacture.ini']))
                config.read(parentDir+'/config/manufacture.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.error("path not available : %s",e)
            call(['cp',parentDir+'/backup/manufacture.ini',parentDir+'/config/manufacture.ini'])
            config.read(parentDir+'/config/manufacture.ini')
        global manufacProfile
        manufacProfile = config['manufacture']
        global serialNo
        serialNo=manufacProfile['serialNo']
        global firmwareVersion
        firmwareVersion=manufacProfile['firmwareVersion']
        
        countConfig = 0
        
    except Exception as e:
        print("Error in manufacProfileFunction :",e)
        errlogger.error("Error in manufacProfileFunction : %s",e)
        #global countConfig
        time.sleep(10)
        countConfig=countConfig+1
        
        if countConfig<=5:
            print("countConfig :: ",countConfig)
            manufacProfile()
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
           
        elif countConfig>5 and countConfig<=10:
            print("counConfig is greaer than 5 and less than 11 so restaring code")
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    print(i)
                    time.sleep(2)
                    main()
                except Exception as e:
                    errlogger.error(e)
                    manufacProfile()
    return serialNo, firmwareVersion

def syncTime():
    try:
        global countConfig
        print("Entered in syncTime function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        params=''
        r = requests.get(TIME_URL, headers = headers, params= params,timeout = 10)
        print('Response:',r.text)
        call(["sudo","date","-s",r.text])
        #call(["sudo","date","-s","2021-01-11  06:04:11 "])
        countConfig=0
    except Exception as e:
        print("Error in syncTime function : ",e)
        errlogger.error("Error in syncTime function : %s ",e)
        
        countConfig=countConfig+1
        if countConfig<=5:
            errlogger.info("calling itself %s",countConfig)
            syncTime() 
#function for reading logger.ini file
def loggerProfile():
    global countConfig
    try:
        print("\n\t\t\tEntered in Logger Profile function")
        errlogger.info("Entered in Logger Profile function")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/logger.ini')
            if(len(config.sections()) == 0):
                print("logger Config File is empty")
                call(['cp',parentDir+'/backup/logger.ini',parentDir+'/config/logger.ini'])
                config.read(parentDir+'/config/logger.ini')
        except Exception as e:
            print("path not fount : ",e)
            errlogger.error("path not found : %s",e)
            call(['cp',parentDir+'/backup/logger.ini',parentDir+'/config/logger.ini'])
            config.read(parentDir+'/config/logger.ini')
        global loggerProfile
        loggerProfile = config['loggerProfile']
        #configStatus=loggerProfile['configStatus']
        #print("configStatus=",configStatus)
        global plantId
        plantId=loggerProfile['plantId']
        #print("plantId=",plantId)
        global loggerId
        loggerId=int(loggerProfile['loggerId'])
        #print("loggerId=",loggerId)
        global deviceCount
        deviceCount=int(loggerProfile['deviceCount'])
        #print("deviceCount=",deviceCount)
        global readInterval
        readInterval=int(loggerProfile['readInterval'])
        #print("readInterval=",readInterval)
        
        countConfig = 0
        
    except Exception as e:
        print("Error in loggerProfileFunction :",e)
        errlogger.error("Error in loggerProfileFunction : %s",e)
        #global countConfig
        time.sleep(10)
        countConfig=countConfig+1
        print("countConfig : ",countConfig)
        if countConfig<=5:
            print("calling itself : ",countConfig)
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            loggerProfile()
        elif countConfig>5 and countConfig<=10:
            print("counConfig is greaer than 5 and less than 11 so restaring code")
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    print(i)
                    time.sleep(2)
                    main()
                except Exception as e:
                    errlogger.error(e)
                    loggerProfile()
    return    loggerId, deviceCount, plantId,   readInterval   
#...................................................................................#

#function for reading flag.ini file

def flagProfile():
    try:
        global countConfig
        print("\n\t\tflagProfile  ")
        errlogger.info("Entered in flagProfile function")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/flag.ini')
            if(len(config.sections()) == 0):
                print("flag Config File is empty")
                call(['cp',parentDir+'/backup/flag.ini',parentDir+'/config/flag.ini'])
                config.read(parentDir+'/config/flag.ini')
        except Exception as e:
            print("path not available",e)
            errlogger.error(e)
            call(['cp',parentDir+'/backup/flag.ini',parentRead+'/config/flag.ini'])
            config.read(parentDir+'/config/flag.ini')
            global flagProfile
        flagProfile = config['controlFlag']
        global isActive
        isActive= flagProfile['isActive']
        #print("isActive =",isActive)
        global isRms
        isRms=flagProfile['isRms']
        #print("isRms",isRms)
        global isSdCard
        isSdCard=flagProfile['isSdCard']
        #print("isSDCard =",isSdCard)
        global isDGSync
        isDgSync=flagProfile['isDgSync']
        #print("isDGSync=",isDgSync)
        global isZeroExport
        isZeroExport=flagProfile['isZeroExport']
        #print("isZeroExport=",isZeroExport)

        #dataString=''
        #dataString=dataString+str(isActive)+','+str(isRms)+','+str(isSdCard)+','+str(isDgSync)+','+str(isZeroExport)
        
        countConfig = 0
        
    except Exception as e:
        print("Error in flag read profile",e)
        errlogger.error("Error in flag read profile %s",e)
        
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<5:
            print("countConfig : ",countConfig)
            #errlogger.info("countConfig =%d --calling itself ",countConfig)
            flagProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    main()
                except Exception as e:
                    errlogger.error(e)
                    flagProfile()
    return isActive, isSdCard,  isRms,  isDgSync,   isZeroExport

#function for  reading device.ini file
def deviceProfile():
    try:
        global countConfig  
        print("\n\t\tdevice Profile ")
        errlogger.info("Entered in deviceProfile function")
        config=configparser.ConfigParser()
        #print(len(config.sections()))
        try:
            config.read(parentDir+'/config/device.ini')
            if(len(config.sections())==0):
                print("logger config file is empty")
                call(['cp',parentDir+'/backup/device.ini',parentDir+'/config/device.ini'])
                config.read(parentDir+'/config/device.ini')
        except Exception as e:
            print("path not available :",e)
            errlogger.error("path not available : %s",e)
        global device
        device=config['device']
        global deviceData
        deviceData=[]
        count=0
        global deviceProfileList
        deviceProfileList= {}
        #print(device.keys())
        for deviceNumber in list(device.keys()):
            #print(deviceNo)
            print(literal_eval(device[deviceNumber]))
            #print(literal_eval(device['device1']))
            
            deviceData.append(literal_eval(device[deviceNumber]))
            #print("deviceData =",deviceData)
            #deviceNo=str(device[deviceNo]['deviceNo'])
            #print("deviceNo=",deviceNo)
            global deviceIndex
            deviceIndex=int(deviceData[count]['deviceIndex'])
            global deviceType
            deviceType=int(deviceData[count]['deviceType'])
            global funCode
            funCode=str(deviceData[count]['funCode'])
            global deviceId
            deviceId=str(deviceData[count]['deviceId'])
            global slaveId
            slaveId=int(deviceData[count]['slaveId'])
            global binCount
            binCount=int(deviceData[count]['binCount'])
            
            binStartStr=str(deviceData[count]['binStart'])
            binLengthStr=str(deviceData[count]['binLength'])
            global ipAddress
            ipAddress=str(deviceData[count]['ipAddress'])
            global port
            port=str(deviceData[count]['port'])
            global protocol
            protocol=str(deviceData[count]['protocol'])
            #print("binStartStr -",binStartStr)
            #print("binLengthStr -",binLengthStr)
            global binLength
            binLength = []
            global binStart
            binStart = []
            lengthSplit=binLengthStr.split(',')
            #print(lengthSplit)
            startSplit=binStartStr.split(',')
            #print(startSplit)
            i=0
            
            while(i < binCount):
                
                binStart.append(int(startSplit[i]))
                binLength.append(int(lengthSplit[i]))
                i=i+ 1
            
            #print("binStart=",binStart)
            #print("binLength=",binLength)
            
            deviceProfileList[count] = [(deviceIndex, deviceType, funCode, deviceId, slaveId, binCount, binStart, binLength, ipAddress, port, protocol)]
            
            count=count+1
          
        countConfig = 0
        #print("deviceProfileReturn=",deviceProfileList)
        
    except Exception as e:
        print("error in device profile function:",e)
        errlogger.error("error in device profile function %s",e)
        countConfig = countConfig+1
        time.sleep(10)
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            deviceProfile()
        elif countConfig>5 and countConfig<=10:
            print("counConfig is greaer than 5 and less than 11 so restaring code")
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    main()
                except Exception as e:
                    errlogger.error(e)
                    deviceProfile()   
    return deviceProfileList

def modbusProfile():
    try:
        global countConfig
        global baudRate, parity, pollRate, timeout
        print("\n\t\t modbus Profile ")
        errlogger.info("Entered in modbus Profile")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/modbus.ini')
            if(len(config.sections()) == 0):
                print("manufacture Config File is empty")
                call(['cp',parentDir+'/backup/modbus.ini',parentDir+'/config/modbus.ini'])
                config.read(parentDir+'/config/modbus.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.error("path not available : %s",e)
            call(['cp',parentDir+'/backup/modbus.ini',parentDir+'/config/modbus.ini'])
            config.read(parentDir+'/config/modbus.ini')
        modbusProfile = config['modbus']
        baudRate = int(modbusProfile['baudRate'])
        parityInt = int(modbusProfile['parity'])
        if parityInt==0:
            parity='N'
        elif parityInt==1:
            parity='O'
        elif parityInt==2:
            parity='E'
        else:
            parity = 'N'
        pollRate = int(modbusProfile['pollRate(ms)'])
        timeout = int(modbusProfile['timeout(ms)'])
        timeout = timeout/1000
        pollRate = pollRate/1000
        print("Baud Rate=",baudRate)
        print("TimeOut=",timeout)
        print("Parity =",parity)
        print("pollRate = ",pollRate)
        countConfig = 0
    except Exception as e:
        print("error in device profile function:",e)
        errlogger.error("error in device profile function %s",e)
        countConfig = countConfig+1
        time.sleep(10)
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            modbusProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    main()
                except Exception as e:
                    errlogger.error(e)
                    modbusProfile()
def get_Data(function, slaveId, binCount, binStart,binLength,ipAddress,port,protocol):
    try:
        print("Slave ID - ",slaveId)
        print("Function - ",function)        
        print("No of packets - {}".format(binCount))        
        print("register length -{}".format(binLength))
        print("Register start -{}".format(binStart))
        print("ipAddress=",ipAddress)
        print("Port=",port)
        print("Protocol",protocol)
        print("Pole Rate =",pollRate)
        print("Baud Rate",baudRate)
        flagError=True
        DataString = ''
        
        if(protocol=='tcp'):
            print("tcp")
            client = ModbusTcpClient(ipAddress, port=port)
        if(protocol=='serial'):
            print("serial")
            client = ModbusSerialClient(method = 'rtu', port = port, baudrate = baudRate, timeout = timeout, parity = parity)
        conn = client.connect()
        print("Connection status:",conn)
        y=""
    
        if(conn):            
            # For Read Holding Register
            if(function == '3'):
                try:                    
                    print("Inside Holding Register")              
                    #Register Address as an argument
                    for countPacket in range(0,binCount):
                        
                        x = client.read_holding_registers(binStart[countPacket],binLength[countPacket],unit = slaveId)                         
                        if(x.isError()):
                            x = client.read_holding_registers(binStart[countPacket],binLength[countPacket],unit = slaveId)                           
                        print("x = ",x)
                        if (x.isError()):
                            try:
                                fcode=x.__getattribute__('fcode')
                                exceptionCode=4
                                print("ExceptionCode :4")
                                y=str(countPacket)+'-'+str(exceptionCode)
                                print(y)
                                flagError = True
                                break
                            except:
                                try:
                                    exceptionCode=x.exception_code
                                    print("Exception Code :",exceptionCode)
                                    y=str(countPacket)+'-'+str(exceptionCode)
                                    flagError = True
                                    break
                                except:
                                    print("unknown error")
                                    y=str(countPacket)+'-'+'12'
                                    
                                    flagError = True
                            
                        else:
                            flagError=False
                            for i in range(0,int(binLength[countPacket])):
                                if countPacket==(binCount-1) and i==(binLength[countPacket]-1):
                                    y=y+str(x.getRegister(i))
                                else:
                                    y=y+str(x.getRegister(i))+str(',')
                        
                        time.sleep(pollRate)
                    
                    DataString = DataString + y
                    #print("DataString =",DataString)
                except Exception as e:
                    print("read error")
                    y=str(countPacket)+'-'+'13'
                    DataString = DataString + y
                    flagError = True
                    print("error :",e)
                    errlogger.error("error code 13 error")
                    errlogger.error(e)
            # For Read Input Register
            if(function == '4'):                
                print("Inside Input Register")
               
                try:                    
                    #Register Address as an argument
                    for countPacket in range(0,binCount):
                        
                        x = client.read_input_registers(binStart[countPacket],binLength[countPacket],unit = slaveId)
                        print("x=",x)
                        if(x.isError()):
                            #retry if error occur
                            x = client.read_input_registers(binStart[countPacket],binLength[countPacket],unit = slaveId)
                            
                        #print(x)
                        if (x.isError()):
                            try:
                                fcode=x.__getattribute__('fcode')
                                exceptionCode=4
                                print("ExceptionCode :4")
                                y=str(countPacket)+'-'+str(exceptionCode)
                                flagError=True
                                break
                            except:
                                try:
                                    exceptionCode=x.exception_code
                                    print("Exception Code :",exceptionCode)
                                    y=str(countPacket)+'-'+str(exceptionCode)
                                    flagError=True
                                    break
                                except:
                                    print("Unknown error")
                                    y=str(countPacket)+'-'+'12'
                                    flagError = True
                                    break
                        else:                        
                            flagError=False
                            for i in range(0,int(binLength[countPacket])):                                    
                                if countPacket==(binCount-1) and i==(binLength[countPacket]-1):
                                    y=y+str(x.getRegister(i))
                                else:
                                    y=y+str(x.getRegister(i))+str(',')
                        time.sleep(pollRate)
                    DataString = DataString + y
                    #print("DataString = ",DataString)
            
                except Exception as e:
                    print("read error")
                    y=str(countPacket)+'-'+'13'
                    DataString = DataString + y
                    flagError = True
                    print("error:",e)
                    errlogger.error("error code 13 error")
                    errlogger.error(e)
            #print("Final String: ",DataString)
        else:
            #If there is no connection Established
            y='0-11'
            flagError=True
            print("No connection")
            DataString = DataString+y
        client.close()
       
        

    except Exception as e:
        flagError = True
        print("error in get data :",e)
        errlogger.error("getData function error :%s",e)
        
        client.close()
    return DataString,flagError
        
'''Function to Read Device'''
def readDevice(LoggerProfile, FlagProfile, DeviceProfile):
    try:
        print("\n*_*_*_*_Processing RMS_*_*_*_*")
        
        deviceCount = int(LoggerProfile[1])#the no of devices to read as per the logger configuration
        print("deviceCount = ",deviceCount)
        print(LoggerProfile)
        print(FlagProfile)
        print(DeviceProfile)
        i = 0
        
        while(i < deviceCount):
            
            print("Reading Devices")
            Device_Data,flagError = get_Data(DeviceProfile.get(i)[0][2], DeviceProfile.get(i)[0][4], DeviceProfile.get(i)[0][5], DeviceProfile.get(i)[0][6], DeviceProfile.get(i)[0][7], DeviceProfile.get(i)[0][8], DeviceProfile.get(i)[0][9], DeviceProfile.get(i)[0][10])
                
            print("DeviceData=",Device_Data)

            time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

            buffer_data = str(LoggerProfile[0]) + ',' + str(LoggerProfile[2]) + ',' + str(DeviceProfile.get(i)[0][1]) + ',' + str(DeviceProfile.get(i)[0][3]) + ','

            print("flagError=",flagError)
            
            if(flagError==False):
                print("correct")
                if(FlagProfile[1]=='0'):
                    LD_Data = buffer_data +'0' +',' +time_stamp
                    ID_Data = Device_Data
                    print("LD_Data=",LD_Data)
                    print("ID_Data=",ID_Data)
                    
                if(FlagProfile[1]=='1'):   
                    buffer_data = buffer_data + '0' + ',' + time_stamp + ',' + Device_Data + '\n'
                    print("Buffer_Data=",buffer_data)
            else:
                print("Incorrect")
                if(FlagProfile[1]=='0'):
                    LD_Data = buffer_data +'1' +',' +time_stamp
                    ID_Data = Device_Data
                    print("LD_Data=",LD_Data)
                    print("ID_Data=",ID_Data)
                if(FlagProfile[1]=='1'):   
                    buffer_data = buffer_data + '1' + ',' + time_stamp + ',' + Device_Data + '\n'
                    print("Buffer_Data ", buffer_data)
            if(FlagProfile[1]=='0'):#if isSD card if false then upload data directly to server
                print("uploading")                
                paramsdata = {'LD': LD_Data, 'ID': ID_Data}
                headers = {'User-Agent': 'Chrome/50.0.2661.102'}
                try:
                    r = requests.get(DATA_URL, headers = headers, params= paramsdata,timeout = 30)
                except Exception as e:
                    errlogger.error(e)
                    print(e)            
                print('Response:',r.text)
                resp=r.text
                if(resp.find("ConnectedOKOK")>=0):
                    print("Data Upload Successful")
                else:
                    print("Data Upload failed")
            if(FlagProfile[1]=='1'):#if isSD card is true then record data to SD card
                print("recording")
                updateData(buffer_data)
            i = i + 1           
            
    except Exception as e:
        print("error read Device =",e)
        errlogger.error("readDevice funtion error : %s",e)
       

def checkFileOpen():
    try:
        print("Entered in checkFileOpen function")
        errlogger.info("Entered in checkFileOpen function")
        time.sleep(10)
        responseServer = run(["pgrep","-x","server.sh"])
        print("responseServer = ",responseServer)
        responseUpload = run(["pgrep","-x","upload.sh"])
        print("responseUpload = ",responseUpload)
        
        
        if not(responseServer.returncode==0):
            print("opening server file...")
            x=call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/server.sh', shell =True)
            print(x)
        else:
            print("server file is open")
        time.sleep(4)
        
        if not(responseUpload.returncode==0):
            print("opening upload file...")
            y=call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/upload.sh', shell =True)
            print(y)
            
        else:
            print("upload file is open")
    except Exception as e:
        print("checkFileOpen function error :",e)
        errlogger.error("Error in checkFileOpen : %s",e)
    
def internet_on():
    try:
        
        response = urllib.request.urlopen(SERVER_URL,timeout = 10)
        return True
    except urllib.request.URLError as err: pass
    except Exception as e:
        errlogger.error(e)
        print(e)
        return False
    return False

def checkFileIdle(checkRowNo):
    try:
        global fileIdleCount,timeCheckIdle
        if LastUploadRowPre==checkRowNo:
            fileIdleCount=fileIdleCount+1
            print("fileIdleCount=",fileIdleCount)
            errlogger.info("file idle count = %d",fileIdleCount)
            print("file idle count = ",fileIdleCount)
            if fileIdleCount==12:
                fileIdleCount=0
                errlogger.info("file idle count is equel to 12 so restarting code")
                #call(['sudo','reboot']) 
        else:
            fileIdleCount=0
            print("fileIdleCount=",fileIdleCount)
            
    except Exception as e:
        print("Error in checkFileIdle function : ",e)
        errlogger.info("Error in checkFileIdle function : %s",e)
def checkLastUploadRow():
    try:
        print("Entered in checkLastRow function")
        errlogger.info("Entered in checkLastRow function")
        global LastUploadRowPre
        
        with open(parentDir+"/records/tracker.txt", 'r') as rowFile:
            data= rowFile.readline()
            rowFile.close()
        
        dataSplit=data.split(',')
        print(dataSplit)
        rowLast=int(dataSplit[4])
        checkFileIdle(rowLast)
        LastUploadRowPre = rowLast 
         
    except Exception as e:
        print("Error in checkLastUploadRow : ",e)
        errlogger.error("Error in checkLastUploadRow : ",e)

def main():
    try:
        global timeCheckIdle
        #checkFileOpen()
        syncTime()
        manufacProfileReturn= manufacProfile()
        print("\nmanufacProfile : ",manufacProfileReturn)
        serialNo=manufacProfileReturn[0]
        print("\nserialNo",serialNo)
        LoggerProfileReturn = loggerProfile()
        print("\nLogger Profile : ",LoggerProfileReturn)
        
        FlagProfileReturn=flagProfile()
        print("\nFlag Profile : ",FlagProfileReturn)
        DeviceProfileReturn = deviceProfile()
        print("\nDevice Profile :  " ,DeviceProfileReturn)
        modbusProfile()
        setRecordFormat()
        print("isActive = ",FlagProfileReturn[0])
        print("isSDCard =",FlagProfileReturn[1])
        #Run First Time
        lasttime = time.time()
        while True:
            if(FlagProfileReturn[0]=='1'):#check if device is active
                if (time.time()-timeCheckIdle>300):
                    checkLastUploadRow()
                    timeCheckIdle = time.time()
                if(FlagProfileReturn[2] == '1'):#check if RMS is active
                    
                    if((time.time() - lasttime) > LoggerProfileReturn[3]):#read devices after every time interval to read time

                        lasttime = time.time()
                        readDevice(LoggerProfileReturn, FlagProfileReturn, DeviceProfileReturn)
                        
            else:
                print("device is disable")
                time.sleep(5)
         
    except Exception as e:
        print("Error in main function : ",e)
        errlogger.error("Error in main funciton :%s ",e)
        
        time.sleep(5)
        main()

if __name__=="__main__":
    main()
