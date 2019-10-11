#!/usr/bin/python3
"""
Names: Nicolas Reid
Student Number: RDXNIC008
Prac: 1
Date: 22 July 2019
"""

# import Relevant Librares
import RPi.GPIO as GPIO
import time

# Initialise counter variable
count = 0

def main():

    # GPIO setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(14, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Create lists to store binary numbers
    zero = (0,0,0)
    one = (1,0,0)
    two = (0,1,0)
    three = (1,1,0)
    four = (0,0,1)
    five = (1,0,1)
    six = (0,1,1)
    seven = (1,1,1)

    # Begin at zero
    GPIO.output((14,15,18), zero)

    # Case: 'up' button pressed
    def up(channel):
        global count
        count += 1
        if (count == 1):
            GPIO.output((14, 15, 18), one)
        elif (count == 2):
            GPIO.output((14,15,18), two)
        elif (count == 3):
            GPIO.output((14,15,18), three)
        elif (count == 4):
            GPIO.output((14,15,18), four)
        elif (count == 5):
            GPIO.output((14,15,18), five)
        elif (count == 6):
            GPIO.output((14,15,18), six)
        elif (count == 7):
            GPIO.output((14,15,18), seven)
        elif (count == 8):
            count = 0
            GPIO.output((14,15,18), zero)

    # Case "down" button pressed
    def down(channel):
        global count
        count -= 1
        if (count == 1):
            GPIO.output((14, 15, 18), one)
        elif (count == 2):
            GPIO.output((14,15,18), two)
        elif (count == 3):
            GPIO.output((14,15,18), three)
        elif (count == 4):
            GPIO.output((14,15,18), four)
        elif (count == 5):
            GPIO.output((14,15,18), five)
        elif (count == 6):
            GPIO.output((14,15,18), six)
        elif (count == -1):
            count = 7
            GPIO.output((14,15,18), seven)
        elif (count == 0):
            GPIO.output((14,15,18), zero)

    # Setup interupts for up and down buttons
    GPIO.add_event_detect(23, GPIO.FALLING, callback=up, bouncetime=130)
    GPIO.add_event_detect(24, GPIO.FALLING, callback=down, bouncetime=130)

    # Allow time for implementation
    time.sleep(200)

# Only run the functions if
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
           main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off GPIOs
        GPIO.cleanup()
