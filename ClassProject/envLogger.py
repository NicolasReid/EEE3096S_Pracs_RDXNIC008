#!/usr/bin/python3
# Invrioment logger to record:
#                             - Temprature
#                             - Light
#                             - Humidity (Right now it is just an output form a pot)

# HYSMAT002, RDXNIC008
# October 2019


# Imports
import spidev            # for SPI
import RPi.GPIO as GPIO  # for GPIO
import time              # for time --> remove when rtc is working
import threading         # for threads

#---------------------------Global Variables----------------------------

IsGPIO = False
IsSPI = False

delay = 5

# For ADC SPI
firstByte = int('00000001',2)
humidityByte = int('10000000',2)
lightByte = int('10010000',2)
tempByte = int('10100000',2)
lastByte = int('00000000',2)
adc = spidev.SpiDev()

# For time
sysHours = 0
sysMin = 0
sysSec = 0
Data = ["00:00:00",0,0,0]

# For threads
threads = []

# For temperatuer
Tc  = 0.01 #Volts/(degrees Celcius)
V_0 = 0.5  #Volts

Vout = 0
#----------------------------functions----------------------------------
def init():

    # init Gpio
    GPIO.setmode(GPIO.BCM)
    # outputs
    #GPIO.setup(chipSelectPins, GPIO.OUT)
    #GPIO.output(chipSelectPins, 1) # set chip select pins hight because communication starts on a logic low.

    # init SPI    adc = spidev.SpiDev()
    adc.open(0,0)
    IsSPI = True
    # Set up threads
    dataThread = threading.Thread(target = dataThreadFunction)
    mainThread = threading.Thread(target = mainThreadFunction)
    DACThread = threading.Thread(target = DACThreadFunction)
    threads.append(mainThread)
    threads.append(dataThread)
    threads.append(DACThread)

def mainThreadFunction():
    global Vout
    while(1):
       print('|{:^10}|{:^11}|   {:1.1f}V   |  {:2.0f}°C  |  {:^4.0f} |  {:1.2f}V  |   {}   |'.format("00:00:00", Data[0], Data[1], Data[2],Data[3],Vout," "))
       time.sleep(delay)

def dataThreadFunction():
    global sysSec
    while(1):
        getADCData()
        sysSec += 1
        sysTime = '{:02d}:{:02d}:{:02d}'.format(sysHours,sysMin,int(sysSec))
        Data[0] = sysTime
        time.sleep(1)

def DACThreadFunction():
    global Vout
    while (1):
        Vout = Data[1]/1023 * Data[3]
        time.sleep(1)

def convertToVoltage (ADC_Output ,Vref= 3.3):
    v = ((ADC_Output[1] & int('00000011',2)) << 8) + ADC_Output[2]
    return (v*Vref)/1024.0

def getHumidty():
    data = [firstByte,humidityByte,lastByte]
    adc.xfer(data, 10000, 24)
    return convertToVoltage(data)

def getLight():
    data = [firstByte,lightByte,lastByte]
    adc.xfer(data, 10000, 24)
    v = ((data[1] & int('00000011',2)) << 8) + data[2]
    return (2**10 - 1 - v)

def getTemperature():
    data = [firstByte,tempByte,lastByte]
    adc.xfer(data, 10000, 24)
    temp = (convertToVoltage(data)-V_0)/Tc
    return temp

def getADCData():
    Data[1] = getHumidty()
    Data[3] = getLight()
    Data[2] = getTemperature()
    return;

def main():
    print("+====================================================================+")
    print("|                              Starting                              |")
    print("+----------+-----------+----------+--------+-------+---------+-------+")
    print("| RTC Time | Sys Timer | Humidity |  Temp  | Light | DAC Out | Alarm |")
    print("+==========+===========+==========+========+=======+=========+=======+")
    init()
    getADCData()
    # start threads
    for thread in threads:
        thread.start()




def cleanUp():
    if IsGPIO:
        GPIO.cleanup()
    if IsSPI:
        acd.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting gracefully")
        cleanUp()
    except Exception as e:
        cleanUp()
        print("Error: ")
        print (str(e))
