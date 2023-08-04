import math
import random

import pygame

import arg
import game_object
import script
from bush import timer, util


class Enemy(game_object.MobileGameObject):
    registry_groups = ("main", "enemies", "collision")

    def __init__(self, data, anim_dict=None, touch_damage=2, scripted=False):
        super().__init__(data, anim_dict)
        self.touch_damage = 2
        if scripted:
            self.run_script(data.script)

    def update_behaviour(self, dt):
        player = self.registry.get_group("player").sprite
        if self.collision_rect.colliderect(player.collision_rect):
            player.hurt(self.touch_damage)


class EelHead(Enemy):
    SPEED = 12
    TURN_SPEED = 5
    TTYPE_FOLLOW = 1
    TTYPE_RANDOM = 0

    def __init__(self, data):
        data.surface = util.circle_surf(9, "red")
        self.rotation = 0
        self.surface = data.surface.copy()
        self.turn_timer = timer.Timer(1500, self.turn, True)
        self.turn_type = self.TTYPE_RANDOM
        self.turn_speed = 0
        self.turn()
        super().__init__(data)
        last = self
        for _ in range(6):
            data = arg.GameObjectArgs(self.pos, self.registry, layer=self.layer - 1)
            last = EelBody(data, last)
        self.desired_velocity = util.randincircle(self.SPEED, True)

    def update_rects(self):
        self.rect = self.image.get_rect()
        self.collision_rect = self.image.get_bounding_rect()
        self.rect.center = self.collision_rect.center = self.pos

    def update_environment(self):
        self.terrain = "null"

    def turn(self):
        print("turn", self.turn_type)
        if random.randint(0, 1):
            self.turn_type = self.TTYPE_RANDOM
            self.turn_speed = random.random() * random.choice(
                [self.TURN_SPEED, -self.TURN_SPEED]
            )
        else:
            self.turn_type = self.TTYPE_FOLLOW
            self.turn_speed = 0

    def update_behaviour(self, dt):
        self.turn_timer.update()
        if self.turn_type == self.TTYPE_FOLLOW:
            self.desired_velocity = self.desired_velocity.slerp(
                self.registry.get_group("player").sprite.pos - self.pos, 0.02
            ).clamp_magnitude(self.SPEED)
        else:
            self.desired_velocity.rotate_ip(self.turn_speed)
        self.update_rects()
        super().update_behaviour(dt)


class EelBody(Enemy):
    SPEED = 32

    def __init__(self, data, leader):
        data.surface = util.circle_surf(8, "green")
        self.leader = leader
        super().__init__(data)

    def update_behaviour(self, dt):
        self.desired_velocity = self.leader.pos - self.pos
        super().update_behaviour(dt)

    def update_environment(self):
        self.terrain = "null"


class Fish(Enemy):
    SPEED = 12

    def __init__(self, data):
        ...
