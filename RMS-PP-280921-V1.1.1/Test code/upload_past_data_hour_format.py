import socket
import requests
import urllib.request
import time
from subprocess import call
import logging
from datetime import datetime
import RPi.GPIO as GPIO
import os
import configparser
import serial
import sys
TIME_URL='http://www.holmiumtechnologies.com/rms/api/timestamp/sync'
DATA_URL='http://www.holmiumtechnologies.com/rms/api/insertdata?'
SERVER_URL='http://www.holmiumtechnologies.com'


#----GPIO Initialization---#
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
pwrKey =12
GPIO.setup(pwrKey,GPIO.OUT)

#global variable for AT command flag
flagATcommand=False
isGSM=0

#global variable for tracking last upload details
YEAR_FLAG=0
MONTH_FLAG=0
DAY_FLAG=0
HOUR_FLAG=0
#globalVariables for
LastUploadRow = 1
LastUploadHour=0
LastUploadDay = 8
LastUploadMonth = 5
LastUploadYear = 2021



errorCount =0      #assigning of the count for restart , syncTime,main error
fileIdleCount=0     #for counting when file read is in idle state
timeCheckIdle = time.time()     # at every 5 minute the code check that last upload row is incresed or not
LastUploadRowPre =1 #for counting when file read is in idle state
timePrevious=time.time()  #for updating logs for upload data line at every 120 sec

#global variables for today's year month day hour
today   = datetime.today()
year    = str(today.year)
month   = str(today.month)
day     = str(today.day)
hour    =str(today.hour)


try:    
    workingDir=os.getcwd()
    print(workingDir)
    parentDir=os.path.dirname(workingDir)
    #os.chdir(parentDir)
    print(parentDir)
except:
    print("Error in setting parent directory")
    

def setLogFormat():  
    try:
        print("\n*_*_*_checking year date month log format _*_*_* ")
        now     = datetime.now()
        syncTime = now.strftime("%d/%m/%Y")
        dayFilePath=parentDir+'/logs/upload/'+year+'/'+month+'/'+day+'.txt'
        print(dayFilePath)

        try:
            fileExist=os.path.exists(dayFilePath)
            if (not(fileExist)):
                print("making year and month directory")
                path=parentDir+'/logs/upload/'
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
        errlogger.error(e)


try:
   
    setLogFormat()
    path = parentDir+'/logs/upload/'+year+'/'+month+'/'+day+'.txt'
    logging.basicConfig(filename = path,format='%(asctime)s --Line: %(lineno)s--%(levelname)s--%(message)s', filemode = 'a')
    errlogger = logging.getLogger()
    errlogger.setLevel(logging.INFO)
    errlogger.info("set configuration for error log")
    
except Exception as e:
    print(e)
    for i in range(0,4):
        try:
            if os.execl(sys.executable, sys.executable, *sys.argv):
                break
            else:
                print("trying again...")
                os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            print(e)
            errlogger.error(e)

    
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



def updateError():
    try:
        global timePrevious
        if (time.time()-timePrevious)>120:
            errlogger.info("uploadData functon")
           
            timePrevious = time.time()
        else:
            print("time.time()-timePrevious =",time.time()-timePrevious)
    except Exception as e:
        print(e)
        errlogger.error(e)
def checkFileIdle(checkRowNo):
    try:
        global fileIdleCount,timeCheckIdle
        if LastUploadRowPre==checkRowNo:
            if (time.time()-timeCheckIdle)>300:
                fileIdleCount=fileIdleCount+1
                print("fileIdleCount=",fileIdleCount)
                errlogger.info("file idle count = %d",fileIdleCount)
                print("file idle count = ",fileIdleCount)
                if fileIdleCount==12:
                    fileIdleCount=0
                    errlogger.info("file idle count is equel to 200 so restarting code")
                    call(['sudo','reboot'])
                timeCheckIdle = time.time()    
        else:
            fileIdleCount=0
            print("fileIdleCount=",fileIdleCount)
            
    except Exception as e:
        print("Error in checkFileIdle function : ",e)
        errlogger.info("Error in checkFileIdle function : %s",e)
def bypassHour(LastUploadHour):
    try:
        print("Entered in bypassHour ")
        errlogger.info("Entered in bypassHour function")
        bypassHourVal = False
        for i in range(LastUploadHour,24):
            path= path=parentDir+'/records/'+str(LastUploadYear)+'/'+str(LastUploadMonth)+'/'+str(LastUploadDay)+'/'+str(i)+'.csv'
            print(path)
            isFile = os.path.isfile(path)
            if isFile==True:
                print(isFile)     
            else:
                print("file does not exist")
                isFile=False
            bypassHourVal=bypassHourVal or (isFile)
        
        
    except Exception as e:
        print("Error in bypassHour function",e)
        errlogger.error("Error in bypass function : %s",e)
    print("bypassHour val=",bypassHourVal)
    return bypassHourVal
def uploadData():
    try:
        #print("Entered in upload uploadData ")
        global LastUploadRow, LastUploadHour, LastUploadDay, LastUploadMonth, LastUploadYear
        global HOUR_FLAG, DAY_FLAG, YEAR_FLAG, MONTH_FLAG
        
        checkFileIdle(LastUploadRow)
          
        global LastUploadRowPre
        LastUploadRowPre=LastUploadRow                  #it is used to check file read is idle or running
        checkLastUpload(LastUploadRow, LastUploadHour, LastUploadDay, LastUploadMonth, LastUploadYear)
        #----------------for error log --------------#
        updateError()
        #---------------------------------------------------#
        #call read upload to upload the file
        #check if file is available or not
        path=parentDir+'/records/'+str(LastUploadYear)+'/'+str(LastUploadMonth)+'/'+str(LastUploadDay)+'/'+str(LastUploadHour)+'.csv'
        print("path : ",path);
        isFile = os.path.isfile(path)
        uploadFlag=True
        if(isFile==True):
            LastUploadRow,uploadFlag= read_Upload(LastUploadRow,path)    
        else:
            print("No such file or directory")
            errlogger.error("no such file or directory")
        if(uploadFlag==True):
            if(HOUR_FLAG==1):
                if bypassHour(LastUploadHour)==False:
                    LastUploadHour=0
                    LastUploadDay=LastUploadDay+1
                else:
                    LastUploadRow=1
                    LastUploadHour = LastUploadHour +1
                if((LastUploadHour >23 and DAY_FLAG==1) or (LastUploadDay>31)):
                    LastUploadHour= 0
                    LastUploadDay = LastUploadDay+1
                    if(LastUploadDay > 31 and MONTH_FLAG==1):
                        LastUploadDay=1
                        LastUploadMonth = LastUploadMonth+1
                        if(LastUploadMonth > 12 and YEAR_FLAG==1):                
                            LastUploadMonth=1
                            LastUploadYear = LastUploadYear +1   
       
        
        #finaly save the last upload details
        updateRowNum(LastUploadRow, LastUploadHour, LastUploadDay, LastUploadMonth, LastUploadYear)
    except Exception as e:
        print("error in uploadData() :",e)
        errlogger.error("Error in Upload data Function : %s",e)
    return uploadFlag
def checkLastUpload(lastRow, lastHour, lastDay, lastMonth, lastYear):
    try:
        global HOUR_FLAG, DAY_FLAG, MONTH_FLAG, YEAR_FLAG
        today=datetime.today()
        currentYear=int(today.year)
        currentMonth=int(today.month)
        currentDay=int(today.day)
        currentHour =int(today.hour)
        #read last upload row, day, month and year
        #lastRow,lastDay,lastMonth,lastYear=lastUploadRow()
        #compare last upload day, month year with current day month year
        print("checking last flag")
        if (lastYear > currentYear):
            print("Invalid Last Year:",lastYear)
            return False
        elif (lastYear < currentYear):
            YEAR_FLAG  = 1
            MONTH_FLAG = 1
            DAY_FLAG   = 1
            HOUR_FLAG  = 1
        else:
            YEAR_FLAG=0
            if(lastMonth > currentMonth):
                print("Invalid Last Month:",lastMonth)
                return False
            elif (lastMonth<currentMonth):
                MONTH_FLAG = 1
                DAY_FLAG   = 1
                HOUR_FLAG  = 1
            else:
                MONTH_FLAG=0
                if(lastDay>currentDay):
                    print("Invalid lastDay:",lastDay)
                    return False
                elif(lastDay<currentDay):
                    DAY_FLAG  = 1
                    HOUR_FLAG = 1
                else:
                    DAY_FLAG=0
                    if(lastHour>currentHour):
                        print("Invalid lastHour:",lastHour)
                        return False
                    elif(lastHour<currentHour):
                        HOUR_FLAG=1
                    else:
                        HOUR_FLAG = 0
        print("HOUR_FLAG=",HOUR_FLAG)
        print("DAY_FLAG=",DAY_FLAG)
        print("MONTH_FLAG=",MONTH_FLAG)
        print("YEAR_FLAG=",YEAR_FLAG)
        return True
    except Exception as e:
        print("error in checkLastUpload fuction :",e)
        errlogger.error("error in checkLastUpload fuction :%s",e)
           
        
def read_Upload(rowUpload,path):
    #print("Entered in read upload function")
    try:
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        
        print("Row Uploading=",rowUpload)
        with open(path,'r') as file:
            print("Reading")
            data = file.readlines()
            #print("data :",data)
        #print("Data:",data)
        my_list = list(data)
        #print("my List",my_list)
        totalRow = len(my_list)
        print("Total Row=",totalRow)
        failedCount=0       # to count the failed request during upload
        
        uploadStatus=True
        while(rowUpload<totalRow):
            data = my_list[int(rowUpload)]
            #print("data read=",data)
            data = data.split(',')
            LD = data[0:6]
            ID = data[6:]
            ID_data = ''
            LD_Data = LD[0] + ',' + LD[1] + ',' + LD[2] + ',' + LD[3] + ',' + LD[4] + ',' + LD[5]
            LD_Data = LD_Data.replace('\x00','') 
            print("LD_Data",LD_Data)
            for x in ID:
                ID_data = ID_data + x + ','
            ID_data = ID_data[:-1]
            ID_data = ID_data.replace('\x00','')
            print("ID_data",ID_data)
            #print("Type",LD[2])
            deviceType=int(LD[2])
            print('device type:',deviceType)
            if((deviceType>= 1) and (deviceType<255)):
                resp="Response"
                print("uploading")
                paramsdata = {'LD': LD_Data, 'ID': ID_data}
                try:
                    r = requests.get(DATA_URL, headers = headers, params= paramsdata,timeout = 30)
                    print('Response:',r.text)
                    resp=r.text
                except Exception as e:
                    errlogger.error(" Request error : %s",e)
                    print(e)
                    resp="Response"
                    
            
            if resp.find("ConnectedOKOK")>=0:
                print("Data Upload Successful")
                rowUpload=rowUpload+1
                failedCount=0
                uploadStatus=True
                
                
            else:
                failedCount = failedCount+1
                if(failedCount>10):
                    uploadStatus=False
                    print("request failed 10 times")
                    errlogger.error("request failed 10 times")
                    
                    return rowUpload,uploadStatus
                    
                    
            #time.sleep(0.1)             # this time stop the connection port 80 error as time gap between two request
        return rowUpload,uploadStatus
    except Exception as e:
        print("Error in readUpload function : ",e)
        errlogger.error("read_Upload function error : %s ",e)
        

    return rowUpload,uploadStatus            
    
def lastUploadRow():
    print("Checking lastupload row")
    errlogger.info("checking lastupload row")
    try:
        try:
            with open(parentDir+"/records/tracker.txt", 'r') as rowFile:
                data= rowFile.readline()
                rowFile.close()
            if not (data):
                print("Recovery of tracker")
                call(['cp',parentDir+'/backup/tracker.txt',parentDir+'/records/tracker.txt'])
                with open(parentDir+"/records/tracker.txt", 'r') as rowFile:
                    data= rowFile.readline()
                    rowFile.close()
                if(not(data)):
                    print("empty file")
                    errlogger.error("empty tracker file")
                    today   = datetime.today()
                    year    = str(today.year)
                    month   = str(today.month)
                    day     = str(today.day)
                    hour    = str(today.hour)
                    lastUploadRowStr = year+','+month+','+day+','+hour+'1'
                    print(lastUploadRowStr)
                    with open(parentDir+"/records/tracker.txt", 'w') as rowFile:
                        data = lastUploadRowStr
                        print("writing......")
                        rowFile.write(data)
                        rowFile.close()
        except Exception as e:
            print("path nor available ")
            errlogger.error("path not available :%s",e)
            with open(parentDir+"/backup/tracker.txt", 'r') as rowFile:
                data= rowFile.readline()
                rowFile.close()
        
        errlogger.info(data)
        dataSplit=data.split(',')
        print(dataSplit)
        
        rowLast=int(dataSplit[4])
        hourLast=int(dataSplit[3])
        dayLast=int(dataSplit[2])
        monthLast=int(dataSplit[1])
        yearLast=int(dataSplit[0])
        if(yearLast>2022 or yearLast<2000 or monthLast>12 or dayLast>30):
            print("yearLast or monthLast or dayLast or hourLast fault so setting current date")
            errlogger.info("yearLast or monthLast or dayLast or hourLast fault so setting current date")
            today   = datetime.today()
            rowLast=1
            hourLast=today.hour
            dayLast= today.day
            monthLast= today.month
            yearLast= today.year 
            lastUploadRowStr = str(yearLast)+','+str(monthLast)+','+str(dayLast)+','+str(hourLast)+','+str(rowLast)
            print(lastUploadRowStr)
            with open(parentDir+"/records/tracker.txt", 'w') as rowFile:
                data = lastUploadRowStr
                print("writing......")
                rowFile.write(data)
                rowFile.close()
        if(checkLastUpload(rowLast, hourLast, dayLast,monthLast,yearLast)!=True):
            today   = datetime.today()
            rowLast=1
            hourLast=today.hour
            dayLast= today.day
            monthLast= today.month
            yearLast= today.year 
            lastUploadRowStr = str(yearLast)+','+str(monthLast)+','+str(dayLast)+','+str(hourLast)+','+str(rowLast)
            print(lastUploadRowStr)
            with open(parentDir+"/records/tracker.txt", 'w') as rowFile:
                data = lastUploadRowStr
                print("writing......")
                rowFile.write(data)
                rowFile.close()
        
                
    except Exception as e:
        errlogger.error("Last Upload Row function error : %s",e)
        print("Error in last Upload Row :",e)
    return rowLast, hourLast, dayLast, monthLast, yearLast

def updateRowNum(rowUpdate,hourUpdate, dayUpdate,monthUpdate,yearUpdate):
    print("entered in row update function")
    try:
        with open(parentDir+"/records/tracker.txt", 'w') as rowFile:
            #rowFile.write(str(rowUpdate))
            dateUpdate=str(str(yearUpdate)+','+str(monthUpdate)+','+str(dayUpdate)+','+str(hourUpdate)+','+str(rowUpdate))
            print(dateUpdate)
            rowFile.write(str(dateUpdate))
        
        print("Row Updated Successfull")
        return True
        #print("updated row=",row)
        #print("updated Day=",dayUpdate)
        #print("updated Month=",monthUpdate)
        #print("updated Month=",yearUpdate)
        #print("Row ,day,month,Updated")
    except Exception as e:
        print("Error in update row function : ",e)
        errlogger.error("Error in update row function : %s",e)
        return False

def startGSM():
    try:
        print("Entered in startGSM function")
        errlogger.info("Entered in startGSM function")
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        time.sleep(3)
        print("HIGH..")
        GPIO.output(pwrKey,GPIO.HIGH)
        time.sleep(3)
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        print("stated gsm successfully")
        print("wait 20 sec")
        time.sleep(20)
    except Exception as e:
        print("Error in startGSM function : ",e)
        errlogger.error("Error in startGSM function : %s",e)
def checkATResponse():
    try:
        global errorCount
        global flagATResponse
        flagATResponse = False
        print("Entered in checkATResponse")
        errlogger.info("Entered in checkATResponse function")
        # Enable Serial Communication
        call(['sudo','poff','rnet'])
        time.sleep(5)
        with serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2) as port:
            port.write(b'AT'+b'\r\n')
            rcv = port.read(30)
            print(rcv)
            rcvStr = str(rcv, 'UTF-8')
            print(rcvStr)
            if rcvStr.find("OK")>=0:
                print("AT resonse success")
                errorCount=0
                flagATResponse = True
                return flagATResponse
            else:
                errorCount=errorCount+1
                print("errorCount =",errorCount)
                errlogger.info("errorCount : %s",errorCount)
                if errorCount==10:
                    print("Error count is equel to 10")
                    errlogger.info("Error count is equel to 10")
                    flagATResponse =False
                    return flagATResponse
                else:
                    checkATResponse()
    except Exception as e:
        print("Error in checkATResponse function :",e)
        errlogger.error("Error in checkATResponse : %s",e)
        errorCount=errorCount+1
        print("errorCount=",errorCount)
        if errorCount<10:
            checkATResponse()
        else:
            print("Error count is equel to 10")
            errlogger.info("Error count is equel to 10")
            flagATResponse = False
            
            
def resetGSM():
    try:
        print("Entered in resetGSM function")
        errlogger.info(" Entered in resetGSM function")
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        time.sleep(3)
        print("HIGH..")
        GPIO.output(pwrKey,GPIO.HIGH)
        time.sleep(3)
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        print("wait 1 minute..")
        time.sleep(60) # delay of 60 second
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        time.sleep(3)
        print("HIGH..")
        GPIO.output(pwrKey,GPIO.HIGH)
        time.sleep(3)
        print("LOW..")
        GPIO.output(pwrKey,GPIO.LOW)
        print("resetGSM successfully")
        print("wait 1 min..")
    except Exception as e:
        print("Error in resetGSM function :",e)
        errlogger.error("Error in resetGSM function :%s",e)

def gsmData(): 
    # Enable Serial Communication
    print(call(['sudo','poff','rnet']))
    time.sleep(5)
    with serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2) as port:
        print("Entered in gsmData")
        errlogger.info("Entered in gsmData ")
        try:
            port.write(b'AT+CSQ'+b'\r\n')
            rcv = port.read(30)
            b1 = str(rcv, 'UTF-8')  
            #print(b1)
            b1Split = b1.split("+CSQ:")
            #print(b1Split)
            csqDataSplit=b1Split[1].split(",99")
            signalQuality =csqDataSplit[0] 
            #print("signalQuality = ",signalQuality)
        except Exception as e:
            print("signal quality error")
            signalQuality="csqERROR"
        time.sleep(2)    
        try:
            port.write(b'AT+ICCID'+b'\r\n')
            rcv = port.read(50)
            print(rcv)
            b1 = str(rcv, 'UTF-8')  
            #print(b1)
            b1Split = b1.split("+ICCID:")
            #print(b1Split)
            simDataSplit=b1Split[1].split("OK")
            simSerial = simDataSplit[0]
            #print("sim Serial No = ",simSerial)
        except Exception as e:
            print("sim serial error")
            errlogger.error("sim serial error : %s",e)
            simSerial="simSerialERROR"
        time.sleep(2)
        try:
            port.write(b'ATI'+b'\r\n')
            rcv = port.read(120)
            print(rcv)
            b1 = str(rcv, 'UTF-8')  

            #print(b1)
            b1Split = b1.split("IMEI:")
            #print(b1Split)
            gsmIMEIData = b1Split[1]
            gsmIMEISplit = gsmIMEIData.split("+G")
            gsmIMEI = gsmIMEISplit[0]
            #print("GSM IMEI = ",gsmIMEI)
        except Exception as e:
            print("gsm imei error : ",e)
            errlogger.error("gsm IMEI error : %s",e)
            gsmIMEI = "gsmIMEIERROR"
        time.sleep(2)
        try:
            port.write(b'AT+COPS?'+b'\r\n')
            rcv = port.read(120)
            print(rcv)
            b1 = str(rcv, 'UTF-8')  
            #print(b1)
            b1Split = b1.split('"')
            network = b1Split[1]
            #Sprint("network = ",network)
        except Exception as e:
            print("network error")
            errlogger.error("network error : %s",e)
            network = "networkERROR"
        port.flush()
    return signalQuality, simSerial, gsmIMEI, network

def manufacProfile():
    global errorCount
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
        
        errorCount = 0
        
    except Exception as e:
        print("Error in manufacProfileFunction :",e)
        errlogger.error("Error in manufacProfileFunction : %s",e)
        #global countConfig
        time.sleep(10)
        errorCount=errorCount+1
        
        if errorCount<=5:
            print("countConfig :: ",countConfig)
            manufacProfile()
            errlogger.info("countConfig =%d --calling itself",countConfig)
            time.sleep(2)
           
        elif errorCount>5 and errorCount<=10:
            print("errorCount is greaer than 5 and less than 11 so restaring code")
            errlogger.info("errorCount is greaer than 5 and less than 11 so restaring code")
            for i in range(0,4):
                try:
                    print(i)
                    time.sleep(2)
                    if os.execl(sys.executable, sys.executable, *sys.argv):
                        break
                    else:
                        print("retrying again...")
                        errlogger.info("retrying again...")
                        os.execl(sys.executable, sys.executable, *sys.argv)
                except Exception as e:
                    errlogger.error(e)
                    manufacProfile()
    return serialNo

def sendRestartData(signalQuality, simSerial, gsmIMEI, network):
    try:
        print("Entered in sendRestartData")
        errlogger.info("sending restart data")
        global errorCount
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        serialNo=manufacProfile()
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/logger.ini')
            if(len(config.sections()) == 0):
                print("logger Config File is empty")
                call(['cp','parentDir/backup/logger.ini',parentDIr+'/config/logger.ini'])
                config.read(parentDir+'/config/logger.ini')
            loggerProfile = config['loggerProfile']
            #configStatus=loggerProfile['configStatus']
            #print("configStatus=",configStatus)
            plantId=loggerProfile['plantId']
            #print("plantId=",plantId)
            loggerId=loggerProfile['loggerId']
            #print("loggerId=",loggerId)
            deviceCount=loggerProfile['deviceCount']
            #print("deviceCount=",deviceCount)
        except Exception as e:
            print("path does not exists :",e)
            errlogger.error("path does not exists : ",e)
            config.read(parentDir+'/backup/logger.ini')
       
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        LD_Data =str(loggerId)+','+str(plantId)+','+'0,0,2,0'+time_stamp
        ID_Data =str(serialNo)+','+str(deviceCount)
        bufferData = LD_Data + ID_Data
        paramsadata = {'LD': LD_Data, 'ID': ID_Data}
        r = requests.get(DATA_URL, headers = headers, params= paramsadata,timeout = 10)

        print("Response:",r.text)
        resp=r.text
        if(resp.find("ConnectedOKOK")>=0):
            print("Data Upload Successful")
            errlogger.info("DataUpload Successful")
        errorCount=0
    except Exception as e:
        print("Error in sendRestartData function : ",e)
        errlogger.error("Error in sendRestarData function : %s",e)
        
        errorCount=errorCount+1
        print("errorCount=",errorCount)
        time.sleep(5)
        if errorCount<=5:
            print("calling itself ",errorCount)
            errlogger.info("calling itself %s",errorCount)
            sendRestartData(signalQuality, simSerial, gsmIMEI, network)
        else:
            try:
                errlogger.info("writing restartData in record file")
                pathRecord = parentDir+'/records/'+year+'/'+month+'/'+day+'.txt'
                with open(pathRecord,'a') as file:
                    file.write(bufferData)
                    errlogger.info("appended in record file")
            except Exception as e:
                print(e)
                errlogger.error(e)
def sendRestartData():
    try:
        print("Entered in sendRestartData")
        errlogger.info("sending restart data")
        global errorCount
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        serialNo=manufacProfile()
        config = configparser.ConfigParser()
        try:
            config.read(parentDir+'/config/logger.ini')
            if(len(config.sections()) == 0):
                print("logger Config File is empty")
                call(['cp','parentDir/backup/logger.ini',parentDIr+'/config/logger.ini'])
                config.read(parentDir+'/config/logger.ini')
            loggerProfile = config['loggerProfile']
            #configStatus=loggerProfile['configStatus']
            #print("configStatus=",configStatus)
            plantId=loggerProfile['plantId']
            #print("plantId=",plantId)
            loggerId=loggerProfile['loggerId']
            #print("loggerId=",loggerId)
            deviceCount=loggerProfile['deviceCount']
            #print("deviceCount=",deviceCount)
        except Exception as e:
            print("path does not exists :",e)
            errlogger.error("path does not exists : ",e)
            config.read(parentDir+'/backup/logger.ini')
       
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        LD_Data =str(loggerId)+','+str(plantId)+','+'0,0,2,0'+time_stamp
        ID_Data =str(serialNo)+','+str(deviceCount)
        bufferData = LD_Data + ID_Data
        paramsadata = {'LD': LD_Data, 'ID': ID_Data}
        r = requests.get(DATA_URL, headers = headers, params= paramsadata,timeout = 10)

        print("Response:",r.text)
        resp=r.text
        if(resp.find("ConnectedOKOK")>=0):
            print("Data Upload Successful")
            errlogger.info("DataUpload Successful")
        errorCount=0
    except Exception as e:
        print("Error in sendRestartData function : ",e)
        errlogger.error("Error in sendRestarData function : %s",e)
        
        errorCount=errorCount+1
        print("errorCount=",errorCount)
        time.sleep(5)
        if errorCount<=5:
            print("calling itself ",errorCount)
            errlogger.info("calling itself %s",errorCount)
            sendRestartData(signalQuality, simSerial, gsmIMEI, network)
        else:
            try:
                errlogger.info("writing restartData in record file")
                pathRecord = parentDir+'/records/'+year+'/'+month+'/'+day+'.txt'
                with open(pathRecord,'a') as file:
                    file.write(bufferData)
                    errlogger.info("appended in record file")
            except Exception as e:
                print(e)
                errlogger.error(e)

def syncTime():
    try:
        global errorCount
        print("Entered in syncTime function")
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        params=''
        r = requests.get(TIME_URL, headers = headers, params= params,timeout = 10)
        print('Response:',r.text)
        call(["sudo","date","-s",r.text])
        #call(["sudo","date","-s","2021-01-11  06:04:11 "])
        errorCount=0
    except Exception as e:
        print("Error in syncTime function : ",e)
        errlogger.error("Error in syncTime function : %s ",e)
        
        errorCount=errorCount+1
        time.sleep(5)
        if errorCount<=4:
            errlogger.info("calling itself %s",errorCount)
            syncTime()
            
     
def gsmOFF():
    try:
        print("\n gsmOFF function")
        errlogger.info("gsmOFF function")
        print(call(['sudo','poff','rnet']))
        time.sleep(3)
        port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)
        port.write(b'AT+CPOF'+b'\r\n')
        rcv = port.read(50)
        errlogger.info("%s",rcv)
        print (rcv)
        time.sleep(60)
    except Exception as e:
        print("gsmOFF error :",e)
        errlogger.error("gsmOFF error : %s",e)

    

def main():
    global errorCount
    try:
        errlogger.info("Restart main")
        
        uploadInterval = 10
        if isGSM==1:
            checkATResponse()
            if flagATResponse==False:
                startGSM()
                errorCount = 0
                checkATResponse()
        else:
            print("GSM not available")
##        signalQuality, simSerial, gsmIMEI, network = gsmData()
##        print("signal Quality = ",signalQuality)
##        print("sim Serial = ",simSerial)
##        print("gsm IMEI",gsmIMEI)
##        print("network = ",network)
        statusFlag = False
        conn = False
        count = 0
        #read last upload data from file
        global LastUploadRow,LastUploadHour, LastUploadDay,LastUploadMonth,LastUploadYear
        LastUploadRow,LastUploadHour, LastUploadDay,LastUploadMonth,LastUploadYear=lastUploadRow()
        
        call(["sudo", "pon","rnet"])
        time.sleep(10)
        conn = internet_on()
        lastTime = time.time()    
        
        if(conn==True):
            print("Internet is OK")            
            statusFlag=True
            lastTime = time.time()
            #sendRestartData(signalQuality, simSerial, gsmIMEI, network)
            sendRestartData()
            syncTime()
        else:
            flagRestartReq = 1      #this flag is used to resend restart req again if internet is not available
        timeReboot = time.time()
        countFalse=0   # This local variable is used to count the failed internet connections
        countgsmOFF=0   #this local variable is used to count how many time gsm off is called
        while True:
            #print("Connection = {}, StatusUpload = {}".format(conn,statusFlag))
            if(((time.time() - lastTime) > uploadInterval)):
                lastTime=time.time()
                if(conn==True and statusFlag ==True):  
                    print("Uploading.........")
                    statusFlag = uploadData()
                    if(statusFlag==False):
                        errlogger.error("statusFlag : %s",statusFlag)
                        timeReboot = time.time()
                        conn=internet_on()
                        errlogger.error(" now internet connection : %s ",conn)
                        if conn==True:
                            statusFlag = True        
                       
                if(conn == False):
                    if ((time.time()-timeReboot)>3600):
                        print("Rebooting device due to internet failure")
                        errlogger.info("Rebooting device due to internet failure")
                        call(['sudo','reboot'])
                    print(call(["sudo", "poff","rnet"]))
                    time.sleep(5)
                    print("Restart internet ")
                    errlogger.info("Restart internet")
                    print(call(["sudo", "pon","rnet"]))
                    time.sleep(10)
                    conn = internet_on()
                    if(conn == True):
                        print("Internet Running")
                        errlogger.error("internet running")
                        if flagRestartReq==1:
                            print("sending restart again")
                            sendRestartData()
                            flagRestartReq = 0
                        statusFlag = True
                        countFalse = 0
                    countFalse=countFalse+1
                    print("countFalse = ",countFalse)
                    if countFalse==10:
                        countgsmOFF=countgsmOFF+1
                        print("countgsmOFF=",countgsmOFF)
                        errlogger.info("countgsmOFF : %s",countgsmOFF)
                        if isGSM==1:
                            if countgsmOFF==15:
                                countFalse=0
                                print("countgsmOFF is equel to 15 so calling resetGSM")
                                errlogger.info("countgsmOFF is equel to 15 so calling resetGSM")
                                countgsmOFF=0
                                resetGSM()
                                checkATResponse()
                                if flagATResponse==False:
                                    startGSM()
                                    errorCount=0
                                    checkATResponse()
                                countgsmOFF=0
                            
                           
                                
            errorCount=0
    except Exception as e:
        errlogger.error("Error in main function")
        main()

if __name__ == '__main__':
    main()
