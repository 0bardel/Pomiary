# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import argparse
import math
from multiprocessing import Process, Value
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation

PIN_DIR_X = 19
PIN_STEP_X = 26
PIN_DIR_Y = 21
PIN_STEP_Y = 20


def step(angle, direction_pin, step_pin):
    direction = 0

    while True:
        direction = int(angle.value / 2.0)
        if direction > 0:
            GPIO.output(direction_pin, GPIO.HIGH)
        else:
            GPIO.output(direction_pin, GPIO.LOW)

        if abs(direction) >= 1:
            sleep_time = 0.02 / abs(direction) / 2
            for i in range(0, abs(direction) * 2):
                GPIO.output(step_pin, i % 2)
                time.sleep(sleep_time)


def anim(x_angle, y_angle):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Gimbal')
    xs = []
    ys = []
    t = []

    def animate(_, xs, ys, t, x_angle, y_angle):
        xs.append(x_angle.value)
        ys.append(y_angle.value)
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
    _ = animation.FuncAnimation(fig, animate, fargs=(
        xs, ys, t, x_angle, y_angle), interval=500, cache_frame_data=False)
    plt.show()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--dummy-data', action='store_true')
    dummy_data = argument_parser.parse_args().dummy_data

    if not dummy_data:
        # pylint: disable=import-error
        # pylint: disable=import-outside-toplevel
        import adafruit_adxl34x
        import board
        import busio
        from RPi import GPIO

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(19, GPIO.OUT)  # dir
        GPIO.setup(26, GPIO.OUT)  # step
        GPIO.setup(21, GPIO.OUT)  # dir
        GPIO.setup(20, GPIO.OUT)  # step

        i2c = busio.I2C(board.SCL, board.SDA)
        accelerometer = adafruit_adxl34x.ADXL345(i2c)

    # klasa ogarniajaca silniki krokowe

    x_angle = Value("i", 0)
    y_angle = Value("i", 0)

    if not dummy_data:
        x = Process(target=step, args=(x_angle, PIN_DIR_X, PIN_STEP_X))
        y = Process(target=step, args=(y_angle, PIN_DIR_Y, PIN_STEP_Y))
        x.start()
        y.start()

    a = Process(target=anim, args=(x_angle, y_angle))
    a.start()

    alpha_hist = []
    beta_hist = []

    prev_time = time.time()
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
        x_angle.value = int(alpha)
        y_angle.value = int(beta)

        time.sleep(0.02)
        print(time.time() - prev_time)
        prev_time = time.time()

        alpha_hist.append(alpha)
        beta_hist.append(beta)


if __name__ == '__main__':
    main()
