import os

import pygame

import common
import gui
import map_loader
from bush import event_binding, particle, timer, util
from game_state import base, ui

map_loader = map_loader.MapLoader()


class MapState(base.GameState):
    def __init__(self, filename, registry, above=None, below=None, soundtrack=None):
        self.registry = registry
        self.main_group = self.registry.get_group("main")
        self.soundtrack = soundtrack
        self.particle_manager = particle.ParticleManager()
        if self.soundtrack is not None:
            self.music_player.play(self.soundtrack)
        hud = gui.UIGroup()
        player = registry.get_group("player").sprite
        gui.BarMeter(
            lambda: (player.current_health, player.health_capacity),
            pygame.Rect(4, 4, 64, 6),
            1,
            hud,
            bar_color="green",
        )
        gui.BarMeter(
            lambda: (player.oxygen, player.max_oxygen),
            pygame.Rect(4, 12, 48, 6),
            1,
            hud,
            bar_color="white",
        )
        super().__init__(filename, gui=hud)
        self.filename = filename
        self.above = above
        self.below = below

    def update(self, dt=0.03):
        super().update(dt)
        self.particle_manager.update(dt)
        self.main_group.update(dt)

    def update_map(self):
        pass

    def handle_event(self, event):
        if event.type == common.LAYER_DOWN:
            self.layer_down()
        if event.type == common.LAYER_UP:
            self.layer_up()
        if event.type == common.GAME_OVER:
            self.pop()
            map_loader.clear_cache()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pygame.event.post(pygame.Event(common.PAUSE))
        return super().handle_event(event)

    def layer_up(self):
        if self.above is not None:
            switch_map(
                self._stack, self.above, self.registry.get_group("player").sprite.pos
            )

    def layer_down(self):
        if self.below is not None:
            switch_map(
                self._stack, self.below, self.registry.get_group("player").sprite.pos
            )

    def draw(self, surface):
        self.main_group.draw(surface)
        if self.main_group.debug_physics:
            pygame.draw.rect(
                surface,
                (255, 0, 0),
                globals.player.get_interaction_rect().move(
                    -pygame.Vector2(self.main_group.cam_rect.topleft)
                ),
                1,
            )
        self.particle_manager.draw(
            surface, -pygame.Vector2(self.main_group.cam_rect.topleft)
        )
        super().draw(surface)


def switch_map(stack, name, player_pos=None, pop=True):
    if pop:
        stack.pop()
    print("loading", name)
    registry, properties = map_loader.load(name, player_pos)
    stack.push(
        MapState(
            name,
            registry,
            properties.get("above", None),
            properties.get("below", None),
        )
    )
    return registry, properties
