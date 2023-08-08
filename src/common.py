import pygame

from bush import asset_handler

ITEM_IMAGES = dict(
    zip(
        asset_handler.glob_loader.load("pickup_names.csv", flatten=True),
        asset_handler.glob_loader.load_spritesheet("pickups.png", (8, 8)),
    )
)

TERRAINS = {
    "underwater": {
        "speed": 32,
        "traction": 0.1,
        "boost": 48,
        "flow": pygame.Vector2(-0.4, 0),
    },
    "water": {
        "speed": 12,
        "traction": 0.1,
        "boost": 48,
        "flow": pygame.Vector2(-0.4, 0),
    },
    "land": {
        "speed": 24,  # basic speed
        "traction": 0.7,  # ability to change direction
        "boost": 16,  # extra burst of speed applied on keydown
        "flow": pygame.Vector2(),  # "gravity" toward a certain direction
    },
    "metal": {
        "speed": 30,
        "traction": 1,
        "boost": 0,
        "flow": pygame.Vector2(),
    },
    "null": {"speed": 32, "traction": 1, "boost": 0, "flow": pygame.Vector2()},
}

SCREEN_SIZE = pygame.Vector2(320, 240)

LAYER_UP = pygame.event.custom_type()
LAYER_DOWN = pygame.event.custom_type()
MAP_SWITCH = pygame.event.custom_type()
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
