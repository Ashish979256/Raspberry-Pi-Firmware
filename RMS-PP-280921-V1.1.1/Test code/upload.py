import socket
import requests
import urllib.request
import time
from subprocess import call
import logging
from datetime import datetime
import os
import configparser


TIME_URL='http://13.234.86.197/rms/api/timestamp/sync'
DATA_URL='http://13.234.86.197/rms/api/insertdata?'
SERVER_URL='http://www.holmiumtechnologies.com'
YEAR_FLAG=0
MONTH_FLAG=0
DAY_FLAG=0
try:    
    workingDir=os.getcwd()
    print(workingDir)
    parentDir=os.path.dirname(workingDir)
    #os.chdir(parentDir)
    print(parentDir)
except:
    print("Error in setting parent directory")

logging.basicConfig(filename = parentDir+"/logs/error_upload.log",format='%(asctime)s %(message)s', filemode = 'a')
errlogger = logging.getLogger()
errlogger.setLevel(logging.ERROR)


def manufacProfile():
    try:
        config = configparser.ConfigParser()
        config.read('../config/manufacture.ini')
        if(len(config.sections()) == 0):
            print("manufacture Config File is empty")
            call(['cp','../backup/manufacture.ini','../config/manufacture.ini'])
            config.read('../config/manufacture.ini')
        manufacProfile = config['manufacture']
        serialNo=manufacProfile['serialNo']
        
        firmwareVersion=manufacProfile['firmwareVersion']
        
        
        return serialNo
    except Exception as e:
        print("error in manufac config",e)
    
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

def syncTime():
    try:
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        paramsadata = ""
        r = requests.get(TIME_URL, headers = headers, params= paramsadata,timeout = 10)
        date_time=r.text
        print(date_time)
        print(call(["sudo", "date","-s",date_time]))
    except Exception as e:
        errlogger.error(e)
        
def uploadData():
    try:
        #read current time
        today=datetime.today()
        currentYear=int(today.year)
        currentMonth=int(today.month)
        currentDay=int(today.day)
        #read last upload row, day, month and year
        lastRow,lastDay,lastMonth,lastYear=lastUploadRow()
        #compare last upload day, month year with current day month year
        #If lastYear<currentYear then set yearFlag , monthFlag, dayFlag to HIGH
        #If lasyYear==currentYear the reset yearFlag LOW
        #If lastYear>CurrentYear then return with None and print invalid lastYear
        
        #If yearFlag==LOW
        #If lastMonth> currentMonth return with invalid month in last upload
        #If lastMonth==currentMonth then reset month flag LOW
        #If lastMonth<currentMonth then set monthFlag,dayFlag to HIGH

        #If monthFlag==LOW
        #If lastDay> currentDay return with invalid day in last upload
        #If lastDay==currentDay then reset dayFlag with LOW
        #If lastDay<currentDay then set Day Flag
        print("checking last flag")
        if (lastYear > currentYear):
            print("Invalid Last Year:",lastYear)
            return
        elif (lastYear < currentYear):
            YEAR_FLAG  = 1
            MONTH_FLAG = 1
            DAY_FLAG   = 1
        else:
            YEAR_FLAG=0
            if(lastMonth > currentMonth):
                print("Invalid Last Month:",lastMonth)
                return
            elif (lastMonth<currentMonth):
                MONTH_FLAG = 1
                DAY_FLAG   = 1
            else:
                MONTH_FLAG=0
                if(lastDay>currentDay):
                    print("Invalid lastDay:",lastDay)
                    return
                elif(lastDay<currentDay):
                    DAY_FLAG=1
                else:
                    DAY_FLAG=0
        #call read upload to upload the file
        #check if file is available or not
        path=parentDir+'/records/'+str(lastYear)+'/'+str(lastMonth)+'/'+str(lastDay)+'.csv'
        isFile = os.path.isfile(path)
        if(isFile==True):
            lastRow,uploadFlag= read_Upload(lastRow,path)    
        else:
            print("No such file or directory")
            uploadFlag=True

        #if readUpload()==true then update the last upload variables
        #if dayFlag==HIGH then increase lastDay by 1
        #if lastDay>31 then reset to lastDay to 1 and
        #If monthFlag==HIGH then increase lastMonth by 1 and
        #If lastMonth>12 and yearFlag is HIGH then reset lastMonth to 1 and increase lastYear by1
        #return to main()
        if(uploadFlag==True):
            if(DAY_FLAG==1):
                lastRow=1
                lastDay = lastDay+1
                if(lastDay > 31 and MONTH_FLAG==1):            
                    lastDay=1
                    lastMonth = lastMonth+1
                    if(lastMonth > 12 and YEAR_FLAG==1):                
                        lastMonth=1
                        lastYear = lastYear +1

        #finaly save the last upload details
        updateRowNum(lastRow,lastDay,lastMonth,lastYear)
    except Exception as e:
        print("error :",e)
    return uploadFlag
def read_Upload(rowUpload,path):
    #print("Entered in read upload function")
    try:
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        #print(rowUp)
        #print(dayUp)
        #print(monthUp)
        #print(yearUp)
        #path=str(str(parentDir)+'/records/'+str(yearUpload)+'/'+str(monthUpload)+'/'+str(dayUpload)+'.csv')
        #print(path)
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
        failedCount=0
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
                print("uploading")
                paramsadata = {'LD': LD_Data, 'ID': ID_data}
                try:
                    r = requests.get(DATA_URL, headers = headers, params= paramsadata,timeout = 30)
                except Exception as e:
                    errlogger.error(e)
                    print(e)            
            print('Response:',r.text)
            resp=r.text
            if(resp.find("ConnectedOKOK")>=0):
                print("Data Upload Successful")
                rowUpload=rowUpload+1
                failedCount=0
                uploadStatus=True
                #return True
            else:
                failedCount = failedCount+1
                if(failedCount>10):
                    uploadStatus=False
                    return rowUpload,uploadStatus
                    print("upload failed")
                    #return False
                  
    except Exception as e:
        errlogger.error(e)        
        print(errlogger.error(e))
    return rowUpload,uploadStatus
      
def lastUploadRow():
    print("Checking lastupload row")
    try:
        with open(parentDir+"/records/LastUploadRow.txt", 'r') as rowFile:
            data= rowFile.readline()
        if not (data):
            print("Recovery of LastUploadRow")
            call(['cp',parentDir+'/backup/LastUploadRow.txt',parentDir+'/records/LastUploadRow.txt'])
            with open(parentDir+"/records/LastUploadRow.txt", 'r') as rowFile:
                data= rowFile.readline()
            
        dataSplit=data.split(',')
        print(dataSplit)
        rowLast=int(dataSplit[0])        
        dayLast=int(dataSplit[1])
        monthLast=int(dataSplit[2])
        yearLast=int(dataSplit[3])
        rowFile.close()
        return rowLast,dayLast,monthLast,yearLast
                
    except Exception as e:
        errlogger.error(e)
        print("Error in last Upload Row")


def updateRowNum(rowUpdate,dayUpdate,monthUpdate,yearUpdate):
    print("entered in row update function")
    try:
        with open(parentDir+"/records/LastUploadRow.txt", 'w') as rowFile:
            #rowFile.write(str(rowUpdate))
            dateUpdate=str(str(rowUpdate)+','+str(dayUpdate)+','+str(monthUpdate)+','+str(yearUpdate))
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
        print("Error in update row function")
        errlogger.error(e)
        return False


def sendRestartData():
    print("Sending Restart data")
    try:
        serialNo=manufacProfile()
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        try:
            config = configparser.ConfigParser()
            config.read('../config/logger.ini')
            if(len(config.sections()) == 0):
                print("logger Config File is empty")
                call(['cp','../backup/logger.ini','../config/logger.ini'])
                config.read('../config/logger.ini')
            loggerProfile = config['loggerProfile']
            #configStatus=loggerProfile['configStatus']
            #print("configStatus=",configStatus)
            plantId=loggerProfile['plantId']
            #print("plantId=",plantId)
            loggerId=loggerProfile['loggerId']
            #print("loggerId=",loggerId)
            deviceCount=loggerProfile['deviceCount']
            #print("deviceCount=",deviceCount)
            readInterval=loggerProfile['readInterval']
            #print("readInterval=",readInterval)
            
            
        except Exception as e:
            print("error in logger profile :",e)

        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        LD_Data =str(loggerId)+','+str(plantId)+','+'0,0,2,0'+time_stamp
        ID_Data =str(serialNo)+','+str(deviceCount)
        paramsadata = {'LD': LD_Data, 'ID': ID_Data}
        r = requests.get(DATA_URL, headers = headers, params= paramsadata,timeout = 10)

        print("Response:",r.text)
        resp=r.text
        if(resp.find("ConnectedOKOK")>=0):
            print("Data Upload Successful")
        
    except Exception as e:
        print(e)
        errlogger.error(e)
    
def timestamp():
     headers = {'User-Agent': 'Chrome/50.0.2661.102'}
     params=''
     r = requests.get(TIME_URL, headers = headers, params= params,timeout = 10)
     print('Response:',r.text)
     call(["sudo","date","-s",r.text])
     #call(["sudo","date","-s","2021-01-11  06:04:11 "])
     


def main():
    try:
        sendRestartData()
        try:
            timestamp()
        except Exception as e:
            print("timeStamp error =",e)
        with open(parentDir+"/config/upload_config.txt", 'r') as config:
            config_data = config.readline()
        if not (config_data):
            call(['cp', parentDir+'backup/upload_config.txt',parentDir+'/config/upload_config.txt'])
            with open(parentDir+"/config/upload_config.txt", 'r') as config:
                config_data = config.readline()
                
        config_data = config_data.split(',')
        uploadInterval = int(config_data[0])
        print("Upload Interval: ",uploadInterval)

        statusFlag = True
        count = 0
        #call(["sudo", "pon","rnet"])
        time.sleep(1)
        print("Internet is OK")
        conn = internet_on()
        lastTime = time.time()
        if(conn==True):
            print("Internet is OK")
            rowLast,dayLast,monthLast,yearLast=lastUploadRow()
            statusFlag=True
            lastTime = time.time()        
        while True:
            #print("Connection = {}, StatusUpload = {}".format(conn,statusFlag))
            if(conn==True and statusFlag ==True):
                if(((time.time() - lastTime) > uploadInterval)):
                    lastTime=time.time()
                    print("inside loop")
                    statusFlag = uploadData()
                    if(statusFlag==False):
                        conn=False
            if(conn == False):
                call(["sudo", "poff","rnet"])
                time.sleep(5)
                print("Restart internet ")
                call(["sudo", "pon","rnet"])
                time.sleep(5)
                conn = internet_on()
                if(conn == True):
                    print("Internet Running")
                    statusFlag = True
    except Exception as e:
        errlogger.error(e)
        print(e)
        #main()

if __name__ == '__main__':
    main()
