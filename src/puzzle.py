import pygame

import game_object
import player
from bush import asset_handler, entity, physics, util


class Communicator(game_object.MobileGameObject):
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
        if physics_data is None:
            physics_data = physics.PhysicsData(
                physics.TYPE_DYNAMIC, data.registry.get_group("collision")
            )
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

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC:
            physics.resolve_collision(other, self)

    def receive_signal(self, signal):
        pass

    def send_signal(self, signal):
        group = self.registry.get_group("communicators")
        for receiver in self.receivers:
            sprite = group.get_by_id(receiver)
            sprite.receive_signal(signal)


class BiStateCommunicator(Communicator):
    DEFAULT_START_STATE = True
    FORCE_SWITCH = False
    SEND_DATA = False

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
        self.state = self.last_state = bool(
            data.misc.get("start_state", self.DEFAULT_START_STATE)
        )
        self.on_switch()

    def update_state(self, dt):
        pass

    def get_anim_key(self):
        return self.state

    def receive_signal(self, signal):
        self.state = (bool(signal), not self.state)[self.FORCE_SWITCH]

    def on_switch(self):
        pass

    def update(self, dt):
        super().update(dt)
        if self.last_state != self.state:
            if self.SEND_DATA:
                self.send_signal(self.state)
            self.on_switch()
        self.last_state = self.state


class Pushblock(BiStateCommunicator):
    PUSH_SPEED = 16
    registry_groups = ("main", "collision", "communicators")

    def __init__(self, data):
        tiles = asset_handler.glob_loader.load_spritesheet("tiled/puzzle.png", (16, 16))
        anim_dict = {
            True: data.surface,
            False: tiles[3],
        }
        self.push_directions = [
            util.string_direction_to_vec(i)
            for i in data.misc.get("push_directions", "up, down, left, right").split(
                ", "
            )
        ]
        super().__init__(
            data,
            anim_dict=anim_dict,
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, data.registry.get_group("collision")
            ),
        )

    def on_switch(self):
        print("block to", self.state)

    def on_collision(self, other, dt):
        def get_push_direction(self, other):
            return util.direction_orthag(self.pos - other.pos)

        match other:
            # move slightly for player, if turned on
            # also move slightly for a pushblock that can move the rest
            case player.Player() | Pushblock(state=True) if get_push_direction(
                other, self
            ) in other.push_directions:
                push_direction = get_push_direction(self, other)
                if self.state and push_direction in self.push_directions:
                    veloc = pygame.Vector2(push_direction)
                    veloc.scale_to_length(self.PUSH_SPEED * dt)
                    self.pos += veloc
                    self.update_rects()
                physics.resolve_collision(other, self)
                physics.dynamic_update(other, 0, False)
                physics.dynamic_update(self, 0, False)
            # I smashed into something static
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_STATIC, _)
            ):
                physics.resolve_collision(self, other)
            # Communicators are weird
            case Communicator(
                physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, _)
            ):
                physics.resolve_collision(self, other)
            case entity.Entity(
                physics_data=physics.PhysicsData(physics.TYPE_DYNAMIC, _)
            ):
                physics.resolve_collision(other, self)


class Drifter(BiStateCommunicator):
    registry_groups = ("main", "collision", "communicators")

    def __init__(self, data):
        anim_dict = None
        if not isinstance(data.surface, pygame.Surface):
            anim_dict = {
                True: data.surface,
                False: data.surface.image(),
            }

        super().__init__(
            data,
            anim_dict=anim_dict,
            physics_data=physics.PhysicsData(
                physics.TYPE_TRIGGER, data.registry.get_group("collision")
            ),
        )
        self.direction = pygame.Vector2(
            [int(i) for i in data.misc.get("direction", "0, 0").split(", ")]
        )

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC and self.state:
            other.drift(self.direction)


class ZapPortal(BiStateCommunicator):
    DEFAULT_START_STATE = False
    SEND_DATA = True
    registry_groups = ("main", "interactable", "communicators", "collision")

    def __init__(self, data):
        tiles = asset_handler.glob_loader.load_spritesheet("tiled/puzzle.png", (16, 16))
        anim_dict = {
            "off right": tiles[4],
            "off down": tiles[5],
            "off left": tiles[6],
            "on down": tiles[7],
            "on right": tiles[12],
            "off up": tiles[13],
            "on left": tiles[14],
            "on up": tiles[15],
        }
        super().__init__(data, anim_dict)
        self.facing = data.misc["facing"]

    def get_anim_key(self):
        return f"{('off', 'on')[self.state]} {self.facing}"

    def interact(self):
        self.state = not self.state


class Zap(BiStateCommunicator):
    DEFAULT_START_STATE = False
    registry_groups = ("main", "collision", "communicators")

    def __init__(self, data):
        super().__init__(
            data,
            anim_dict={
                False: data.surface,
                True: pygame.Surface((0, 0)),
            },
            physics_data=physics.PhysicsData(
                physics.TYPE_DYNAMIC, data.registry.get_group("collision")
            ),
        )
        self.mask = pygame.mask.from_surface(self.image)

    def on_collision(self, other, dt):
        if not self.state:
            physics.resolve_collision(other, self)


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
            initial_state=False,
        )
        self.last_state = self.state

    def update_state(self, dt):
        if self.state != self.last_state:
            print("pp signal", self.state)
            self.send_signal(self.state)
        self.last_state = self.state
        self.state = False

    def on_collision(self, other, dt):
        if other.physics_data.type == physics.TYPE_DYNAMIC and not self.state:
            self.state = True
            self.send_signal(self.state)


class Switch(BiStateCommunicator):
    registry_groups = ("main", "collision", "communicators", "interactable")

    def __init__(self, data):
        tiles = asset_handler.glob_loader.load_spritesheet("tiled/puzzle.png", (16, 16))
        anim_dict = {True: tiles[8], False: tiles[9]}
        super().__init__(data, anim_dict=anim_dict)
        self.state = data.misc.get("start-state", False)

    def interact(self):
        self.state = not self.state
        self.send_signal(self.state)


class Lock(Communicator):
    registry_groups = ("main", "collision", "communicators", "interactable")

    def __init__(self, data):
        tiles = asset_handler.glob_loader.load_spritesheet("tiled/puzzle.png", (16, 16))
        anim_dict = {True: tiles[10], False: tiles[11]}
        super().__init__(data, anim_dict, initial_state=False)

    def get_anim_key(self):
        return self.state

    def interact(self):
        if self.registry.get_group("player").sprite.lose_key():
            self.state = True
            self.send_signal(True)
