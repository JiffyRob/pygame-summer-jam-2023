import math

import numpy as np
import pygame

import common

a = common.WAVE_DATA["amplitude"] / math.pi * 2
b = common.WAVE_DATA["period"] / math.pi * 2


def modulate(surface, offset):
    size = surface.get_size()
    with pygame.pixelarray.PixelArray(surface).transpose() as array:
        for y in range(size[1]):
            sin_offset = round(a * math.sin(b * (y - offset)))
            if sin_offset:
                array[y][:sin_offset] = array[y][-sin_offset:]
                array[y][sin_offset:] = array[y][:-sin_offset]
    return surface
