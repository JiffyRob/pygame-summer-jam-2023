import pygame

import game_object
import player
from bush import entity, physics


class Pushblock(game_object.MobileGameObject):
    PUSH_SPEED = 16
    registry_groups = ("main", "collision")

    def __init__(self, data):
        super().__init__(data)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, other, dt):
        match other:
            # move slightly for player
            case player.Player():
                self.pos += (self.pos - other.pos).clamp_magnitude(self.PUSH_SPEED * dt)
                self.update_rects()
                physics.static_collision(other, self, dt, False)
            # I smashed into something static
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_STATIC, _)
            ):
                physics.static_collision(self, player, dt, False)
            # I smashed into something dynamic (or more likely they smashed into me)
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, _)
            ):
                physics.static_collision(other, self, dt, False)


class Drifter(game_object.GameObject):
    registry_groups = ("main", "collision")

    def __init__(self, data):
        super().__init__(
            data,
            physics_data=physics.PhysicsData(
                physics.TYPE_TRIGGER, data.registry.get_group("collision")
            ),
        )
        self.direction = pygame.Vector2(
            [int(i) for i in data.misc.get("direction", "0, 0").split(", ")]
        )
        self.mask = pygame.mask.from_surface(self.image)

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC:
            other.drift(self.direction)
