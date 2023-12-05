# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import random


class Motor:
    def __init__(self, *_args, **_kwargs):
        pass

    def set_direction(self, *_args, **_kwargs):
        pass

    def set_step(self, *_args, **_kwargs):
        pass


class Accelerometer:
    def __init__(self, *_args, **_kwargs):
        pass

    def get_acceleration(self, *_args, **_kwargs) -> (float, float, float):
        return tuple(random.uniform(-1, 1) for _ in range(3))
