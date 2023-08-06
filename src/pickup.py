import common
import game_object
import itertools
import pygame
from bush import timer
import random


class Pickup(game_object.GameObject):
    registry_groups = ("main", "pickups")
    image_name = None

    def __init__(self, data):
        if self.image_name is not None:
            data.surface = common.ITEM_IMAGES[self.image_name]
        super().__init__(data)
        self.positions = itertools.cycle(
            [
                self.pos + pygame.Vector2(0, 1),
                self.pos,
                self.pos + pygame.Vector2(0, -1),
                self.pos,
            ]
        )
        for i in range(random.randint(0, 4)):
            next(self.positions)
        self.new_pos_timer = timer.Timer(250, self.adjust_pos, True)

    def adjust_pos(self):
        self.pos = next(self.positions)

    def update(self, dt):
        super().update(dt)
        self.new_pos_timer.update()

    def pickup(self):
        pass


class Key(Pickup):
    image_name = "key"

    def pickup(self):
        if self.registry.get_group("player").sprite.get_key():
            self.kill()


class Machinery(Pickup):
    def __init__(self, data):
        self.value = self.image_name = data.misc["value"]
        super().__init__(data)

    def pickup(self):
        if self.registry.get_group("player").sprite.get_machinery(self.value):
            self.kill()


class Oxygen(Pickup):
    image_name = "oxygen"

    def pickup(self):
        if self.registry.get_group("player").sprite.refill_oxygen():
            self.kill()


class Health(Pickup):
    image_name = "health"

    def pickup(self):
        if self.registry.get_group("player").sprite.heal(3):
            self.kill()
