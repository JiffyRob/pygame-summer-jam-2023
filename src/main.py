from bush import asset_handler

asset_handler.AssetHandler.set_global_home("assets")
asset_handler.glob_loader.base = asset_handler.AssetHandler.base

import asyncio

import pygame

import common
import player
from bush import util
from bush.ai import state
from game_state import ui


class Game:
    FLAGS = pygame.SCALED | pygame.RESIZABLE
    BG_COLOR = "blue"
    FPS = 30 * (not util.is_pygbag())
    VSYNC = 1

    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.stack = state.StateStack()
        self.player = player.Player(common.SCREEN_SIZE / 2)

    def quit(self):
        self.running = False

    async def run(self):
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
                state.handle_event(event)

            self.screen.fill(self.BG_COLOR)

            state.update(dt)
            state.draw(self.screen)

            pygame.display.flip()
            await asyncio.sleep(0)
            dt = self.clock.tick(self.FPS) / 1000


if __name__ == "__main__":
    asyncio.run(Game().run())
