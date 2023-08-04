import pygame

import arg
import common
import game_object
from bush import physics, timer, util


class Player(game_object.MobileGameObject):
    SPEED = 64
    SWIM_SPEED = 32
    true_groups = ("main", "collision", "player", "scriptable")
    registry_groups = ()

    def __init__(self, pos):
        data = arg.GameObjectArgs(pos, surface=util.rect_surf((0, 0, 16, 16), "red"))
        super().__init__(data, start_health=12, max_health=12)
        self.terrain = "water"
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, pygame.sprite.Group()
        )
        self.collision_rect = self.rect.copy()
        self.boost_cooldown = timer.Timer(600)
        self.boost_cooldown.finish()
        self.map_cooldown = timer.Timer(700)

    def update_rects(self):
        self.rect.center = self.collision_rect.center = self.pos

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.boost_cooldown.done():
            self.velocity += {
                pygame.K_UP: pygame.Vector2(0, -1),
                pygame.K_DOWN: pygame.Vector2(0, 1),
                pygame.K_LEFT: pygame.Vector2(-1, 0),
                pygame.K_RIGHT: pygame.Vector2(1, 0),
            }.get(event.key, pygame.Vector2()) * common.TERRAINS[self.terrain]["boost"]
            self.boost_cooldown.reset()

    def up(self):
        if "water" in self.terrain and self.map_cooldown.done():
            pygame.event.post(pygame.Event(common.LAYER_UP))
            self.map_cooldown.reset()

    def down(self):
        if "water" in self.terrain and self.map_cooldown.done():
            pygame.event.post(pygame.Event(common.LAYER_DOWN))
            self.map_cooldown.reset()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        speed = common.TERRAINS[self.terrain]["speed"]
        self.desired_velocity = pygame.Vector2()
        if keys[pygame.K_UP]:
            self.desired_velocity.y -= 1
        if keys[pygame.K_DOWN]:
            self.desired_velocity.y += 1
        if keys[pygame.K_LEFT]:
            self.desired_velocity.x -= 1
        if keys[pygame.K_RIGHT]:
            self.desired_velocity.x += 1
        if self.desired_velocity:
            self.desired_velocity.scale_to_length(speed)
        if keys[pygame.K_LSHIFT]:
            self.up()
        if keys[pygame.K_LCTRL]:
            self.down()

        traction = common.TERRAINS[self.terrain]["traction"]
        self.velocity = (self.desired_velocity * traction) + (
            self.velocity * (1 - traction)
        )
        self.velocity += common.TERRAINS[self.terrain]["flow"]

    def kill(self, game_over=True):
        if game_over:
            pygame.event.post(pygame.Event(common.GAME_OVER))
        else:
            super().kill()

    def update(self, dt):
        self.handle_input()
        super().update(dt)
        if self.terrain != "underwater":
            for terrain in common.TERRAINS:
                terrain_mask = self.registry.get_mask(terrain)
                if terrain_mask.get_at(self.pos):
                    self.terrain = terrain

    def reset(self, pos, layer, registry, underwater):
        self.pos = pos
        self.update_rects()
        self.kill(False)
        self.layer = layer
        self.registry = registry
        self.add([self.registry.get_group(i) for i in self.true_groups])
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, self.registry.get_group("collision")
        )
        self.terrain = (self.terrain, "water")[underwater]

    def new_game(self):
        self.heal(100000)
