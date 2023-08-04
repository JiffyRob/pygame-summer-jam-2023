import pygame

TERRAINS = {
    "land": {
        "speed": 64,  # basic speed
        "traction": 1,  # ability to change direction
        "boost": 16,  # extra burst of speed applied on keydown
        "flow": pygame.Vector2(),  # "gravity" toward a certain direction
    },
    "water": {
        "speed": 12,
        "traction": 0.1,
        "boost": 32,
        "flow": pygame.Vector2(-0.4, 0),
    },
    "underwater": {
        "speed": 10,
        "traction": 0.1,
        "boost": 32,
        "flow": pygame.Vector2(-0.4, 0),
    },
}

SCREEN_SIZE = pygame.Vector2(320, 240)

LAYER_UP = pygame.event.custom_type()
LAYER_DOWN = pygame.event.custom_type()
