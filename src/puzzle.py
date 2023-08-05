import pygame

import game_object
import player
from bush import entity, physics, util


class Pushblock(game_object.MobileGameObject):
    PUSH_SPEED = 16
    registry_groups = ("main", "collision")

    def __init__(self, data):
        super().__init__(data)
        self.mask = pygame.Mask(self.rect.size, True)

    def on_collision(self, other, dt):
        print("collider")
        match other:
            # move slightly for player
            case player.Player():
                veloc = pygame.Vector2(util.direction_orthag(self.pos - other.pos))
                veloc.scale_to_length(self.PUSH_SPEED * dt)
                self.pos += veloc
                self.update_rects()
                physics.resolve_collision(other, self)
            # I smashed into something static
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_STATIC, _)
            ):
                physics.resolve_collision(self, player)
            # I smashed into something dynamic (or more likely they smashed into me)
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, _)
            ):
                physics.resolve_collision(other, self)


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
        else:
            print("can't collide with", other)
