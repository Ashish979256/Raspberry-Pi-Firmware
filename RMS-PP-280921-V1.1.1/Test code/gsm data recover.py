import serial   
import os, time

def gsmData(): 
# Enable Serial Communication
    port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=2)

    try:
        port.write(b'AT+CSQ'+b'\r\n')
        rcv = port.read(30)
        b1 = str(rcv, 'UTF-8')  
        print(b1)
        b1Split = b1.split("+CSQ:")
        print(b1Split)
        csqDataSplit=b1Split[1].split(",99")
        signalQuality =csqDataSplit[0] 
        print("signalQuality = ",signalQuality)
    except Exception as e:
        print("signal quality error")
        signalQuality="ERROR"
        
    try:
        port.write(b'AT+ICCID'+b'\r\n')
        rcv = port.read(50)
        print(rcv)
        b1 = str(rcv, 'UTF-8')  
        print(b1)
        b1Split = b1.split("+ICCID:")
        print(b1Split)
        simDataSplit=b1Split[1].split("OK")
        simSerial = simDataSplit[0]
        print("sim Serial No = ",simSerial)
    except Exception as e:
        print("sim serial error")
        simSerial="ERROR"
        
    try:
        port.write(b'ATI'+b'\r\n')
        rcv = port.read(120)
        print(rcv)
        b1 = str(rcv, 'UTF-8')  
        print(b1)
        b1Split = b1.split("IMEI:")
        print(b1Split)
        gsmIMEIData = b1Split[1]
        gsmIMEISplit = gsmIMEIData.split("+G")
        gsmIMEI = gsmIMEISplit[0]
        print("GSM IMEI = ",gsmIMEI)
    except Exception as e:
        print("gsm imei error")
        gsmIMEI = "gsmIMEI"
    try:
        port.write(b'AT+COPS?'+b'\r\n')
        rcv = port.read(120)
        print(rcv)
        b1 = str(rcv, 'UTF-8')  
        print(b1)
        b1Split = b1.split('"')
        network = b1Split[1]
        print("network = ",network)
    except Exception as e:
        print("network error")
        network = "ERROR"
    return signalQuality, simSerial, gsmIMEI, network
signalQuality, simSerial, gsmIMEI, network = gsmData()
print("signal Quality = ",signalQuality)
print("sim Serial = ",simSerial)
print("gsm IMEI",gsmIMEI)
print("network = ",network)
