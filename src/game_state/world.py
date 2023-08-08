import pygame

import common
import gui
import map_loader
import modulate
from bush import particle
from game_state import base

map_loader = map_loader.MapLoader()


class MapState(base.GameState):
    def __init__(
        self,
        filename,
        registry,
        bg,
        above=None,
        below=None,
        soundtrack=None,
        modulate=False,
    ):
        self.registry = registry
        self.main_group = self.registry.get_group("main")
        self.soundtrack = soundtrack
        self.particle_manager = particle.ParticleManager()
        self.bg = bg
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
        rect = pygame.Rect(4, 0, 64, 10)
        rect.bottom = common.SCREEN_SIZE[1] - 4
        gui.Inventory(common.ITEM_IMAGES, player.get_inventory, rect, 1, hud)
        super().__init__(filename, gui=hud)
        self.filename = filename
        self.above = above
        self.below = below
        self.modulate = modulate
        if self.modulate:
            self.modulation_offset = common.WAVE_DATA["amplitude"] * 4
            self.to_modulate = pygame.Surface(
                common.SCREEN_SIZE + (self.modulation_offset * 2, 0)
            )

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
        if event.type == common.MAP_SWITCH:
            switch_map(self._stack, event.name, event.pos)
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
        self.main_group.update_rects()
        draw_pos = -pygame.Vector2(self.main_group.cam_rect.topleft)
        self.bg.pos.update(*draw_pos)
        if self.modulate:
            self.to_modulate.blit(self.bg.image, (0, 0))
            self.main_group.draw(self.to_modulate)
            surface.blit(
                modulate.modulate(self.to_modulate, pygame.time.get_ticks() / 1000),
                (-self.modulation_offset, 0),
            )
        else:
            surface.blit(self.bg.image, (0, 0))
            self.main_group.draw(surface)
        super().draw(surface)


def switch_map(stack, name, player_pos=None, pop=True):
    if pop:
        stack.pop()
    print("loading", name)
    registry, properties, bg = map_loader.load(name, player_pos)
    stack.push(
        MapState(
            name,
            registry,
            bg,
            properties.get("above", None),
            properties.get("below", None),
            modulate="underwater" in properties.get("area", "inside"),
        )
    )
    track = properties.get("track", None)
    if track is not None:
        common.switch_track(track)
    return registry, properties
