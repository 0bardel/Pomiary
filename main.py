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


def update_motor(angle, motor):
    direction = 0

    while True:
        direction = int(angle.value / 2.0)
        motor.set_direction(direction > 0)

        if abs(direction) >= 1:
            sleep_time = 0.02 / abs(direction) / 2
            for i in range(0, abs(direction) * 2):
                motor.set_step(bool(i % 2))
                time.sleep(sleep_time)


def plot(x_angle, y_angle):
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle("Gimbal")
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
        plt.title("Angle over time")
        plt.xlabel("Kąt X")
        plt.ylabel("Kąt Y")

        fig[1].plot(t, xs)
        fig[1].plot(t, ys)
        plt.ion()
        return plt.plot()

    _ = animation.FuncAnimation(
        fig,
        animate,
        fargs=(xs, ys, t, x_angle, y_angle),
        interval=500,
        cache_frame_data=False,
    )
    plt.show()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--dummy-data", action="store_true")
    dummy_data = argument_parser.parse_args().dummy_data

    # pylint: disable=import-outside-toplevel
    if dummy_data:
        from dummy_io import (
            Motor,
            Accelerometer,
        )
    else:
        from pi_io import (
            Motor,
            Accelerometer,
        )

    motor_x = Motor(PIN_DIR_X, PIN_STEP_X)
    motor_y = Motor(PIN_DIR_Y, PIN_STEP_Y)
    accelerometer = Accelerometer()

    x_angle = Value("i", 0)
    y_angle = Value("i", 0)

    process_update_motor_x = Process(target=update_motor, args=(x_angle, motor_x))
    process_update_motor_y = Process(target=update_motor, args=(y_angle, motor_y))
    process_update_motor_x.start()
    process_update_motor_y.start()

    process_plot = Process(target=plot, args=(x_angle, y_angle))
    process_plot.start()

    prev_time = time.time()
    while True:
        (xaccel, yaccel, zaccel) = accelerometer.get_acceleration()

        alpha = math.atan2(zaccel, yaccel) * 360 / (2 * math.pi) + 90
        beta = math.atan2(zaccel, xaccel) * 360 / (2 * math.pi) + 90
        x_angle.value = int(alpha)
        y_angle.value = int(beta)

        time.sleep(0.02)
        print(time.time() - prev_time)
        prev_time = time.time()


if __name__ == "__main__":
    main()
