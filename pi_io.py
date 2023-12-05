# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=import-error

import adafruit_adxl34x
import board
import busio
from RPi import GPIO

GPIO.setmode(GPIO.BCM)


class Motor:
    def __init__(self, pin_direction: int, pin_step: int):
        self._pin_direction = pin_direction
        self._pin_step = pin_step
        GPIO.setup(pin_direction, GPIO.OUT)
        GPIO.setup(pin_step, GPIO.OUT)

    def set_direction(self, direction: bool):
        GPIO.output(self._pin_direction, direction)

    def set_step(self, step: bool):
        GPIO.output(self._pin_step, step)


class Accelerometer:
    def __init__(self, pin_scl: int = board.SCL, pin_sda: int = board.SDA):
        i2c = busio.I2C(pin_scl, pin_sda)
        self._adxl345 = adafruit_adxl34x.ADXL345(i2c)

    def get_acceleration(self) -> (float, float, float):
        return self._adxl345.acceleration
