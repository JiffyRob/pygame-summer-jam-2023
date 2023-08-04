import pygame

from bush import asset_handler, event_binding, sound_manager
from bush.ai import state


class GameState(state.StackState):
    music_player = sound_manager.music_player
    loader = asset_handler.glob_loader
    save_ext = ".json"

    def __init__(
        self,
        value,
        on_push=lambda: None,
        on_pop=lambda: None,
        gui=None,
        enable_cursor=False,
    ):
        self.cursor = pygame.Cursor()
        self.screen_surf = None
        self.gui = gui
        self.enable_cursor = enable_cursor
        super().__init__(value, on_push, on_pop)

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        if self.gui:
            self.gui.process_events(event)

    def cache_screen(self):
        self.screen_surf = pygame.display.get_surface().copy()

    def draw(self, surface):
        if self.gui:
            self.gui.draw_ui(surface)

    def update(self, dt=0.03):
        super().update()
        if self.gui is not None:
            self.gui.update(dt)
