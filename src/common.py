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
    }
}