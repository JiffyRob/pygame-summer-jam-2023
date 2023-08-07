import pygame

import common
import menu
from bush import util
from game_state import base


class MenuState(base.GameState):
    def __init__(
        self,
        value,
        on_push=None,
        on_pop=None,
        supermenu=None,
        screen_surf=None,
    ):
        if on_push is None:
            on_push = lambda: None
        if on_pop is None:
            if supermenu is None:
                on_pop = lambda: None
            else:
                on_pop = lambda: supermenu.rebuild()
        super().__init__(value, on_push, on_pop, enable_cursor=True)
        self.screen_surf = screen_surf
        if supermenu is not None and self.screen_surf is None:
            self.screen_surf = supermenu.screen_surf
        self.nothing_func = lambda: None
        self.rebuild()
        self.supermenu = supermenu

    def rebuild(self):
        self.gui = None

    def draw(self, surface):
        if self.screen_surf is not None:
            surface.blit(self.screen_surf, (0, 0))
        super().draw(surface)

    def handle_event(self, event):
        super().handle_event(event)

    def run_submenu(self, menu_type, **kwargs):
        self._stack.push(menu_type(supermenu=self, **kwargs))


class PauseMenu(MenuState):
    def __init__(self, screen_surf):
        super().__init__(
            "PauseMenu",
            screen_surf=screen_surf,
        )

    def quit(self):
        pygame.event.post(pygame.event.Event(common.GAME_OVER))

    def rebuild(self):
        self.gui = menu.create_menu(
            "PauseMenu",
            ["Resume", "Quit"],
            [self.pop, self.quit],
            common.SCREEN_SIZE,
        )


class MainMenu(MenuState):
    def __init__(self):
        self.button_list = ("Play", "Exit")
        if util.is_pygbag():
            self.button_list = self.button_list[:-1]
        super().__init__(
            "MainMenu",
            screen_surf=util.rect_surf((0, 0, *common.SCREEN_SIZE), "turquoise"),
        )

    def rebuild(self):
        self.gui = menu.create_menu(
            "Atlantica",
            self.button_list,
            [self.play, self.pop],
            common.SCREEN_SIZE,
        )

    def play(self):
        pygame.event.post(pygame.Event(common.GAME_START))
        self.rebuild()

    def pop(self):
        if util.is_pygbag():
            return  # No quit in pygbag
        super().pop()
