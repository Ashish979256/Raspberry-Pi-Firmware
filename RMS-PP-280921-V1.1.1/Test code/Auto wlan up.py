import socket
import requests
import urllib.request
import time
from subprocess import call


SERVER_URL='http://www.holmiumtechnologies.com'
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
print("calling wlan down.....")
print(call(['sudo','ifconfig','wlan0','down']))

time.sleep(20)
for i in range(0,4):
    flagCheckNet = internet_on()
    print("internet status = ",flagCheckNet)
    time.sleep(5)
if(flagCheckNet == False):
        print(call(['sudo','ifconfig','wlan0','up']))
else:
    print("net running using GSM")
