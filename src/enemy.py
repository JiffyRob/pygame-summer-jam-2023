import random

import pygame

import arg
import game_object
from bush import asset_handler, timer, util


class Enemy(game_object.MobileGameObject):
    registry_groups = ("main", "enemies", "collision")

    def __init__(self, data, anim_dict=None, touch_damage=2, scripted=False):
        super().__init__(data, anim_dict)
        self.touch_damage = touch_damage
        if scripted:
            self.run_script(data.script)

    def update_behaviour(self, dt):
        player = self.registry.get_group("player").sprite
        if player is not None and self.collision_rect.colliderect(
            player.collision_rect
        ):
            player.hurt(self.touch_damage)


class EelHead(Enemy):
    SPEED = 12
    TURN_SPEED = 5
    TTYPE_FOLLOW = 1
    TTYPE_RANDOM = 0

    def __init__(self, data):
        frames = asset_handler.glob_loader.load_spritesheet("eel.png", (16, 16))
        flip = pygame.transform.flip
        anim_dict = {
            "up": flip(frames[2], False, True),
            "right_up": flip(frames[1], True, True),
            "right": flip(frames[0], True, False),
            "right_down": flip(frames[1], True, False),
            "down": frames[2],
            "left_down": frames[1],
            "left": frames[0],
            "left_up": flip(frames[1], False, True),
        }
        self.rotation = 0
        self.surface = data.surface.copy()
        self.turn_timer = timer.Timer(1500, self.turn, True)
        self.turn_type = self.TTYPE_RANDOM
        self.turn_speed = 0
        self.turn()
        super().__init__(data, anim_dict)
        last = self
        for _ in range(6):
            data = arg.GameObjectArgs(self.pos, self.registry, layer=self.layer - 1)
            last = EelBody(data, last)
        EelTail(arg.GameObjectArgs(self.pos, self.registry, layer=self.layer - 1), last)
        self.desired_velocity = util.randincircle(self.SPEED, True)

    def get_anim_key(self):
        return util.string_direction(self.velocity)

    def update_rects(self):
        self.rect = self.image.get_rect()
        self.collision_rect = self.image.get_bounding_rect()
        self.rect.center = self.collision_rect.center = self.pos

    def update_environment(self):
        self.terrain = "null"

    def turn(self):
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
        player = self.registry.get_group("player").sprite
        if player is not None and self.turn_type == self.TTYPE_FOLLOW:
            self.desired_velocity = self.desired_velocity.slerp(
                player.pos - self.pos, 0.02
            ).clamp_magnitude(self.SPEED)
        else:
            self.desired_velocity.rotate_ip(self.turn_speed)
        self.update_rects()
        super().update_behaviour(dt)


class EelBody(Enemy):
    SPEED = 32

    def __init__(self, data, leader):
        data.surface = asset_handler.glob_loader.load_spritesheet("eel.png", (16, 16))[
            -1
        ]
        self.leader = leader
        super().__init__(data)

    def update_behaviour(self, dt):
        self.desired_velocity = self.leader.pos - self.pos
        super().update_behaviour(dt)

    def update_environment(self):
        self.terrain = "null"


class EelTail(Enemy):
    SPEED = 32

    def __init__(self, data, leader):
        frames = asset_handler.glob_loader.load_spritesheet("tail.png", (16, 16))
        flip = pygame.transform.flip
        anim_dict = {
            "up": flip(frames[2], False, True),
            "right_up": flip(frames[1], True, True),
            "right": flip(frames[0], True, False),
            "right_down": flip(frames[1], True, False),
            "down": frames[2],
            "left_down": frames[1],
            "left": frames[0],
            "left_up": flip(frames[1], False, True),
            "still": frames[0],
        }
        super().__init__(data, anim_dict)
        self.leader = leader

    def update_behaviour(self, dt):
        self.desired_velocity = self.leader.pos - self.pos
        super().update_behaviour(dt)

    def update_environment(self):
        self.terrain = "null"

    def get_anim_key(self):
        return util.string_direction(-self.velocity)


class Fish(Enemy):
    SPEED = 6

    def __init__(self, data):
        data.image = util.circle_surf(6, "chartreuse")
        super().__init__(data)

    def update_behaviour(self, dt):
        if self.registry.get_group("player").sprite:
            self.desired_velocity = (
                self.registry.get_group("player").sprite.pos - self.pos
            ).clamp_magnitude(self.SPEED)
        super().update_behaviour(dt)
