import pygame

import game_object
import player
from bush import entity, physics, util


class Pushblock(game_object.MobileGameObject):
    PUSH_SPEED = 16
    registry_groups = ("main", "collision")

    def on_collision(self, other, dt):
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

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC:
            other.drift(self.direction)
        else:
            print("can't collide with", other)


class Pickup(game_object.GameObject):
    registry_groups = ("main", "pickups")

    def __init__(self, data):
        super().__init__(data)

    def pickup(self):
        pass


class Key(Pickup):
    def pickup(self):
        if self.registry.get_group("player").sprite.get_key():
            self.kill()


class Communicator(game_object.GameObject):
    registry_groups = ("main", "communicators")

    def __init__(
        self,
        data,
        anim_dict=None,
        initial_state=None,
        physics_data=None,
        start_health=1,
        max_health=1,
        immunity=150,
        hit_effect=None,
    ):
        super().__init__(
            data,
            anim_dict,
            initial_state,
            physics_data,
            start_health,
            max_health,
            immunity,
            hit_effect,
        )
        if "receivers" in data.misc:
            self.receivers = data.misc["receivers"].split(", ")
        else:
            self.receivers = ()

    def receive_signal(self, signal):
        pass

    def send_signal(self, signal):
        group = self.registry.get_group("communicators")
        for receiver in self.receivers:
            sprite = group.get_by_id(receiver)
            sprite.receive_signal(signal)


class Door(Communicator):
    registry_groups = ("main", "collision", "interactable", "communicators")

    def __init__(self, data):
        super().__init__(
            data,
            anim_dict={
                "open": util.rect_surf((0, 0, 16, 16), "black", 1),
                "closed": util.rect_surf((0, 0, 16, 16), "black"),
            },
            initial_state="closed",
        )
        self.lock_type = data.misc.get("lock", "none")
        self.last_state = self.state

    def receive_signal(self, signal):
        self.state = ("closed", "open")[signal]

    def update_state(self, dt):
        super().update_state(dt)
        if self.last_state != self.state:
            if self.state == "open":
                self.mask.clear()
            if self.state == "closed":
                self.mask.fill()
        self.last_state = self.state

    def interact(self):
        match self.lock_type:
            case "none":
                self.state = "open"
            case "key":
                if self.registry.get_group("player").sprite.lose_key():
                    self.state = "open"
            case "trigger":
                print("trigger only")


class PressurePlate(Communicator):
    registry_groups = ("main", "collision", "communicators")

    def __init__(
        self,
        data,
    ):
        super().__init__(
            data,
            physics_data=physics.PhysicsData(
                physics.TYPE_TRIGGER, data.registry.get_group("collision")
            ),
        )
        self.was_down = False
        self.down = False

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC and not self.down:
            self.down = True
            self.send_signal(True)

    def update(self, dt):
        super().update(dt)
        if not self.down and self.was_down:
            self.send_signal(False)
        self.was_down = self.down
        self.down = False
