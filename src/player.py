import pygame

import common
from bush import entity, physics, timer, util


class Player(entity.Actor):
    SPEED = 64
    SWIM_SPEED = 32
    registry_groups = ("main", "collision", "player")

    def __init__(self, pos):
        super().__init__(pos, util.rect_surf((0, 0, 16, 16), "red"))
        self.force = pygame.Vector2()
        self.terrain = "water"
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, pygame.sprite.Group()
        )
        self.collision_rect = self.rect.copy()
        self.boost_cooldown = timer.Timer(600)
        self.boost_cooldown.finish()
        self.map_cooldown = timer.Timer(700)
        self.current_health = 12
        self.health_capacity = 12

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
        self.force = pygame.Vector2()
        if keys[pygame.K_UP]:
            self.force.y -= speed
        if keys[pygame.K_DOWN]:
            self.force.y += speed
        if keys[pygame.K_LEFT]:
            self.force.x -= speed
        if keys[pygame.K_RIGHT]:
            self.force.x += speed
        if keys[pygame.K_LSHIFT]:
            self.up()
        if keys[pygame.K_LCTRL]:
            self.down()

        traction = common.TERRAINS[self.terrain]["traction"]
        self.velocity = (self.force * traction) + (self.velocity * (1 - traction))
        self.velocity += common.TERRAINS[self.terrain]["flow"]

    def update(self, dt):
        self.handle_input()
        super().update(dt)
        physics.dynamic_update(self, dt)
        if self.terrain != "underwater":
            for terrain in common.TERRAINS:
                terrain_mask = self.registry.get_mask(terrain)
                if terrain_mask.get_at(self.pos):
                    self.terrain = terrain

    def reset(self, pos, layer, registry, underwater):
        self.pos = pos
        self.update_rects()
        self.kill()
        self.layer = layer
        self.registry = registry
        self.add([self.registry.get_group(i) for i in self.registry_groups])
        self.physics_data = physics.PhysicsData(
            physics.TYPE_DYNAMIC, self.registry.get_group("collision")
        )
        self.terrain = (self.terrain, "water")[underwater]
