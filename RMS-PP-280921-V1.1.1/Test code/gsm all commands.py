import socket
import requests
import urllib.request
import serial   
import os, time
from subprocess import call

SERVER_URL='http://www.holmiumtechnologies.com'
call(['sudo','poff','rnet'])
# Enable Serial Communication
port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
 
# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key
def reset():
    
    print("Reset the module")
    port.write(b'AT+CRESET'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

def gsm_response():
     
    port.write(b'AT'+b'\r\n')
    rcv = port.read(40)
    print (rcv)
    port.flush()

def module_detail():
    print("\nmanufacturer:")
    port.write(b'ATI'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

    print("\nIMEI no of device")
    port.write(b'AT+GSN'+b'\r\n')
    rcv = port.read(70)
    print (rcv)
    port.flush()

def sim_detail():
    print("\nnetwork operator")
    port.write(b'AT+COPS?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

    print("check sim is unlocked and active")
    port.write(b'AT+CPIN?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

    
     
    
    
def network_reg():
    print("if response is 0,1 then network is registered at Home Network")
    port.write(b'AT+CREG?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

def signal_quality():
    print("2-9\tmarginal network")
    print("10-14\tOK network")
    print("15-19\tGood network")
    print("20-30\tExcellent network")
    
    port.write(b'AT+CSQ'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

        

def gprs_network_reg():
    print("if response is 0,1 then gprs network is registered at Home Network")
    port.write(b'AT+CGREG?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()
     
    
def read_msg():
     
    
    print("Read all messages\n")

    
    print("\n set into textmode for message")
    port.write(b'AT+CMGF=1'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

    print("\n read simcard's all messages")
    port.write(b'AT+CMGL="ALL"'+b'\r\n')
    rcv = port.read(8000)
    print (rcv)
    port.flush()

    print("\n read simcard's all messages")
    port.write(b'AT+CMGL="ALL"'+b'\r\n')
    rcv = port.read(8000)
    print (rcv)
    port.flush()

def en_err_report():
    print("\n1. Nemeric code error reporting\n")
    print("2. verbode error reporting\n")
    print("3. exit\n")
    
    number=int(input("Enter a number:-"))
    if number==1:
        port.write(b'AT+CMEE=1'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
        en_err_report()
    if number==2:
        port.write(b'AT+CMEE=2'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
        en_err_report()
    if number==3:
        menu()
            
    
def apn():
    print("check apn or pdp(packet to data protocol) context")
    port.write(b'AT+CGDCONT?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

    print("check Baud rate")
    port.write(b'AT+IPR?'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()

def internet_on():
    print("\t\t choose an option\n")
    print("1. internet on command \n 2. internet off command\n3. net status\n4. exit")
    number=int(input("Enter a number : "))
    if(number==1):
        try:
            call(["sudo","pon","rnet"])
        except Exception as e:
            print("command error : " ,e)
        internet_on()
    if(number==2):
            try:
                call(["sudo","pon","rnet"])
            except Exception as e:
                print("command error : " ,e)
            internet_on()
    if(number==3):
        try:
            response = urllib.request.urlopen(SERVER_URL,timeout = 10)
            print("success")
        except urllib.request.URLError as err: pass
        except Exception as e:
            errlogger.error(e)
            print("failed : ",e)
        internet_on()
    if(number==4):
        menu()
def mobileEquipError():
    print("check error ")
    port.write(b'AT+CEER'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()
def simOnlineOffline():
    print("check phoen online or offline")
    print("1. check current status \n 2. full functionality ONLINE mode\n3. least functionality OFFLINE mode\n4. airoplane mode\n5. exit")
    number=int(input("Enter a number : "))
    if(number==1):
        print("check error ")
        port.write(b'AT+CFUN?'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
        print("if 0 means OFFLINE Mode\n if 1 means ONLINE Mode \n if 4 airoplane Mode ")
        simOnlineOffline()
    if(number==2):
        print("Run phone at full functionality online mode ")
        port.write(b'AT+CFUN=1'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
        
        simOnlineOffline()
    if(number==3):
        print("Run phone at least functionality offline mode ")
        port.write(b'AT+CFUN=0'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
    if(number==4):
        print("Run phone in airoplane mode it disable Rx Tx from the modem still we get AT command response ")
        port.write(b'AT+CFUN=4'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
        print("after this sun online mode otherwise sim card will not work")        
        simOnlineOffline()
    if(number==5):
        menu()
def powerOff():
    print("power off module after this command modem will restart in 20 sec")
    port.write(b'AT+CPOF'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()
def USSD():
    print("check USSD code *199# for vodafone")
    port.write(b'AT+CMGF=1'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()
    port.write(b'AT+CSCS="GSM"'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    port.flush()
    print("enter 222 to go to main menu")
    x=str(input("enter USSD code"))
    #print("x",x)
    if x=='222':
        menu()
    byte1 = bytes(x, encoding='utf-8')
    #print(byte1)
    #print(type(byte1))
    port.write(b'AT+CUSD=1,"'+byte1+b'",15'+b'\r\n')
    rcv = port.read(2000)
    print (rcv)
    rcv = port.read(2000)
    print (rcv)
    port.flush()
    
    y=1111
    while(not(y==111)):
        if not(y==1111):
           
            y=str(y)
            byte2 = bytes(y, encoding='utf-8')
            port.write(b'AT+CUSD=1,"'+byte2+b'",15'+b'\r\n')
            rcv = port.read(2000)
            print (rcv)
            rcv = port.read(2000)
            print (rcv)
            port.flush()
        print("enter 111 to go USSD function")
        print("enter222 to go to main menu")
        #print (rcv)
        y=int(input("enter your choise"))
        if y==111:
            USSD()
        if y==222:
            menu()
def setAPN():
    try:
        print("it set  APN set the apn of the modem\n")
        apn=input("Enter apn : ")
        apnByte = bytes(apn, encoding='utf-8')
        port.write(b'AT+CGDCONT=1,"IP","'+apnByte+b'","0.0.0.0",0,0,0,0'+b'\r\n')
        rcv = port.read(200)
        print (rcv)
        port.flush()
    except Exception as e:
        print("Error in set APN ",e)
def checkAPN():
    try:
        print("it checks apn of the modem\n")
        port.write(b'AT+CGDCONT?'+b'\r\n')
        rcv = port.read(2000)
        print (rcv)
        port.flush()
    except Exception as e:
        print("Error in set APN ",e)

def menu():
    print("\t\t\t choose an option\n\n")
    print("1. Check GSM response\t\t2. Module details\t\t3. Sim details\n")

    print("4. Check Signal Quality\t\t5. Read Messages\t\t6.  Reset GSM\n")

    print("7. Network Reg Status\t\t8. GPRS registration Status\t9. APN &Baud rate \n")
    print("10. enable error reporting\t11. internet on \t 12. Mobile Eqipment error \n ")
    print("13. SIM online/offline/mode \t 14. Power OFF Modem \t15. USSD code\n")
    print("16. Set APN \t 17. check APN")
    number=int(input("Enter a number:-"))
    if number==1:
        gsm_response()
        menu()
    if number==2:
        module_detail()
        menu()
    if number==3:
        sim_detail()
        menu()
    if number==4:
        signal_quality()
        menu()
    if number==5:
        read_msg()
        menu()
    if number==6:
        reset()
        menu()
    if number==7:
        
        network_reg()
        menu()
    if number==8:
        gprs_network_reg()
        menu()
    if number==9:
        apn()
        menu()
    if number==10:
        en_err_report()
        menu()
    if number==11:
        internet_on()
        menu()
    if number==12:
        mobileEquipError()
        menu()
    if number==13:
        simOnlineOffline()
        menu()
    if number==14:
        powerOff()
        menu()
    if number==15:
        USSD()
        menu()
    if number==16:
        setAPN()
        menu()
    if number==17:
        checkAPN()
        menu()


if __name__=='__main__':
    try:
        
        menu()
    except Exception as e:
        print(e)
        
    
    
