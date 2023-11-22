#importy
import time
import adafruit_adxl34x
import board
import busio
import math
import queue
from threading import Thread

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

dirX = 19
stepX = 26

dirY = 21
stepY = 20

GPIO.setup(19,GPIO.OUT) # dir
GPIO.setup(26,GPIO.OUT) # step
GPIO.setup(21,GPIO.OUT) # dir
GPIO.setup(20,GPIO.OUT) # step


i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)
#klasa ogarniajaca silniki krokowe

def step(directionRef, directionPin, stepPin, commandQueue):
    direction = 0
    while(True):
        try:
            direction = commandQueue.get(block=False)
            print(direction)
        except queue.Empty:
            pass

        # if(direction > 0):
        #     GPIO.output(directionPin,GPIO.HIGH)
        # else:
        #     GPIO.output(directionPin,GPIO.LOW)

        if abs(direction) > 1e-6:
            print(direction)
            for i in range(0,abs(direction)*2):
                # GPIO.output(stepPin, i%2)
                sleep( 0.05 / abs(direction) / 2)
            

angleRefX = [0]
angleRefY = [0]

xCommandQueue = queue.Queue()
xCommandQueue.put(3)
x = Thread(target=step, args=(angleRefX, dirX, stepX, xCommandQueue))
# y = Thread(target=step, args=(angleRefY, dirY, stepY))
x.start()
# y.start()

while True:
    pass
    # xaccel = accelerometer.acceleration[0]
    # yaccel = accelerometer.acceleration[1]
    # zaccel = accelerometer.acceleration[2]

    # alpha = -(math.atan2(zaccel, xaccel)*360/(2*math.pi) + 90)
    # beta = math.atan2(zaccel, yaccel)*360/(2*math.pi) + 90
    
    # angleRefX[0] = int(alpha)
    # angleRefY[0] = int(beta)

    # time.sleep(0.05)

    #obliczenie wektora
    #sczytanie danych z adxl345
    #normalizacja wektora
    #obliczenie kata odchylenia
