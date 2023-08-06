import pygame


class Machinery:
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
GAME_START = pygame.event.custom_type()
GAME_OVER = pygame.event.custom_type()
PAUSE = pygame.event.custom_type()
DIALOG = pygame.event.custom_type()

TRACK_SWITCH = pygame.event.custom_type()
PLAY_SOUND = pygame.event.custom_type()


def play_sound(path, priority=10, loops=0, volume=1, fade=0, location=(0, 0)):
    pygame.event.post(
        pygame.Event(
            PLAY_SOUND,
            {
                "path": path,
                "priority": priority,
                "loops": loops,
                "volume": volume,
                "fade": fade,
                "location": location,
            },
        )
    )


def switch_track(path, volume=1):
    pygame.event.post(pygame.Event(TRACK_SWITCH, {"path": path, "volume": volume}))
