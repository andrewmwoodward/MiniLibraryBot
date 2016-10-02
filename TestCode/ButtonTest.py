import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(36,GPIO.IN)

try:
    while True:
        if(GPIO.input(36) == True):
            print "Button was pressed"
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
