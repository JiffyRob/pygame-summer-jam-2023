import pygame

import common
from bush import entity


class Teleport(entity.Entity):
    def __init__(self, data):
        data.image = pygame.Surface((16, 16))
        super().__init__(
            data.pos, None, [data.registry.get_group("main")], topleft=True
        )
        self.dest_map = data.misc["dest_map"]
        self.dest = pygame.Vector2([int(i) for i in data.misc["dest"].split(", ")])
        self.registry = data.registry
        self.rect = pygame.Rect(0, 0, 8, 8)
        self.rect.topleft = data.pos + (4, 4)

    def update(self, dt):
        player = self.registry.get_group("player").sprite
        if player is not None and player.collision_rect.colliderect(self.rect):
            pygame.event.post(
                pygame.Event(
                    common.MAP_SWITCH, {"name": self.dest_map, "pos": self.dest}
                )
            )
