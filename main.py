#importy
import time
import adafruit_adxl34x
import board
import busio
import math
import queue
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import RPi.GPIO as GPIO
from time import sleep
from multiprocessing import Process, Value

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

def step(angle, directionPin, stepPin):
    direction = 0
    while(True):

        direction = int(angle.value / 2.)
        if(direction > 0):
            GPIO.output(directionPin,GPIO.HIGH)
        else:
            GPIO.output(directionPin,GPIO.LOW)

        if abs(direction) >= 1:
            sleepTime = 0.02 / abs(direction) / 2
            for i in range(0,abs(direction)*2):
                GPIO.output(stepPin, i%2)
                sleep(sleepTime)
            
# xCommandQueue = queue.Queue()
# xCommandQueue.put(3)
xAngle = Value('i', 0)
yAngle = Value('i', 0)
x = Process(target=step, args=(xAngle, dirX, stepX))
y = Process(target=step, args=(yAngle, dirY, stepY))
x.start()
y.start()

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# xs = []
# ys = []

# def animate(i, xs, ys):
#     # Read temperature (Celsius) from TMP102
#     temp_c = round(tmp102.read_temp(), 2)

#     # Add x and y to lists
#     xs.append(dt.datetime.now().strftime('%H:%M:%S.%f'))
#     ys.append(i % 3)

#     # Limit x and y lists to 20 items
#     xs = xs[-20:]
#     ys = ys[-20:]

#     # Draw x and y lists
#     ax.clear()
#     ax.plot(xs, ys)

#     # Format plot
#     plt.xticks(rotation=45, ha='right')
#     plt.subplots_adjust(bottom=0.30)
#     plt.title('TMP102 Temperature over Time')
#     plt.ylabel('Temperature (deg C)')

# ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
# plt.show()

prevTime = time.time()
while True:
    
    xaccel = accelerometer.acceleration[0]
    yaccel = accelerometer.acceleration[1]
    zaccel = accelerometer.acceleration[2]
    
    alpha = (math.atan2(zaccel, yaccel)*360/(2*math.pi) + 90)
    beta = (math.atan2(zaccel, xaccel)*360/(2*math.pi) + 90)
    xAngle.value = int(alpha)
    yAngle.value = int(beta)

    time.sleep(0.02)
    #print(time.time() - prevTime)
    prevTime = time.time()

