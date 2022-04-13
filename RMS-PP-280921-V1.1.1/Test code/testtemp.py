import math
def temp(vo):
    rth=((3.33/vo)-1)*4990
    #print("rth{}",format(rth))
    y1=(23410.77*(math.log(rth)))
    #print("y1=")
    #print(y1)
    y2=(8.7754688*pow(math.log(rth),3))
    #print("y2=")
    #print(y2)
    y=112924.1+y1+y2
    temp=((pow(10,8)/y)-1)-273.13
    temp=round(temp,2)
    #print("temperature is =",format(temp))
    return temp   
temperature=temp(1.18)
print('temp:',temperature)
