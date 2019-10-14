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
import datetime          # for timing
import BlynkLib          # for blynk app

#---------------------------Global Variables----------------------------

IsGPIO = False
IsSPI = False
delay = 5
logging = True
alarm = False
blynk = BlynkLib.Blynk('QaSs_5koxPXKY8STWWwvX3Eqsdsi-1U3') # Initialize Blynk

# For ADC SPI
firstByte = int('00000001',2)
humidityByte = int('10000000',2)
lightByte = int('10010000',2)
tempByte = int('10100000',2)
lastByte = int('00000000',2)
adc = spidev.SpiDev()

# For DAC
commandBits = int('0111',2) << 12
Vref = 3.3
dac = spidev.SpiDev()
upperLimit = 2.65
lowerLimit = 0.65
AlarmString = " "
lastAlarmTime = 0
alarmBuffer = 3 #min
# For time
sysStart = datetime.datetime.now()
Data = ["00:00:00",0,0,0]

# For threads
threads = []

# For temperatuer
Tc  = 0.01  #Volts/(degrees Celcius)
V_0 = 0.55  #Volts

Vout = 0

pwm = []
#----------------------------functions----------------------------------
def init():
    # init Gpio
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    #Inputs
    GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP) # reset system time
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP) # increment
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP) # decrement
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) # start/stop
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP) # deactivate alarm

     # Setup interupts for HW buttons
    GPIO.add_event_detect(15, GPIO.FALLING, callback=increment, bouncetime=200)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=decrement, bouncetime=200)
    GPIO.add_event_detect(14, GPIO.FALLING, callback=resetSysTime, bouncetime=200)
    GPIO.add_event_detect(23, GPIO.FALLING, callback=stopStart, bouncetime=200)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=alarmDeactivate, bouncetime=200)
    # outputs
    GPIO.setup(12, GPIO.OUT)
    alarmPwm = GPIO.PWM(12, 262)
    pwm.append(alarmPwm)
    IsGPIO = True
    # init SPI    adc = spidev.SpiDev()
    adc.open(0,1)
    dac.open(0,0)
    IsSPI = True

    # Set up threads
    dataThread = threading.Thread(target = dataThreadFunction)
    mainThread = threading.Thread(target = mainThreadFunction)
    DACThread = threading.Thread(target = DACThreadFunction)
    alarmThread = threading.Thread(target = alarmThreadFunction)
    blynkThread = threading.Thread(target = blynkThreadFunction)
    threads.append(mainThread)
    threads.append(DACThread)
    threads.append(dataThread)
    threads.append(alarmThread)
    threads.append(blynkThread)


def mainThreadFunction():
    global Vout
    global delay
    global logging
    while(1):
        if(logging):
            now = datetime.datetime.now()
            print('|{:^10}|{:^11}|   {:1.1f}V   |  {:2.0f}°C  |  {:^4.0f} |  {:1.2f}V  |   {}   |'.format(now.strftime("%H:%M:%S"), str(now-sysStart)[:-7], Data[1], Data[2],Data[3],Vout,AlarmString))
            print("+----------+-----------+----------+--------+-------+---------+-------+")
    #wait = time.time()
    #while((time.time()-wait) < delay):
        #pass
        time.sleep(delay)

def dataThreadFunction():
    global sysSec
    global logging
    while(1):
        if logging:
            getADCData()
        time.sleep(1)

def DACThreadFunction():
    global Vout
    global Vref
    global lastAlarmTime
    global AlarmString
    global alarm
    global logging
    global upperLimit, lowerLimit
    while (1):
        if logging:
            Vout = Data[1]/1023 * Data[3]
            if(((Vout < lowerLimit) or (Vout > upperLimit)) and ((time.time()-lastAlarmTime) > (60*alarmBuffer))):
                AlarmString = "*"
                lastAlarmTime = time.time()
                alarm = True
            Dn = int((Vout*2**10)/Vref)
            Dn = Dn << 2
            Dn = commandBits | Dn
            upperByte = Dn >> 8
            lowerByte = Dn & int('0000000011111111',2)
            dac.xfer([upperByte,lowerByte],10000,16)
        time.sleep(1)


def alarmThreadFunction():
    global alarm
    global pwm
    duty = 50
    while(1):
        if(alarm):
            pwm[0].start(duty)
            time.sleep(0.5)
            if (duty == 70):
                duty = 50
            else:
                duty = 70
        pwm[0].stop()
        time.sleep(0.01)

def blynkThreadFunction():
    # Temperature
    @blynk.VIRTUAL_READ(0)
    def my_read_handler():
        blynk.virtual_write(0, Data[2])

    # Humidity Guage
    @blynk.VIRTUAL_READ(1)
    def my_read_handler():
        hum = (Data[1]/3.3)*100
        blynk.virtual_write(1, hum)

    # Light Bar
    @blynk.VIRTUAL_READ(2)
    def my_read_handler():
        blynk.virtual_write(2, Data[3])


    while(1):
        blynk.run()

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

def decrement(channel):
    global delay
    switcher = {
        1: 5,
        2: 1,
        5: 2,
    }
    delay = switcher.get(delay, delay)
    print("|                           Delay is {:d}                               |".format(delay))
    print("+----------+-----------+----------+--------+-------+---------+-------+")

def increment(channel):
    global delay
    switcher = {
        1: 2,
        2: 5,
        5: 1,
    }
    delay = switcher.get(delay, delay)
    print("|                           Delay is {:d}                               |".format(delay))
    print("+----------+-----------+----------+--------+-------+---------+-------+")

def resetSysTime(channel):
    global sysStart
    sysStart = datetime.datetime.now()

def stopStart(channel):
    global logging
    logging = not logging
    if logging:
        #print("+----------+-----------+----------+--------+-------+---------+-------+")
        print("|                               Start                                |")
        print("+----------+-----------+----------+--------+-------+---------+-------+")
    else:
        #print("+----------+-----------+----------+--------+-------+---------+-------+")
        print("|                              Stopped                               |")
        print("+----------+-----------+----------+--------+-------+---------+-------+")

def alarmDeactivate(channel):
    global alarm, AlarmString
    if(alarm):
        alarm = False
        AlarmString = " "
        #print("+----------+-----------+----------+--------+-------+---------+-------+")
        print("|                           Alarm Dismissed                          |")
        print("+----------+-----------+----------+--------+-------+---------+-------+")

    else:
        print("|                     Oi stop pressing buttons :(                    |")
        print("+----------+-----------+----------+--------+-------+---------+-------+")

def main():
    global Vout
    global Alarm
    global AlarmString
    global lowerLiminit, upperLimit
    print("+====================================================================+")
    print("|                              Starting                              |")
    print("+----------+-----------+----------+--------+-------+---------+-------+")
    print("| RTC Time | Sys Timer | Humidity |  Temp  | Light | DAC Out | Alarm |")
    print("+==========+===========+==========+========+=======+=========+=======+")
    init()
    getADCData()
    Vout = Data[1]/1023 * Data[3]
    if((Vout < lowerLimit) or (Vout > upperLimit)):
          #print("Alarm")
          Alarm = True;
          AlarmString = "*"
          lastAlarmTime = time.time()

    for thread in threads:
        thread.start()




def cleanUp():
    GPIO.cleanup()
    acd.close()
    dac.cllose()
    for thread in threads():
        thread.join()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting gracefully")
        cleanUp()
        GPIO.cleanup()
    except Exception as e:
        cleanUp()
        print("Error: ")
        print (str(e))
