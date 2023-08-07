import pygame

import common
import script
from bush import animation, asset_handler, entity, physics, timer, util

loader = asset_handler.AssetHandler("sprites")
tile_loader = asset_handler.AssetHandler("tiled/tilesets")


class GameObject(entity.Actor):
    registry_groups = ("main",)

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
        self.anim_dict = {}
        if anim_dict is not None:
            self.anim_dict = anim_dict
        self.anim_dict = {
            key: value
            if isinstance(value, animation.Animation)
            else animation.Animation([value])
            for key, value in self.anim_dict.items()
        }
        surface = data.surface
        if surface is None and anim_dict is not None:
            surface = self.anim_dict[min(anim_dict.keys())].image()
        super().__init__(
            data.pos,
            surface,
            (data.registry.get_group(i) for i in self.registry_groups),
            data.id,
            data.layer,
            data.topleft,
        )
        self.registry = data.registry
        if initial_state is not None:
            self.state = initial_state
        elif self.anim_dict:
            self.state = "idle"
        else:
            self.state = None
        self.pushed_state = None
        if physics_data is not None:
            self.physics_data = physics_data
        else:
            self.physics_data = physics.PhysicsData(
                physics.TYPE_STATIC, self.registry.get_group("collision")
            )
        self.current_health = start_health
        self.health_capacity = max_health
        self.desired_velocity = pygame.Vector2()
        self.move_state = "walk"
        self.idle_state = "idle"
        self.facing = "down"
        self.immunity_time = immunity
        self.immunity_timer = timer.DTimer(immunity)
        self.immunity_timer.finish()
        self.visual_effects = []
        self.hit_effect = hit_effect
        self.script_stack = []
        self.mask = pygame.Mask(self.rect.size, True)

    def get_anim_key(self):
        return self.state

    def add_visual_effect(self, effect):
        self.visual_effects.append(effect)

    def heal(self, amount):
        if self.current_health >= self.health_capacity:
            return False
        self.current_health = min(self.health_capacity, self.current_health + amount)
        return True

    def hurt(self, amount):
        if self.immunity_timer.done():
            self.current_health -= amount
            if self.current_health <= 0:
                self.kill()
            self.immunify()

    def immunify(self):
        if self.hit_effect is not None:
            self.hit_effect.reset()
            self.add_visual_effect(self.hit_effect)
        self.immunity_timer.reset()

    def move(self, direction):
        self.desired_velocity = direction

    def stop(self):
        self.desired_velocity *= 0

    def run_script(self, script_name):
        self.script_stack.append(
            script.Script(self.get_id(), self.registry, script_name)
        )

    def update_state(self, dt):
        if self.desired_velocity:
            if self.state == self.idle_state:
                self.state = self.move_state
            self.facing = util.round_string_direction(
                util.string_direction(self.desired_velocity)
            )
        if not self.desired_velocity and self.state == self.move_state:
            self.state = self.idle_state
        if self.pushed_state:
            self.state = self.pushed_state

    def update_image(self, dt):
        if self.anim_dict:
            self.anim = self.anim_dict[self.get_anim_key()]
        if self.anim:
            self.image = self.anim.image()
        self.visual_effects = [e for e in self.visual_effects if not e.done()]
        for effect in self.visual_effects:
            effect.update(dt)
            self.image = effect.apply(self.image)

    def update_physics(self, dt):
        self.pos += self.velocity * dt
        self.update_rects()

    def update_behaviour(self, dt):
        pass

    def update_script(self, dt):
        if self.script_stack:
            self.script_stack[-1].update(dt)
            if self.script_stack[-1].finished():
                self.script_stack = self.script_stack[:-1]

    def update_rects(self):
        self.rect.center = self.pos

    def update(self, dt):
        self.update_state(dt)
        self.update_physics(dt)
        self.update_image(dt)
        self.update_behaviour(dt)
        self.update_script(dt)
        self.immunity_timer.update(dt)

    @staticmethod
    def spawn_particles(particles):
        ...  # TODO


class MobileGameObject(GameObject):
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
            data=data,
            anim_dict=anim_dict,
            initial_state=initial_state,
            physics_data=physics_data,
            start_health=start_health,
            max_health=max_health,
            immunity=immunity,
            hit_effect=hit_effect,
        )
        self.facing = "down"
        if physics_data is None:
            self.physics_data = physics.PhysicsData(
                physics.TYPE_DYNAMIC, self.registry.get_group("collision")
            )
        self.collision_rect = self.rect.copy()
        self.mobile = True
        self.terrain = "water"
        self.slowed = False
        self.drift_veloc = pygame.Vector2()

    def mobilize(self):
        self.mobile = True

    def immobilize(self):
        self.mobile = False

    def slow(self):
        self.slowed = True

    def drift(self, amount):
        self.drift_veloc += amount

    def face(self, dest):
        if isinstance(dest, str):
            self.facing = dest
        else:
            self.facing = util.string_direction(
                pygame.Vector2(util.direction_orthag(dest - self.pos))
            )

    def update(self, dt):
        self.update_environment()
        super().update(dt)
        self.update_rects()

    def update_rects(self):
        self.collision_rect.center = self.rect.center = self.pos

    def update_environment(self):
        if not self.terrain == "underwater":
            for key in common.TERRAINS:
                if self.registry.get_mask(key).get_at(self.pos):
                    self.terrain = key

    def get_anim_key(self):
        return f"{self.state} {self.facing}"

    def update_physics(self, dt):
        if self.physics_data.type == physics.TYPE_DYNAMIC:
            self.desired_velocity *= self.mobile
            if self.slowed:
                self.desired_velocity *= 0.7
                self.slowed = False
            # slippety-slide!
            traction = common.TERRAINS[self.terrain]["traction"]
            self.velocity = (
                (self.desired_velocity * traction)
                + self.velocity * (1 - traction)
                + self.drift_veloc
            )
            self.drift_veloc *= 0

            physics.dynamic_update(self, dt)
        self.update_rects()


def get_anim_dict(path, size):
    frames = loader.load_spritesheet(path + ".png", size)
    return {
        "walk down": animation.Animation(frames[0:16:4], 150),
        "walk up": animation.Animation(frames[1:17:4], 150),
        "walk left": animation.Animation(frames[2:18:4], 150),
        "walk right": animation.Animation(frames[3:18:4], 150),
        "idle down": animation.Animation(frames[0:1]),
        "idle up": animation.Animation(frames[1:2]),
        "idle left": animation.Animation(frames[2:3]),
        "idle right": animation.Animation(frames[3:4]),
    }


def load_tile(tile_index, tileset="objects", tile_size=(16, 16)):
    return tile_loader.load_spritesheet(tileset + ".png", tile_size)[tile_index]


def load_tiles(tile_indices, tileset="objects", tile_size=(16, 16)):
    tiles = []
    for tile_index in tile_indices:
        tiles.append(load_tile(tile_index, tileset, tile_size))
    return tiles
