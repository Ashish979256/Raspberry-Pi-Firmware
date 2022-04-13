import socket
import requests
import urllib.request
import time
from subprocess import call
CONFIG_URL='http://www.holmiumtechnologies.com/rms/api/configuration/sync'
def checkConfiguration(serialNo):
    try:
        print("\nChecking Server Configuration\n")
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
                flagNormal = True
            elif (resp.find("EXTENDED")>=0):
                flagExtended = True
            
        except Exception as e:
            print(e)       
       
        
    except Exception as e:
        print("error check configuration :",e)
        errlogger.error("checkConfiguration function error")
        errlogger.error(e)
    
serialNo='HO-K301506'
while(1):
    checkConfiguration(serialNo)
    time.sleep(5)
