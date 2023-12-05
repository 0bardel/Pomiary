import argparse
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from time import sleep
from multiprocessing import Process, Value


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


def anim(xAngle, yAngle):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Gimbal')
    xs = []
    ys = []
    t = []

    def animate(i, xs, ys, t, xAngle, yAngle):
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
        plt.setp(axs[0], xlim=(-25, 25))
        fig[0].ylim(-25, 25)
        plt.title('Angle over time')
        plt.xlabel("Kąt X")
        plt.ylabel("Kąt Y")

        fig[1].plot(t, xs)
        fig[1].plot(t, ys)
        plt.ion()
        return plt.plot()
    aaa = animation.FuncAnimation(fig, animate, fargs=(
        xs, ys, t, xAngle, yAngle), interval=500, cache_frame_data=False)
    plt.show()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--dummy-data', action='store_true')
    dummy_data = argument_parser.parse_args().dummy_data

    if not dummy_data:
        import adafruit_adxl34x
        import board
        import busio
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(19, GPIO.OUT)  # dir
        GPIO.setup(26, GPIO.OUT)  # step
        GPIO.setup(21, GPIO.OUT)  # dir
        GPIO.setup(20, GPIO.OUT)  # step

        i2c = busio.I2C(board.SCL, board.SDA)
        accelerometer = adafruit_adxl34x.ADXL345(i2c)

    dirX = 19
    stepX = 26

    dirY = 21
    stepY = 20

    # klasa ogarniajaca silniki krokowe

    xAngle = Value("i", 0)
    yAngle = Value("i", 0)
    xPrevious = Value("i", 0)
    yPrevious = Value("i", 0)

    if not dummy_data:
        x = Process(target=step, args=(xAngle, dirX, stepX))
        y = Process(target=step, args=(yAngle, dirY, stepY))
        x.start()
        y.start()

    a = Process(target=anim, args=(xAngle, yAngle))
    a.start()

    alphaHist = []
    betaHist = []

    prevTime = time.time()
    while True:
        if dummy_data:
            xaccel = math.sin(time.time())
            yaccel = math.sin(time.time() * 1.1)
            zaccel = math.sin(time.time() * 1.2)
        else:
            xaccel = accelerometer.acceleration[0]
            yaccel = accelerometer.acceleration[1]
            zaccel = accelerometer.acceleration[2]

        alpha = math.atan2(zaccel, yaccel) * 360 / (2 * math.pi) + 90
        beta = math.atan2(zaccel, xaccel) * 360 / (2 * math.pi) + 90
        xAngle.value = int(alpha)
        yAngle.value = int(beta)

        time.sleep(0.02)
        # print(time.time() - prevTime)
        prevTime = time.time()

        alphaHist.append(alpha)
        betaHist.append(beta)


if __name__ == '__main__':
    main()
