import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BOARD)

GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("starting")
    GPIO.wait_for_edge(38, GPIO.FALLING)
    print("detected")
    os.system("sudo shutdown -h now")
    
except KeyboardInterrupt:
    pass

GPIO.cleanup()
