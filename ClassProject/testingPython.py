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


while True:
    blynk.run()
