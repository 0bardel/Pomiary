import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

GPIO.setup(19,GPIO.OUT) # dir
GPIO.setup(26,GPIO.OUT) # step


stepFlag = False
while True:
    GPIO.output(19,GPIO.LOW)
    stepFlag = not stepFlag
    GPIO.output(26,stepFlag)
    sleep(0.002)
