from enum import Enum

import pygame


class Machinery(Enum):
    MACHINERY_1 = 1
    MACHINERY_2 = 2
    MACHINERY_3 = 4
    MACHINERY_4 = 8


TERRAINS = {
    "metal": {
        "speed": 70,
        "traction": 1,
        "boost": 0,
        "flow": pygame.Vector2(),
    },
    "land": {
        "speed": 64,  # basic speed
        "traction": 0.7,  # ability to change direction
        "boost": 16,  # extra burst of speed applied on keydown
        "flow": pygame.Vector2(),  # "gravity" toward a certain direction
    },
    "water": {
        "speed": 12,
        "traction": 0.1,
        "boost": 48,
        "flow": pygame.Vector2(-0.4, 0),
    },
    "underwater": {
        "speed": 32,
        "traction": 0.1,
        "boost": 48,
        "flow": pygame.Vector2(-0.4, 0),
    },
    "null": {"speed": 32, "traction": 1, "boost": 0, "flow": pygame.Vector2()},
}

SCREEN_SIZE = pygame.Vector2(320, 240)

LAYER_UP = pygame.event.custom_type()
LAYER_DOWN = pygame.event.custom_type()
GAME_OVER = pygame.event.custom_type()
