from bush import asset_handler

asset_handler.AssetHandler.set_global_home("assets")
asset_handler.glob_loader.base = asset_handler.AssetHandler.base

import pygame

import common
import player
from bush.ai import state
from game_state import ui


class Game:
    FLAGS = pygame.SCALED | pygame.RESIZABLE
    BG_COLOR = "blue"
    FPS = 30
    VSYNC = True

    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.stack = state.StateStack()
        self.player = player.Player(common.SCREEN_SIZE / 2)

    def quit(self):
        self.running = False

    def run(self):
        self.screen = pygame.display.set_mode(
            common.SCREEN_SIZE, self.FLAGS, self.VSYNC
        )
        self.running = True
        self.stack.push(ui.MainMenu())
        self.clock.tick()
        dt = 0

        while self.running:
            state = self.stack.get_current()
            if state is None:
                self.quit()
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.player.handle_event(event)
                state.handle_event(event)

            self.screen.fill(self.BG_COLOR)

            state.update(dt)
            state.draw(self.screen)

            pygame.display.flip()
            dt = self.clock.tick(self.FPS) / 1000


if __name__ == "__main__":
    Game().run()
