import BlynkLib
import time

# Initialize Blynk
blynk = BlynkLib.Blynk('QaSs_5koxPXKY8STWWwvX3Eqsdsi-1U3')

@blynk.VIRTUAL_READ(2)
def my_read_handler():
#    blynk.virtual_write(1, 50)
    blynk.virtual_write(2, 20)

@blynk.VIRTUAL_READ(1)
def my_read_handler():
    blynk.virtual_write(1, 30)

@blynk.VIRTUAL_READ(0)
def my_read_handler():
    # blynk.virtual_write(1, 50)
    blynk.virtual_write(0, 99)

@blynk.ON(3)
def my_read_handler():
    blynk.on(3, 225)
    #WidgetLED led1(V3)
    #blynk.led1.on()

blynk.notify("Alarm!")

while True:
    blynk.run()
