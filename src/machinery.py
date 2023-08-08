import game_object
from bush import asset_handler


class Machine(game_object.GameObject):
    registry_groups = ("main", "collision")

    def _init__(self, data):
        img = asset_handler.glob_loader.load("parts.png")
        sub = img.subsurface
        self.parts = {
            "machinery1": (sub((0, 0, 16, 16), (16, 16))),
            "machinery2": (sub(0, 30, 18, 16), (46, 16)),
            "machinery3": (sub((0, 16, 22, 16)), (64, 16)),
            "machinery4": (sub()),
            "machinery5": 0,
        }
