import pygame

import game_object


class NPC(game_object.GameObject):
    registry_groups = ("main", "collision", "interactable")

    def __init__(self, data):
        super().__init__(data)
        self.script = data.misc.get("script")

    def interact(self):
        if not self.script_stack:
            self.run_script(self.script)
