import pygame

import arg
import common
import game_object
from bush import collision, physics, timer, util


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
        self.boost_cooldown = timer.Timer(300)
        self.boost_cooldown.finish()
        self.interaction_cooldown = timer.Timer(300)
        self.map_cooldown = timer.Timer(700)
        self.slowed = False
        self.mask = pygame.Mask(self.rect.size, True)
        self.interaction_rect = pygame.Rect(0, 0, 0, 0)
        self.keys = 0

    def update_rects(self):
        self.rect.center = self.collision_rect.center = self.pos
        match self.facing:
            case "up":
                self.interaction_rect = pygame.Rect(
                    self.rect.width,
                    self.rect.width,
                    self.rect.height / 2,
                    self.rect.height / 2,
                )
                self.interaction_rect.midbottom = self.rect.midtop
            case "down":
                self.interaction_rect = pygame.Rect(
                    self.rect.width,
                    self.rect.width,
                    self.rect.height / 2,
                    self.rect.height / 2,
                )
                self.interaction_rect.midtop = self.rect.midbottom
            case "left":
                self.interaction_rect = pygame.Rect(
                    self.rect.width / 2,
                    self.rect.width / 2,
                    self.rect.height,
                    self.rect.height,
                )
                self.interaction_rect.midright = self.rect.midleft
            case "right":
                self.interaction_rect = pygame.Rect(
                    self.rect.width / 2,
                    self.rect.width / 2,
                    self.rect.height,
                    self.rect.height,
                )
                self.interaction_rect.midleft = self.rect.midright

    def up(self):
        if "water" in self.terrain and self.map_cooldown.done():
            pygame.event.post(pygame.Event(common.LAYER_UP))
            self.map_cooldown.reset()

    def down(self):
        if "water" in self.terrain and self.map_cooldown.done():
            pygame.event.post(pygame.Event(common.LAYER_DOWN))
            self.map_cooldown.reset()

    def interact(self):
        def interaction_rect_collide(player, other):
            return player.interaction_rect.colliderect(other.rect)

        if self.interaction_cooldown.done():
            sprite = pygame.sprite.spritecollideany(
                self, self.registry.get_group("interactable"), interaction_rect_collide
            )
            if sprite is not None:
                sprite.interact()
                self.interaction_cooldown.reset()

    def get_key(self):
        if self.keys >= 3:
            return False
        self.keys += 1
        return True

    def lose_key(self):
        if self.keys <= 0:
            return False
        self.keys -= 1
        return True

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
        if keys[pygame.K_SPACE]:
            self.interact()
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
        for pickup in pygame.sprite.spritecollide(
            self,
            self.registry.get_group("pickups"),
            False,
            pygame.sprite.collide_rect_ratio(0.8),
        ):
            pickup.pickup()

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
