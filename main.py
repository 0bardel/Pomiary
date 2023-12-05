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
    
    while True:
        direction = int(angle.value / 2.0)
        if direction > 0:
            GPIO.output(directionPin, GPIO.HIGH)
        else:
            GPIO.output(directionPin, GPIO.LOW)

        if abs(direction) >= 1:
            sleepTime = 0.02 / abs(direction) / 2
            for i in range(0, abs(direction) * 2):
                GPIO.output(stepPin, i % 2)
                sleep(sleepTime)

xAngle = Value("i", 0)
yAngle = Value("i", 0)
xPrevious = Value("i", 0)
yPrevious = Value("i", 0)
x = Process(target=step, args=(xAngle, dirX, stepX))
y = Process(target=step, args=(yAngle, dirY, stepY))
x.start()
y.start()

def anim(xAngle, yAngle):
    
    fig, axs = plt.subplots(1, 2,figsize=(12,6))
    fig.suptitle('Gimbal')
    xs = []
    ys = []
    t = []
    def animate(i, xs, ys,t, xAngle, yAngle):
        xs.append(xAngle.value)
        ys.append(yAngle.value)
        t.append(time.time())
        # Limit x and y lists to 20 items
        xs = xs[-20:]
        ys = ys[-20:]
        t = t[-20:]
        # Draw x and y lists
        axs[0].scatter(xs, ys)

        # Format plot
        plt.setp(axs[0],xlim = (-25,25))
        fig[0].ylim(-25,25)
        plt.title('Angle over time')
        plt.xlabel("Kąt X")
        plt.ylabel("Kąt Y")

        fig[1].plot(t, xs)
        fig[1].plot(t, ys)
        plt.ion()
        return plt.plot()
    aaa = animation.FuncAnimation(fig, animate, fargs=(xs, ys,t, xAngle, yAngle), interval=500, cache_frame_data=False)
    plt.show()

a = Process(target=anim, args=(xAngle, yAngle))
a.start()



alphaHist=[]
betaHist=[]

prevTime = time.time()
while True:
    xaccel = accelerometer.acceleration[0]
    yaccel = accelerometer.acceleration[1]
    zaccel = accelerometer.acceleration[2]

    alpha = math.atan2(zaccel, yaccel) * 360 / (2 * math.pi) + 90
    beta = math.atan2(zaccel, xaccel) * 360 / (2 * math.pi) + 90
    xAngle.value = int(alpha)
    yAngle.value = int(beta)

    time.sleep(0.02)
    print(time.time() - prevTime)
    prevTime = time.time()


    alphaHist.append(alpha)
    betaHist.append(beta)