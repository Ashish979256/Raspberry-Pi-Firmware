from subprocess import *
import time 
def checkFileOpen():
    try:
        responseServer = run(["pgrep","-x","server.sh"])
        print("responseServer = ",responseServer)
        responseUpload = run(["pgrep","-x","upload.sh"])
        print("responseUpload = ",responseUpload)
        responseFile = run(["pgrep","-x","file.sh"])
        print("responseFile = ",responseFile)
        
        if not(responseFile.returncode==0):
            print("opening file_read file.....")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/file.sh', shell =True))
        else:
            print("file_read is open")
        time.sleep(4)
        if not(responseServer.returncode==0):
            print("opening server file...")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/server.sh', shell =True))
        else:
            print("server file is open")
        time.sleep(4)
        
        if not(responseUpload.returncode==0):
            print("opening upload file...")
            print(call('lxterminal -e /home/pi/Desktop/Firmware_datalogger_V1.8/exe/upload.sh', shell =True))
            
        else:
            print("upload file is open")
    except Exception as e:
        print("checkFileOpen function error")
        print(e)

checkFileOpen()
