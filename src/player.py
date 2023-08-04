from bush import entity, util, physics, timer
import pygame
import common


class Player(entity.Actor):
    SPEED = 64
    SWIM_SPEED = 32

    def __init__(self, pos):
        super().__init__(
            pos, util.rect_surf((0, 0, 16, 16), 'red')
        )
        self.force = pygame.Vector2()
        self.terrain = "water"
        self.physics_data = physics.PhysicsData(physics.TYPE_DYNAMIC, pygame.sprite.Group())
        self.boost_cooldown = timer.Timer(600)
        self.boost_cooldown.finish()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.boost_cooldown.done():
            self.velocity += {
                pygame.K_UP: pygame.Vector2(0, -1),
                pygame.K_DOWN: pygame.Vector2(0, 1),
                pygame.K_LEFT: pygame.Vector2(-1, 0),
                pygame.K_RIGHT: pygame.Vector2(1, 0),
            }.get(event.key, pygame.Vector2()) * common.TERRAINS[self.terrain]["boost"]
            self.boost_cooldown.reset()


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

        traction = common.TERRAINS[self.terrain]["traction"]
        self.velocity = (self.force * traction) + (self.velocity * (1 - traction))
        self.velocity += common.TERRAINS[self.terrain]["flow"]

    def update(self, dt):
        self.handle_input()
        super().update(dt)
        physics.dynamic_update(self, dt)
