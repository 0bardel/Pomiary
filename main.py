# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import argparse
import math
from multiprocessing import Process, Value
import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation

PIN_DIR_X = 19
PIN_STEP_X = 26
PIN_DIR_Y = 21
PIN_STEP_Y = 20

XY_PLOT_MAX_POINTS = 20
ANGLE_TIME_PLOT_MAX_POINTS = 20


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

    start_time = time.time()

    def update(_, xs, ys, t, x_angle, y_angle):
        xs.append(x_angle.value)
        ys.append(y_angle.value)
        t.append(time.time() - start_time)

        axs[0].clear()
        axs[1].set_title("Położenie w czasie")
        axs[0].set_xlim(0, 360)
        axs[0].set_ylim(0, 360)
        axs[0].scatter(xs[-XY_PLOT_MAX_POINTS:], ys[-XY_PLOT_MAX_POINTS:])

        axs[1].clear()
        axs[1].set_title("Zależność kąta od czasu")
        axs[1].set_ylim(0, 360)
        axs[1].plot(
            t[-ANGLE_TIME_PLOT_MAX_POINTS:],
            xs[-ANGLE_TIME_PLOT_MAX_POINTS:],
            label="Kąt X",
        )
        axs[1].plot(
            t[-ANGLE_TIME_PLOT_MAX_POINTS:],
            ys[-ANGLE_TIME_PLOT_MAX_POINTS:],
            label="Kąt Y",
        )
        axs[1].legend(loc="upper right")

        return axs

    _ = animation.FuncAnimation(
        fig,
        update,
        fargs=(xs, ys, t, x_angle, y_angle),
        interval=100,
        cache_frame_data=False,
    )
    plt.show()


def read_accelerometer(accelerometer, x_angle, y_angle):
    while True:
        (xaccel, yaccel, zaccel) = accelerometer.get_acceleration()
        x_angle.value = (math.atan2(zaccel, yaccel) * 360 / (2 * math.pi) + 90) % 360
        y_angle.value = (math.atan2(zaccel, xaccel) * 360 / (2 * math.pi) + 90) % 360
        time.sleep(0.02)


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

    x_angle = Value("d", 0)
    y_angle = Value("d", 0)

    process_update_motor_x = Process(target=update_motor, args=(x_angle, motor_x))
    process_update_motor_y = Process(target=update_motor, args=(y_angle, motor_y))
    process_update_motor_x.start()
    process_update_motor_y.start()

    process_read_accelerometer = Process(
        target=read_accelerometer, args=(accelerometer, x_angle, y_angle)
    )
    process_read_accelerometer.start()

    def exit_program():
        process_update_motor_x.kill()
        process_update_motor_y.kill()
        process_read_accelerometer.kill()
        sys.exit()

    interface_choices = {
        "w": (
            lambda: Process(target=plot, args=(x_angle, y_angle)).start(),
            "Pokaż wykres",
        ),
        "p": (lambda: print("Niezaimplementowane."), "Zapisz dane do pliku"),
        "x": (exit_program, "Wyjdź"),
    }
    while True:
        print(
            'Wybierz operację, wpisując odpowiedni znak i następnie wciskając "enter".'
        )
        for character, (_, description) in interface_choices.items():
            print(f" {character} - {description}")
        user_input = input()
        interface_choices[user_input][0]()


if __name__ == "__main__":
    main()
