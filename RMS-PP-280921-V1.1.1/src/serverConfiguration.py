import socket
import requests
import urllib.request
import time
from subprocess import call
import logging
from datetime import datetime
import os
from subprocess import *
#from gpiozero import MCP3208
#from backports import configparser
import configparser
from ast import literal_eval
SERVER_URL='http://www.holmiumtechnologies.com'
CONFIG_URL='http://www.holmiumtechnologies.com/rms/api/configuration/sync'
try:    
    workingDir=os.getcwd()
    print(workingDir)
    parentDir=os.path.dirname(workingDir)
    #os.chdir(parentDir)
    print(parentDir)
except:
    print("Error in setting parent directory")



#------Config File parameter check------#
countConfig= 0    # this is used to count failures in configuration file
today   = datetime.today()
year    = str(today.year)
month   = str(today.month)
day     = str(today.day)
now     = datetime.now()
def setLogFormat():
    try:
        print("\n*_*_*_checking year date month log format _*_*_* ")
       
        now     = datetime.now()

        timestamp = now.strftime("%d/%m/%Y")
        dayFilePath=parentDir+'/logs/server_config/'+year+'/'+month+'/'+day+'.txt'
        print(dayFilePath)

        try:
            fileExist=os.path.exists(dayFilePath)
            if (not(fileExist)):
                print("making year and month directory")
                path=parentDir+'/logs/server_config/'
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
    path = parentDir+'/logs/server_config/'+year+'/'+month+'/'+day+'.txt'
    logging.basicConfig(filename = path,format='%(asctime)s --%(levelname)s--Line: %(lineno)s--%(message)s', filemode = 'a')
    errlogger = logging.getLogger()
    errlogger.setLevel(logging.INFO)
    errlogger.info("set configuration for error log successfully")
    print("set configuration for error log successfully")
    
except Exception as e:
    print(e)
    for i in range(0,4):
        time.sleep(5)
    
        if os.execl(sys.executable, sys.executable, *sys.argv):
            break
        else:
            print("retrying again...")
            
                
        



def loggerProfile():
    try:
        global countConfig
        print("entered in logger profile function")
        errlogger.info("entered in logger profile function")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/logger.ini')
            if(len(config.sections()) == 0):
                print("logger Config File is empty")
                errlogger.info("logger Config File is empty")
                call(['cp',parentDir+'/backup/logger.ini',parentDir+'/config/logger.ini'])
                config.read(parentDir+'/config/logger.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.info("path not available :%s",e)
            call(['cp',parentDir+'/backup/logger.ini',parentDir+'/config/logger.ini'])
            config.read(parentDir+'/config/logger.ini')
        loggerProfile = config['loggerProfile']
        #configStatus=loggerProfile['configStatus']
        #print("configStatus=",configStatus)
        global plantId
        plantId=loggerProfile['plantId']
        #print("plantId=",plantId)
        global loggerId
        loggerId=loggerProfile['loggerId']
        #print("loggerId=",loggerId)
        global deviceCount
        deviceCount=loggerProfile['deviceCount']
        #print("deviceCount=",deviceCount)
        global readInterval
        readInterval=loggerProfile['readInterval']
        #print("readInterval=",readInterval)
        
        dataString=''
        dataString=dataString+str(plantId)+','+str(loggerId)+','+str(deviceCount)+','+str(readInterval)
        #print("dataSting=",dataString)
        countConfig=0
    except Exception as e:
        print("error in logger profile :",e)
        errlogger.error("loggerProfile function error : %s",e)
        
        #global countConfig
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            loggerProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    main()
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    loggerProfile()
    return dataString,deviceCount
def deviceProfile():
    try:
        global countConfig
        print("Enterd in deviceProfile function")
        errlogger.info("Enterd in deviceProfile function")
        config=configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/device.ini')
            #print(len(config.sections()))           
            if(len(config.sections())==0):
                print("logger config file is empty")
                call(['cp',parentDir+'/backup/device.ini',parentDir+'/config/device.ini'])
                config.read(parentDir+'/config/device.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.error("path not availble : %s",e)
            call(['cp',parentDir+'/backup/device.ini',parentDir+'/config/device.ini'])
            config.read(parentDir+'/config/device.ini')
            
        
        device=config['device']
        #DGProfile=config['DGProfile']
        #slaveId=str(config['device']['device1']['slaveId'])
        #slaveId=str(deviceProfile['device1']['slaveId'])
        #print("slaveId=",slaveId)
        global deviceData
        deviceData=[]
        count=0
        dataString=''
        global deviceProfileList
        deviceProfileList=[]
        for deviceNo in list(device.keys()):            
            deviceData.append(literal_eval(device[deviceNo]))
            global deviceIndex
            deviceIndex=str(deviceData[count]['deviceIndex'])
            global deviceType
            deviceType=str(deviceData[count]['deviceType'])
            global funCode
            funCode=str(deviceData[count]['funCode'])
            global deviceId
            deviceId=str(deviceData[count]['deviceId'])
            global slaveId
            slaveId=str(deviceData[count]['slaveId'])
            global binCount
            binCount=str(deviceData[count]['binCount'])
            global binStart
            binStart=str(deviceData[count]['binStart'])
            global binLength
            binLength=str(deviceData[count]['binLength'])
            global ipAddress
            ipAddress=str(deviceData[count]['ipAddress'])
            global port
            port=str(deviceData[count]['port'])
            global protocol
            protocol=str(deviceData[count]['protocol'])
            
            dataString=deviceIndex+','+deviceType+','+funCode+','+deviceId+','+slaveId+','+binCount+','+binStart+','+binLength+','+ipAddress+','+port+','+protocol
            deviceProfileList.append(dataString)
            
            count=count+1            
            countConfig=0
        #print("Devicedata:",deviceProfileList)
        
    except Exception as e:
        print("error in device profile :",e)
        errlogger.error("deviceProfile function error :%s",e)
        #global countConfig
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            deviceProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    main()
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    deviceProfile()
    return deviceProfileList
def manufacProfile():
    try:
        global countConfig
        print("Entered in manufacProfile")
        errlogger.info("Entered in manufacProfile")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/manufacture.ini')
            if(len(config.sections()) == 0):
                print("manufacture Config File is empty")
                call(['cp',parentDir+'/backup/manufacture.ini',parentDir+'/config/manufacture.ini'])
                config.read(parentDir+'/config/manufacture.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.info("path not available : %s",e)
            call(['cp',parentDir+'/backup/manufacture.ini',parentDir+'/config/manufacture.ini'])
            config.read(parentDir+'/config/manufacture.ini')
        
        manufacProfile = config['manufacture']
        global serialNo
        serialNo=manufacProfile['serialNo']
        #print("serialNo=",serialNo)
        #pcbVersion=manufacProfile['pcbVersion']
        #print("pcb Version=",pcbVersion)
        global firmwareVersion
        firmwareVersion=manufacProfile['firmwareVersion']
        #print("firmwareVersion=",firmwareVersion)
        #serverAddress=manufacProfile['serverAddress']
        #print("serialNo=",serialNo)
        dataString=''
        dataString=dataString+serialNo+','+firmwareVersion
        countConfig=0
    except Exception as e:
        print("error in manufac config",e)
        errlogger.error("manufacProfile function error :%s",e)
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            manufacProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    main()
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    manufacProfile()
    return dataString,serialNo
def flagProfile():
    try:
        global countConfig
        print("Entered in flagProfile function")
        errlogger.error("Entered in flagProfile function")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/flag.ini')
            if(len(config.sections()) == 0):
                print("manufacture Config File is empty")
                call(['cp',parentDir+'/backup/flag.ini',parentDir+'/config/flag.ini'])
                config.read(parentDir+'/config/flag.ini')
        except Exception as e:
            print("path not available : ",e)
            errlogger.info("path not available : %s",e)
            call(['cp',parentDir+'/backup/flag.ini',parentDir+'/config/flag.ini'])
            config.read(parentDir+'/config/flag.ini')
        flagProfile = config['controlFlag']
        global isActive
        isActive= flagProfile['isActive']
        global isSdCard
        isSdCard=flagProfile['isSdCard']
        global isRms
        isRms=flagProfile['isRms']
        global isDgSync
        isDgSync=flagProfile['isDgSync']
        global isZeroExport
        isZeroExport=flagProfile['isZeroExport']
        dataString=''
        dataString=dataString+str(isActive)+','+str(isSdCard)+','+str(isRms)+','+str(isDgSync)+','+str(isZeroExport)
        countConfig=0
    except Exception as e:
        print("Error in flag read profile")
        errlogger.error("flagProfile function error : ",e)
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            flagProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    if os.execl(sys.executable, sys.executable, *sys.argv):
                        break
                    else:
                        print("retrying again...")
                        os.execl(sys.executable, sys.executable, *sys.argv)
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    flagProfile()
    return dataString    

def trackerProfile():
    try:
        global countConfig
        print("Entered in trackerProfile")
        errlogger.info("Entered in trackerProfile")
        try:
            with open(parentDir+'/records/tracker.txt','r') as file:
                print("opening")
                data = file.readline()
                print("data =",data)
                dataSplit = data.split(',')
        except Exception as e:
            print("path not available :",e)
            errlogger.error("path not available : %s",e)
            call(['cp',parentDir+'/backup/tracker.txt',parentDir+'/records/tracker.txt'])
            with open(parentDir+'/records/tracker.txt','r') as file:
                data = file.readline()
                dataSplit = data.split(',')
        global year   
        year = dataSplit[0]
        global month
        month = dataSplit[1]
        global day
        day = dataSplit[2]
        global hour
        hour = dataSplit[3]
        global row
        row = dataSplit[4]
        global dataString
        dataString=''
        dataString=dataString+year+','+month+','+day+','+hour+','+row
        countConfig=0
    except Exception as e:
        print("Error in tracker profile")
        errlogger.error("trackerProfile function error")
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            trackerProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    main()
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    trackerProfile()
    return dataString
def modbusProfile():
    try:
        global countConfig
        print("Entered in modbusProfile")
        errlogger.info("Entered in modbusProfile")
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/modbus.ini')
            if(len(config.sections()) == 0):
                print("manufacture Config File is empty")
                call(['cp',parentDir+'/backup/modbus.ini',parentDir+'/config/modbus.ini'])
                config.read(parentDir+'/config/modbus.ini')
        except Exception as e:
            call(['cp',parentDir+'/backup/modbus.ini',parentDir+'/config/modbus.ini'])
            config.read(parentDir+'/config/modbus.ini')
        modbusProfile = config['modbus']
        global baudRate
        baudRate = modbusProfile['baudRate']
        print("baudRate =",baudRate)
        global parity
        parity = modbusProfile['parity']
        print("parity = ",parity)
        global pollRate
        pollRate = modbusProfile['pollRate(ms)']
        print("pollRate = ",pollRate)
        global timeout
        timeout = modbusProfile['timeout(ms)']
        print("timeout = ",timeout)
        global dataString
        dataString=''
        dataString=dataString+baudRate+','+parity+','+pollRate+','+timeout
        countConfig=0
    except Exception as e:
        print("error in modbus config",e)
        errlogger.error("modbusProfile function error : ",e)
        time.sleep(5)
        countConfig = countConfig+1
        print("countConfig=",countConfig)
        if countConfig<=5:
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
            modbusProfile()
        elif countConfig>5 and countConfig<=10:
            errlogger.info("counConfig is greaer than 5 and less than 11 so restaring code")
            print("config count is >5 and less than 11 so restarting the code")
            for i in range(0,4):
                try:
                    time.sleep(2)
                    print(i)
                    main()
                except Exception as e:
                    print(e)
                    errlogger.error(e)
                    modbusProfile()
    return dataString
'''**************Upload functions*******************'''


def uploadManufacConfig(serialNo,manufacProfileReturn):
    try:
        print("\nEntered in uploadManufacConfig function\n")
        errlogger.info("Entered in uploadManufacConfig function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        manufacProfile=manufacProfileReturn
        dataString='serialNo='+str(serialNo)+'&command=MFCV&configuration='+manufacProfile
        print("DataString:",dataString)
        
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)

            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("manufacture Upload Successful")
                return True
            else:
                return False
        except Exception as e:
            print("error  :",e)
            errlogger.error(e)
        
    except Exception as e:
        print("uploadManufac function error : ",e)
        errlogger.error("upload manufacConfig function error :%s",e)
        

def uploadLoggerConfig(serialNo,loggerProfileReturn):
    try:
        print("\nEntered in uploadLoggerConfig\n")
        errlogger.info("Entered in uploadLoggerConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        loggerProfile=loggerProfileReturn
        dataString='serialNo='+str(serialNo)+'&command=LSCV&configuration='+loggerProfile
        print("DataString:",dataString)
        
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)

            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("Logger config upload Successful")
                return True
            else:
                return False
        except Exception as e:
            print(e)
            errlogger.error(e)
    except Exception as e:
        print("uploadLoggerConfig error : ",e)
        errlogger.error("uploadLoggerConfig function error :%s",e)
       

def uploadDeviceConfig(serialNo,deviceProfile,deviceCount):
    uploadFlag=False
    try:
        print("\nEntered in uploadDeviceConfig\n")
        errlogger.info("Entered in uploadDeviceConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        device_count=int(deviceCount)
        for i in range(0,device_count):
        
            dataString='serialNo='+serialNo+'&command=SDCV&deviceIndex='+str(i)+'&configuration='+deviceProfile[i]
            print("deviceProfileString=",dataString)
            paramsadata = dataString
            try:
                r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
                print('Response:',r.text)
                resp=r.text
                if(resp.find("OK")>=0):
                    print("Device config upload success")
                    uploadFlag=True
            except Exception as e:
                print(e)
                errlogger.error(e)
           
        
    except Exception as e:
        print("UploadDeviceConfig  :",e)
        errlogger.error("uploadDeviceConfig function error : %s",e)
       
    return uploadFlag

def uploadFlagConfig(serialNo,flagProfile):
    try:
        print("\nEntered in uploadFlagConfig\n")
        errlogger.info("Entered in uploadFlagConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}        
        dataString='serialNo='+str(serialNo)+'&command=CFCV&configuration='+flagProfile
        print("DataString:",dataString)
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("control flag Upload Successful")
        except Exception as e:
            print(e)
            errlogger.error(e)
       
        
    except Exception as e:
        print("uploadFlagConfig function error",e)
        errlogger.error("uploadFlagConfig function error : %s",e)
      


def uploadTrackerConfig(serialNo,trackerProfile):
    try:
        print("\nEntered in uploadTrackerConfig\n")
        errlogger.info("Entered in uploadTrackerConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}    
        dataString='serialNo='+str(serialNo)+'&command=UPLOADTRACKER&configuration=='+trackerProfile
        print("DataString:",dataString)
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            
            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("tracker Upload Successful")
        except Exception as e:
            print(e)
            errlogger.error(e)
        #print(time.time())
        
    except Exception as e:
        print("uploadTrackerConfig function error",e)
        errlogger.error("uploadTrackerConfig function error:",e)
      

def uploadModbusConfig(serialNo,modbusProfile):
    try:
        print("\nEntered in uploadModbusConfig\n")
        errlogger.info("Entered in uploadModbusConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}        
        dataString='serialNo='+str(serialNo)+'&command=UPLOADMODBUS&configuration='+modbusProfile
        print("DataString:",dataString)
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            
            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("modbus Upload Successful")
            print(time.time())
        except Exception as e:
            print(e)
            errlogger.error(e)
       
        
    except Exception as e:
        print("uploadModbusConfig function error",e)
        errlogger.error("uploadModbusConfig function error :%s",e)
        

 


'''**********Verfication rules for configuration parameters**************************'''

def downloadFlagConfig(serialNo):
    try:
        
        print("\n Entered in downFlagConfig\n")
        errlogger.info("Entered in downFlagConfig")
        print("serialNo=",serialNo)
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
        dataString='serialNo='+serialNo+'&command=CFC'
        flagCheckControlConfig=False
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            serverResponse=r.text    #comment out for real
            #serverResponse='serialNo=HO-201011&response=0,0,1,0,0'  #for testing
            serverSplit=serverResponse.split('&response=')
            #print("serverSplit=",serverSplit)
            serverSerialData=serverSplit[0]
            #print(serverSerialData)
            serverSerialSplit=serverSerialData.split('serialNo=')
            #print(serverSerialSplit)
            serialNoServer=serverSerialSplit[1]
            #print("serial no server",serialNoServer)
            flagCheckControlConfig=False
            if(serialNoServer==serialNo): 
                flagCheckControlConfig=True
                
        except Exception as e:
            print(e)
            errlogger.error(e)
                
    except Exception as e:
        print("error in downFlagConfig  error :",e)
        errlogger.error("downFlagConfig function error :%s",e)
       
    return flagCheckControlConfig,  serverSplit[1]

def downloadLoggerConfig(serialNo):
    try:
        print("\nEntered in downLoggeConfig\n")
        errlogger.info("Entered in downLoggerConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
        print("serialNo=",str(serialNo))
        dataString='serialNo='+serialNo+'&command=LSC'
        
        flagCheckLoggerConfig=False
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 30)
            print('Response:',r.text)
            serverResponse=r.text    #comment out for real
            #serverResponse='serialNo=HO-201011&response=0,301,1,1,60'
            serverSplit=serverResponse.split('&response=')
            #print("serverSplit=",serverSplit)
            serverSerialData=serverSplit[0]
            serverSerialSplit=serverSerialData.split('serialNo=')
            
            #print(serverSerialSplit)
            serialNoServer=serverSerialSplit[1]
            #print("serialNoServer =",serialNoServer)
            #print("serialNo=",serialNo)
            loggerData=serverSplit[1]
            splitLoggerData=loggerData.split(',')
            deviceCount=splitLoggerData[2]

            
            config=configparser.ConfigParser()
            if(serialNoServer==serialNo):
                print("both serial NO are equal")
                flagCheckLoggerConfig=True
        except Exception as e:
            print(e)
       
        
               
    except Exception as e:
        print("error in downLoggerConfig function :",e)
        errlogger.error("downLoggerConfig function error")
        errlogger.error(e)
    return flagCheckLoggerConfig,   serverSplit[1],deviceCount

def downloadDeviceConfig(serialNo,deviceCount):
    try:
        print("\nEntered in downDeviceConfig function\n")
        errlogger.info("Entered in downloadDeviceConfig function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        deviceDataList=[]
        for i in range(0,int(deviceCount)):
            
            dataString='serialNo='+serialNo+'&command=SDC&deviceIndex='+str(i)
            
            paramsadata = dataString
            try:
                r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 30)

                print('Response:',r.text)
                serverResponse=r.text    #comment out for real
                
                #serverResponse='serialNo=HO-201011&response=1,52,03,1,1,1,10,192.168.10.1,/dev/ttyUSB0,serial'    #for testing
                serverSplit=serverResponse.split('&response=')
                #print("serverSplit=",serverSplit)
                
                serverSerialData=serverSplit[0]
                deviceData=serverSplit[1]
                serverSerialSplit=serverSerialData.split('serialNo=')
                serialNoServer=serverSerialSplit[1]
                flagCheckDeviceConfig=False
                if(serialNoServer==serialNo):
                    flagCheckDeviceConfig=True
                    deviceDataList.append(deviceData)

            except Exception as e:
                print(e)
                errlogger.error(e)
           
            

    except Exception as e:
        print("error in downDeviceConfig :",e)
        errlogger.error("error in downDeviceConfigfuntion :%s",e)
        
    return flagCheckDeviceConfig,deviceDataList


def downTrackerConfig(serialNo):
    try:
        print("\nEntered in downTrackerConfig function\n")
        errlogger.info("Entered in downTrackerConfig function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}        
           
        dataString='serialNo='+str(serialNo)+'&command=DOWNLOADTRACKER'
        print("DataString:",dataString)
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            
            print('Response:',r.text)
            serverResponse=r.text    #comment out for real    
            serverSplit=serverResponse.split('&response=')
            #print("serverSplit=",serverSplit)
            serverSerialData=serverSplit[0]
            trackerData=serverSplit[1]
            serverSerialSplit=serverSerialData.split('serialNo=')
            serialNoServer=serverSerialSplit[1]
            flagCheckTrackerConfig=False
            if(serialNoServer==serialNo):
                print("both Serial No are equel")
                flagCheckTrackerConfig=True
                
        except Exception as e:
            print(e)
            errlogger.error(e)
       
        
    except Exception as e:
        print("downTrackerConfig function error",e)
        errlogger.error("downTrackerConfig function error :%s",e)
        
    return flagCheckTrackerConfig, trackerData


def downModbusConfig(serialNo):
    try:
        print("\n Entered in downMpdbusConfig\n")
        errlogger.error("Entered in downModbusConfig")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}        
           
        dataString='serialNo='+str(serialNo)+'&command=DOWNLOADMODBUS'
        print("DataString:",dataString)
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            serverResponse=r.text    #comment out for real    
            serverSplit=serverResponse.split('&response=')
            #print("serverSplit=",serverSplit)
            serverSerialData=serverSplit[0]
            modbusData=serverSplit[1]
            serverSerialSplit=serverSerialData.split('serialNo=')
            serialNoServer=serverSerialSplit[1]
            flagCheckTrackerConfig=False
            if(serialNoServer==serialNo):
                flagCheckModbusConfig=True    
        except Exception as e:
            print(e)
            errlogger.error(e)
    except Exception as e:
        print("downModbusConfig function error",e)
        errlogger.error("downModbusConfig function error :",e)
        
    return flagCheckModbusConfig, modbusData

'''**********************************************************'''
'''*************Write configuration to file *****************'''

def writeFlagConfig(controlConfigStr):
    try:
        print("\n writing Flag Configuration \n")
        errlogger.info("writing flag configuration :")
        config = configparser.ConfigParser()
        data=controlConfigStr
        dataSplit=data.split(',')
        config['controlFlag']={}
        
        isActive=dataSplit[0]
        config['controlFlag']['isActive']=isActive       
        isSDCard=dataSplit[1]
        config['controlFlag']['isSdCard']=isSDCard
        isRMS=dataSplit[2]
        config['controlFlag']['isRms']=isRMS
        isDGSync=dataSplit[3]
        config['controlFlag']['isDgSync']=isDGSync
        isZeroExport=dataSplit[4]
        config['controlFlag']['isZeroExport']=isZeroExport
        flagWriteControlConfig=False
        print("Ok upto here")
        with open(parentDir+"/config/flag.ini", 'w') as configfile:
            config.write(configfile)
            print("saved controlflag successsfully")
            flagWriteControlConfig=True
    except Exception as e:
        
        print("error in writeFlagConfig function  :",e)
        errlogger.error("writeControlConfig function error :%s ",e)
    return flagWriteControlConfig
    
def writeLoggerConfig(loggerConfigStr):
    try:
        print("\nEntered in writeLoggerConfig \n")
        errlogger.error("Entered in writeLoggerConfig")
        config = configparser.ConfigParser()
        data=loggerConfigStr
        print("data = ",data)
        dataSplit=data.split(',')
        config['loggerProfile']={}
##        configStatus='1'
##        config['loggerProfile']['configStatus']=configStatus
        plantId=dataSplit[0]
        config['loggerProfile']['plantId']=plantId
        loggerId=dataSplit[1]
        config['loggerProfile']['loggerId']=loggerId
        deviceCount=dataSplit[2]
        config['loggerProfile']['deviceCount']=deviceCount
        readInterval=dataSplit[3]
        config['loggerProfile']['readInterval']=readInterval
       
        flagWriteLoggerConfig=False
        with open(parentDir+"/config/logger.ini", 'w') as configfile:
            config.write(configfile)
            flagWriteLoggerConfig=True
            print("Logger prfile saved successfully")
    except Exception as e:
        print("error in writeLoggerConfig :",e)
        errlogger.error("writeLoggerConfig function error :%s",e)
        
    return flagWriteLoggerConfig


def writeDeviceConfig(deviceConfigStr):
    try:
        print("\n Entered in writeDeviceConfig\n")
        errlogger.error("Entered in writeDevicConfig")
        config = configparser.ConfigParser()
        config['device']={}
        data=deviceConfigStr
        print("data",data)
        dataLen=len(data)
        print("dataLen=",dataLen)
        flagriteDeviceConfig=False
        with open(parentDir+'/config/device.ini', 'w') as configfile:
            for i in range(0,dataLen):
                deviceData=data[i]
                print("Data",deviceData)
                deviceSplit=deviceData.split(',')
                
                print("device data:",deviceSplit)
                binStartStr=''
                binLengthStr=''
                binCount=int(deviceSplit[5])
                for j in range(0,binCount): 
                    if(j<(binCount-1)):
                        binStartStr=binStartStr+deviceSplit[6+j]+','
                        binLengthStr=binLengthStr+deviceSplit[6+binCount+j]+','
                    if(j==(binCount-1)):
                        binStartStr=binStartStr+deviceSplit[6+j]
                        binLengthStr=binLengthStr+deviceSplit[6+binCount+j]
                print("binStartStr= ",binStartStr)
                print("binLengthStr= ",binLengthStr)
                string='{\n"deviceIndex":'+deviceSplit[0]+','+'\n"deviceType":'+deviceSplit[1]+','+'\n"funCode":'+'"'+str(deviceSplit[2])+'"'+','+'\n"deviceId":'+deviceSplit[3]+','+'\n"slaveId":'+deviceSplit[4]+','+'\n"binCount":'+deviceSplit[5]+','+'\n"binStart":'+'"'+binStartStr+'"'+','+'\n"binLength":'+'"'+binLengthStr+'"'+','+'\n"ipAddress":'+'"'+str(deviceSplit[5+2*binCount+1])+'"'+','+'\n"port":'+'"'+str(deviceSplit[5+2*binCount+2])+'"'+','+'\n"protocol":'+'"'+str(deviceSplit[5+2*binCount+3])+'"'+','+'\n}'
                print("string=",string)
                deviceName='device'+str(i+1)
                config['device'][deviceName]=string
            config.write(configfile)
            flagWriteDeviceConfig=True
            print("device profile saved successful")

    except Exception as e:
        print("error in writeDeviceConfig :",e)
        errlogger.error("writeDeviceConfig function error : %s",e)
    return flagWriteDeviceConfig

def writeTrackerConfig(trackerConfigStr):
    try:
        print("\n Entered in writeTrackerConfig function")
        errlogger.info("Entered in writeTrackerConfig function")
        
        flagWriteTrackerConfig = False
        path = parentDir+'/records/tracker.txt'
        with open(path,'w') as file:
            file.write(trackerConfigStr)
            flagWriteTrackerConfig = True
            print("trackerProfile write success")
    except Exception as e:
        print("writeTrackerConfig function error : ",e)
        errlogger.error("writeTrackerConfig function error : %s",e)
        flagWriteTrackerConfig = False
    return flagWriteTrackerConfig


def writeModbusConfig(modbusConfigStr):
    try:
        print("\nEntered in writeModbusConfig function \n")
        errlogger.info("Entered in writeModbusConfig function")
        config = configparser.ConfigParser()
        data=modbusConfigStr
        dataSplit=data.split(',')
        config['modbus']={}
##        configStatus='1'
##        config['loggerProfile']['configStatus']=configStatus
        baudRate = dataSplit[0]
        config['modbus']['baudRate'] = baudRate
        parity = dataSplit[1]
        config['modbus']['parity'] = parity
        pollRate= dataSplit[2]
        config['modbus']['pollRate(ms)'] = pollRate 
        timeout = dataSplit[3]
        config['modbus']['timeout(ms)']=timeout
        flagWriteModbusConfig=False
        with open(parentDir+"/config/modbus.ini", 'w') as configfile:
            config.write(configfile)
            flagWriteModbusConfig=True
            print("Modbus prfile saved successfully")
    except Exception as e:
        print("error in writeModbusConfig :",e)
        errlogger.error("writeModbusConfig function error : %s",e)
        
    return flagWriteModbusConfig
######################################################################################
'''**************************Verify configuration from server***********************'''
def verifyLoggerProfile(loggerData):
    try:
        print("\nEntered in verifyLoggerProfile")
        errlogger.info("Entered in verifyLoggerProfile")
        loggerDataSplit=loggerData.split(',')
        
        #print("loggerDataSplit",loggerDataSplit)
        configStatus=int(loggerDataSplit[0])
        #print("configStatus =",configStatus)
        
        plantId=int(loggerDataSplit[1])
        #print("plantId =",plantId)
        deviceCount=int(loggerDataSplit[2])
        #print("deviceCount =",deviceCount)
        readInterval=int(loggerDataSplit[4] )
        #print("read Interval =",readInterval)
        if((configStatus==0) or (configStatus==1) ):
            if(not(plantId==0) and plantId>=200 and plantId<=400):
                if(readInterval>=30 and readInterval<=300):
                    return True
            
        
    except Exception as e:
        print("error in verify logger profile",e)
        errlogger.error("verifyLoggerProfile function error :%s",e)
        return False

def checkConfiguration(serialNo):
    try:
        print("\nEntered in checkConfiguration function\n")
        errlogger.info("Entered in checkConfiguration function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
       
        dataString='serialNo='+str(serialNo)+'&command=CNFCHK'
        
        paramsadata = dataString
        flagNormal = False
        flagExtended = False
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("TRUE")>=0):
                flagNormal = True
            elif (resp.find("FALSE")>=0):
                flagNormal = False
            elif (resp.find("EXTENDED")>=0):
                flagExtended = True
            
        except Exception as e:
            print(e)       
    except Exception as e:
        print("error check configuration :",e)
        errlogger.error("checkConfiguration function error :%s",e)
    return flagNormal, flagExtended
def checkExtendedTypeFlag(serialNo):
    try:
        print("\nEntered in checkExtendedTypeFlag\n")
        errlogger.info("Entered in checkExtendedTypeFlag")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        flagUploadTracker = False
        flagDownTracker = False
        flagUploadModbus = False
        flagDownModbus = False
        flagNormalMode = False
        flagResetEEPROM = False
        flagReboot =False
       
        dataString='serialNo='+str(serialNo)+'&command=ECNFCHK'
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("UPLOADTRACKER")>=0):
                flagUploadTracker = True
                
            if(resp.find("DOWNLOADTRACKER")>=0):
                flagDownTracker = True
            if(resp.find("UPLOADMODBUS")>=0):
                flagUploadModbus = True
            if(resp.find("DOWNLOADMODBUS")>=0):
                flagDownModbus = True
            if(resp.find("CNFCHK")>=0):
                flagNormalMode = True
            if(resp.find("RESETEEPROM")>=0):
                flagResetEEPROM = True
            if(resp.find("REBOOTDEVICE")>=0):
                flagReboot = True
        except Exception as e:
            print(e)
            errloggger.error(e)
            
       
        
    except Exception as e:
        print("error in function checkExtendedFlag :",e)
        errlogger.error("error in function checkExtendedFlag :%s ",e)
    return flagUploadTracker, flagDownTracker, flagUploadModbus, flagDownModbus, flagNormalMode, flagResetEEPROM, flagReboot
    


def rebootAcknowledge(serialNo):
    try:
        print("\nEntered in rebootAcknowledge\n")
        errlogger.info("Entered in rebootAcknowledge")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
       
        dataString='serialNo='+str(serialNo)+'&command=REBOOTDEVICE&configuration=OK'
        
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("rebootAcknowledge success")
                return True
            else:
                print("rebootAcknowledge failed")
                return False
        except Exception as e:
            print(e)       
       
        
    except Exception as e:
        print("error rebootAcknowledge function:",e)
        errlogger.error("rebootAcknowledge function error : %s",e)
        return False
def resetEEPROM(serialNo):
    try:
        print("Entered in resetEEPROM function")
        errlogger.info("Entered in resetEEPROM function")
        controlStr ="1,1,1,0,0,"
        loggerStr ="302,1,1,60"
        deviceStr ="0,52,03,1,1,1,1,10,192.168.10.1,/dev/ttyUSB0,serial"
        modbusStr = '9600,0,250,1000'
        deviceDataList=[]
        deviceDataList.append(deviceStr)
        flagWriteControlConfig = writeFlagConfig(controlStr)
        flagWriteLoggerConfig = writeLoggerConfig(loggerStr)
        flagWriteDeviceConfig = writeDeviceConfig(deviceDataList)
        flagWriteModbusConfig = writeModbusConfig(modbusStr)
        if((flagWriteControlConfig ==True) and (flagWriteLoggerConfig ==True) and (flagWriteDeviceConfig ==True) and (flagWriteModbusConfig ==True)):
            
            print("sending resetAcknowledgement")
            if(resetAcknowledge(serialNo)==True):
                print("Rebooting device ")
                call(['sudo','reboot'])
        else:
            print("reset device failed")
                
    except Exception as e:
        print("resetDevice function error")
        errlogger.error("Reset device funtion error : %s",e)

def resetAcknowledge(serialNo):
    try:
        print("\nChecking reset acknowledgement function\n")
        errlogger.info("Entered in resetAcknowledge function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
       
        dataString='serialNo='+str(serialNo)+'&command=RESETEEPROM&configuration=OK'
        
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("OK")>=0):
                print("reset acknowledge success")
                return True
            else:
                print("reset acknowledge failed")
                return False
        except Exception as e:
            print(e)
            errlogger.error(e)
            return False
       
        
    except Exception as e:
        print("error resetAcknowledge function:",e)
        errlogger.error("resetAcknowledge function error : %s",e)
        return False

def sendConfigDone(serialNo):
    try:
        print("\nEntered in sendConfigDone")
        errlogger.info("Entered in sendConfigDone")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        dataString='serialNo='+str(serialNo)+'&command=CNFDONE'
        
        paramsadata = dataString
        try:
            r = requests.get(CONFIG_URL, headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("TRUE")>=0):
                return True
            else:
                return False
        except Exception as e:
            print(e)
            errlogger.error(e)

    except Exception as e:
        print("error in sendConfigDone function :",e)
        errlogger.error("Error in sendConfigDone :%s",e)
        
        return False
def normalConfiguration(serialNo):
    try:
        print("Entered in normalConfiguration function")
        errlogger.info("Entered in normalConfiguration function")
        flagControlConfig,  flagConfigStr=downloadFlagConfig(serialNo)
        print("flag control config =",flagControlConfig)
        flagLoggerConfig,  loggerConfigStr,noDevice=downloadLoggerConfig(serialNo)
        print("flag logger config =",flagLoggerConfig)
        flagDeviceConfig,  deviceConfigStr=downloadDeviceConfig(serialNo,noDevice)
        print("flag device config =",flagDeviceConfig)
        if(flagControlConfig==True and flagLoggerConfig==True and flagDeviceConfig==True):
            
        
            print("all control ,logger,device config are true")
            errlogger.info("all control, logger, device config are true")
            statusWriteFlagConfig=writeFlagConfig(flagConfigStr)
            statusWriteLoggerConfig=writeLoggerConfig(loggerConfigStr)
            statusWriteDeviceConfig=writeDeviceConfig(deviceConfigStr)
            if(statusWriteFlagConfig==True and statusWriteLoggerConfig==True and statusWriteDeviceConfig==True):
                if(sendConfigDone(serialNo)==True):
                    print("rebooting device")
                    errlogger.info("rebooting device")
                    call(['sudo','reboot'])
                    
    except Exception as e:
        print("error in normalConfiguration function,",e)
        errlogger.error("error in normalConfiguration function error :%s",e)
        

def extendedConfiguration(serialNo ):
    try:
        print("Entered in extendedConfiguration funciton")
        errlogger.info("Entered in extendedConfiguration")
        flagNormalMode = False
        flagUploadTracker, flagDownTracker, flagUploadModbus, flagDownModbus, flagNormalMode, flagResetEEPROM, flagReboot = checkExtendedTypeFlag(serialNo)
        if(flagUploadTracker==True):
            print("flagUploadTracker = True")
            errlogger.info("flagUploadTracker = True")
            trackerProfileReturn = trackerProfile()
            uploadTrackerConfig(serialNo, trackerProfileReturn)
        elif(flagDownTracker==True):
            print("flagDownTracker = True")
            flagDownTrackerConfig, trackerData = downTrackerConfig(serialNo)
            if(flagDownTrackerConfig == True):
                print("tracker download success")
                errlogger.error("tracker download success")
                print("killing upload.sh")
                errlogger.info("killing upload.sh")
                print(call(['sudo','killall','upload.sh']))
                flagWriteTrackerConfig = writeTrackerConfig(trackerData)
                if(flagWriteTrackerConfig == True):
                    print("tracker write sucess")
                    errlogger.info("tracker write success")
                print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/upload.sh', shell =True))           
                    
        elif(flagUploadModbus==True):
            print("flagUploadModbus = True")
            errlogger.info("flagUploadModbus = True")
            modbusProfileReturn = modbusProfile()
            uploadModbusConfig(serialNo, modbusProfileReturn)
            
        elif(flagDownModbus==True):
            print("flagDownModbus = True")
            errlogger.info("flagDownModbus = True")
            flagDownModbusConfig, modbusData = downModbusConfig(serialNo)
            if(flagDownModbusConfig == True):
                print("modbus download success")
                errlogger.info("modbus download success")
                print("killing file.sh and upload.sh")
                errlogger.info("killing file.sh and upload.sh")
                print(call(['sudo','killall','file.sh']))
                print(call(['sudo','killall','upload.sh']))
                flagWriteModbusConfig = writeModbusConfig(modbusData)
                if(flagWriteModbusConfig == True):
                    print("modbus write sucess")
                    errlogger.info("modbus write sucess")
                    time.sleep(7)
                    print("opening file.sh")
                    errlogger.info("opening file.sh")
                    print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/file.sh', shell =True))
                    time.sleep(3)
                    print("opening upload.sh")
                    errlogger.info("opening upload.sh")
                    print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/upload.sh', shell =True))
        elif(flagNormalMode == True):
            print("flagNormalMode")
            errlogger.info("flag Normal mode")
            print("back to normal mode")
        elif(flagResetEEPROM == True):
            resetEEPROM(serialNo)
        elif(flagReboot == True):
            if rebootAcknowledge(serialNo) == True:
                print("Rebooting device....")
                errlogger.info("rebooting device")
                call(['sudo','reboot'])
    except Exception as e:
        print("error in extendedConfiguration function",e)
        errlogger.error("error in extendedConfiguration function :%s",e)
       
    

def checkFileOpen():
    try:
        print("Entered in checkFileOpen")
        errlogger.info("Entered in checkFileOpen")
        time.sleep(20)
        responseServer = run(["pgrep","-x","server.sh"])
        print("responseServer = ",responseServer)
        responseUpload = run(["pgrep","-x","upload.sh"])
        print("responseUpload = ",responseUpload)
        responseFile = run(["pgrep","-x","file.sh"])
        print("responseFile = ",responseFile)
        
        if not(responseFile.returncode==0):
            print("opening file_read file.....")
            errlogger.info("opening file_read file.....")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/file.sh', shell =True))
        else:
            print("file_read is open")
        time.sleep(4)
        if not(responseServer.returncode==0):
            print("opening server file...")
            errlogger.info("opening server file....")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/server.sh', shell =True))
        else:
            print("server file is open")
        time.sleep(4)
        
        if not(responseUpload.returncode==0):
            print("opening upload file...")
            print("opening upload file")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/upload.sh', shell =True))
        else:
            print("upload file is open")
    except Exception as e:
        print("checkFileOpen function error : ",e)
        errlogger.error("checkFileOpen function error :",e)
def backupConfigFiles():
    try:
        print("Entered in backupConfigFiles")
        errlogger.info("Entered in backupConfigFiles")
        call(['cp',parentDir+'/config/logger.ini',parentDir+'/backup/logger.ini'])
        time.sleep(1)
        call(['cp',parentDir+'/config/device.ini',parentDir+'/backup/logger.ini'])
        time.sleep(1)
        call(['cp',parentDir+'/config/flag.ini',parentDir+'/backup/flag.ini'])
        time.sleep(1)
        call(['cp',parentDir+'/config/manufacture.ini',parentDir+'/backup/manufacture.ini'])
        time.sleep(1)
        call(['cp',parentDir+'/records/tracker.txt',parentDir+'/backup/tracker.txt'])
        print("backup successful")
    except Exception as e:
        print("Error in backupConfigFiles :",e)
        errlogger.error("Error in backupConfigFiles",e)
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
def connectToInternet():
    try:
        errlogger.info("Entered in connectToInternet function")
        global countConfig
        call(["sudo", "pon","rnet"])
        time.sleep(10)
        
        for i in range(0,5):
            conn = internet_on()
            if(conn==True):
                print("Internet is OK")
                errlogger.info("Internet is OK")
                break
            time.sleep(2)
        countConfig=0
    except Exception as e:
        print("Error in connectToInternet function")
        errlogger.error("Error in connectToInternet")
        countConfig=countConfig+1
        if countConfig<5:
            print("connecting to internet ")
            connectToInternet()
def main():
    try:
        print("Entered in main function")
        backupConfigFiles()
        errlogger.info("Entered in main function")
        connectToInternet()
        manufacProfileReturn,serialNo=manufacProfile()
        print("manufacture Profile: ",manufacProfileReturn)
        
        loggerProfileReturn,deviceCount=loggerProfile()
        print("Logger Profile :",loggerProfileReturn)
        
        deviceProfileReturn=deviceProfile()
        print("device Profile :",deviceProfileReturn)

        flagProfileReturn=flagProfile()
        print("flagProfile :",flagProfileReturn)

        trackerProfileReturn = trackerProfile()
        print("trackerProfile : ",trackerProfileReturn)

        modbusProfileReturn = modbusProfile()
        print("modbusProfile : ",modbusProfileReturn)
        ##upload configuration to server
        uploadManufacConfig(serialNo, manufacProfileReturn)
        uploadLoggerConfig(serialNo,loggerProfileReturn)
        uploadDeviceConfig(serialNo,deviceProfileReturn,deviceCount)
        uploadFlagConfig(serialNo,flagProfileReturn)
       
        #print("Reseting....")
        #resetConfiguration(serialNo)
        time.sleep(5)
        while(True):            
            print("\n\n\t_*_*_*_*_*_*_Server Based Configuration_*_*_*_*_*\n")
            
            
            flagNormalMode, flagExtendedMode = checkConfiguration(serialNo)
            print("flagNormal={} & flagExtended={}",flagNormalMode,flagExtendedMode)
            if flagNormalMode==True:
                print("normal mode.....")
                errlogger.info("normal mode....")
                normalConfiguration(serialNo)            
                       
            elif flagExtendedMode:
                print ("Extended Mode.....")
                errlogger.info("Extended Mode....")
                extendedConfiguration(serialNo)
            time.sleep(60)
            connectToInternet()
                
    except Exception as e:
        print("error in main function :",e)
        errlogger.error("main function error : %s",e)
    

if __name__=="__main__":
    main()
    
