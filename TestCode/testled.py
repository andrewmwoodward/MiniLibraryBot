#!/usr/bin/env python
import RPi.GPIO as GPIO
import time




GPIO.setmode(GPIO.BOARD)        # Numbers GPIOs by physical location
	
GPIO.setup(22, GPIO.OUT)   # Set all pins' mode is output
GPIO.output(22, GPIO.HIGH) # Set all pins to high(+3.3V) to off led

while True:
    GPIO.output(22, GPIO.LOW)
            
