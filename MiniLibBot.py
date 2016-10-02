# "Mini Library Bot Main Script"
#
# A twitter bot that tweets out when books are taken/removed from a miniature
# library, it also replies to twitter users using the hashtag #MiniLibBot.
# There are also LED's and an LCD that the bot controls within the library.
# 
# LCD functions written by Matt Hawkins
# http://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/
#
# A.Woodward 2016


#imports
import RPi.GPIO as GPIO
import time
import sys
import random
import threading
import os
import LCD_functions
from random import randint
from threading import Thread
from twython import Twython
from datetime import datetime

#twitter credentials
apiKey = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
apiSecret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
accessToken = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
accessTokenSecret = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
api = Twython(apiKey, apiSecret, accessToken, accessTokenSecret)

#initialize gpio pins for buttons and leds
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(32,GPIO.IN) #setup for removetwitter button
GPIO.setup(38,GPIO.IN) #setup for inserttwitter button
GPIO.setup(36,GPIO.IN) #setup for shutdown button

pins = [11, 12, 13, 15, 16, 18, 22, 7]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)   # Set all pins' mode to output
    GPIO.output(pin, GPIO.HIGH) # Set all pins to high(+3.3V) to off led

#initialize of tweetbutton presses
removepresses = 0
insertpresses = 0
shutdown = 0

#import number of books from text file
with open('numberofbooks.txt') as f:
    a = f.read()

with open("lastuser.txt") as f:
    b = f.read()

lastUser = b
remainingBooks = int(a)


# Define GPIO for LCD mapping
LCD_RS = 37
LCD_E  = 35
LCD_D4 = 33
LCD_D5 = 31
LCD_D6 = 29
LCD_D7 = 23

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# dictionaries containing possible strings for tweets
tweetremoveDict = { 0:"Thanks for taking a book at ",
                    1:"The mini library was used at ",
                    2:"Someone used the library and pressed the button at ",
                    3:"Another button press at ",
                    4:"Finally another person has pressed my button at ",
                    5:"Enjoy the read! ",
                    6:"There's always more where that came from! ",
                    7:"Thanks for taking a book, until next time! ",
                    8:"Thanks for stopping by at ",
		    9:"Enjoy! Come back soon. "}

tweetinsertDict = { 0:"Thanks for stocking the mini library at ",
                    1:"Wow another book is here at ",
                    2:"At this rate I wont have any more room! ",
                    3:"People like you keep this library active, thanks! ",
                    4:"Thanks for supporting the local mini library at ",
                    5:"There are so many books being added! ",
		    6:"New books keep things interesting, Thanks! ",
		    7:"I'm going to have to build another library cause there are so many book! "}


#lcd initialization
def lcd_init():

  GPIO.setwarnings(False)
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)



#controls leds after button is pressed
def LEDshow():
    for pin in pins:
    	GPIO.output(pin, GPIO.LOW)	
    	time.sleep(0.5)
    	GPIO.output(pin, GPIO.HIGH)


#sends the removetweet with current time
def tweetremove():
    tweetStr = tweetremoveDict[randint(0,8)] + time.strftime("%I:%M %p",time.localtime(time.time()))
    api.update_status(status=tweetStr)
    print "Tweeted:" + tweetStr

#sends the inserttweet with current time
def tweetinsert():
    tweetStr = tweetinsertDict[randint(0,5)] + time.strftime("%I:%M %p",time.localtime(time.time()))
    api.update_status(status=tweetStr)
    print "Tweeted:" + tweetStr
    

#determines output of LCD 
def LCDtext():
    lcd_init()
    remflag = 0
    while True:
        if(shutdown == 1): break
        lcd_string("# of books put", LCD_LINE_1)
        lcd_string("in here today:" + str(insertpresses), LCD_LINE_2)
        time.sleep(10)
        if(shutdown == 1): break
        
        lcd_string("I'm on Twitter!", LCD_LINE_1)
        lcd_string("@MiniLibBot", LCD_LINE_2)
        time.sleep(10)
        if(shutdown == 1): break

        lcd_string("# of books", LCD_LINE_1)
        lcd_string("removed today:" + str(removepresses), LCD_LINE_2)
        time.sleep(10)
        if(shutdown == 1): break

	lcd_string("# of books",LCD_LINE_1)
	lcd_string("remaining: " + str(remainingBooks),LCD_LINE_2)
	time.sleep(10)
	if(shutdown == 1): break

	lcd_string("Play PokemonGO?",LCD_LINE_1)
	lcd_string("Go Team Mystic!",LCD_LINE_2)
	time.sleep(10)

        if(remainingBooks <= 4 and remainingBooks > remflag):
            tweetStr = "I'm low on books! Please come by and add more!" + time.strftime("%I:%M %p",time.localtime(time.time()))
            api.update_status(status=tweetStr)
            remflag = remainingBooks
        if(remainingBooks > 5):
            remflag = 0
        
#searches through twitter messages every 30 seconds and replys to users with how man books remain
def tweetReply():
    time.sleep(60)
    global lastUser
    global shutdown
    while True:
        if(shutdown == 1): break
        search_results = api.search(q="#MiniLibBot", count=1)
        for tweet in search_results["statuses"]:
            if(lastUser != tweet["user"]["screen_name"]):
                tweetStr = "@" +tweet["user"]["screen_name"]+ " There are " + str(a) + " books remaining in the mini library!"
                api.update_status(status = tweetStr, in_reply_to_status_id = tweet["id_str"])
                lastUser = tweet["user"]["screen_name"]
        time.sleep(10)

#waits for tweetbutton to be pressed to commence
def tweetremoveButton():
    while True:
        if(shutdown == 1): break
        if(GPIO.input(32) == True):
            global removepresses
            removepresses += 1
            global remainingBooks
            remainingBooks -= 1
            lcd_string("Thanks!  :)", LCD_LINE_1)
            lcd_string("Have a nice day.", LCD_LINE_2)
            tweetremove()
            LEDshow()
        time.sleep(0.2)

#waits for insert button to be pressed to commence
def tweetinsertButton():
    while True:
        if(shutdown == 1): break
        if(GPIO.input(38) == True):
            global insertpresses
            insertpresses += 1
            global remainingBooks
            remainingBooks += 1
            lcd_string("Thanks!  :)", LCD_LINE_1)
            lcd_string("Have a nice day.", LCD_LINE_2)
            tweetinsert()
            LEDshow()
        time.sleep(0.2)    

try:    

    #multithreading three main functions
    print "starting threads"

    Thread(target = LCDtext).start()
    Thread(target = tweetremoveButton).start()
    Thread(target = tweetinsertButton).start()
    Thread(target = tweetReply).start()

    #wait for shutdown button press
    while True:
        if(GPIO.input(36) == True):
            break
        time.sleep(0.2)

    
    #program will shutdown after button is detected
    shutdown = 1
    print "shutdown detected"
    tweetStr = "I'm shutting down now, but feel free to still come by! Totals since last shutdown: Removed " + str(removepresses) +", Inserted " + str(insertpresses) + ", Remaining "+ str(remainingBooks)+ "."
    api.update_status(status=tweetStr)

    with open('numberofbooks.txt', 'w') as f:
        f.write(str(remainingBooks))

    with open("lastuser.txt",'w') as f:
        f.write(lastUser)
              
    time.sleep(5)
    lcd_string("Shutdown", LCD_LINE_1)
    lcd_string("Activated", LCD_LINE_2)
    GPIO.cleanup()
    time.sleep(5)
    os.system("sudo shutdown -h now")

except KeyboardInterrupt:
    print "keyboard interupt"
    with open('numberofbooks.txt', 'w') as f:
        f.write(str(remainingBooks))

    with open("lastuser.txt",'w') as f:
        f.write(lastUser)
    GPIO.cleanup()

        

