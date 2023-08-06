import pygame

import common
import snek
from bush import asset_handler, util


class Dialog(snek.SnekCommand):
    def __init__(self, prompt, *answers):
        super().__init__()
        pygame.event.post(
            pygame.Event(
                common.DIALOG,
                {"prompt": prompt, "answers": answers, "on_kill": self.finish},
            )
        )
        self.value = snek.UNFINISHED

    def get_value(self):
        return self.value

    def finish(self, answer):
        self.value = answer


class Script:
    loader = asset_handler.AssetHandler("scripts")

    def __init__(self, this, registry, script):
        self.registry = registry
        namespace = {
            "THIS": this,
            "MACHINERY_1": "machinery1",
            "MACHINERY_2": "machinery2",
            "MACHINERY_3": "machinery3",
            "MACHINERY_4": "machinery4",
            "MACHINERY_5": "machinery5",
        }
        api = {
            # player interaction
            "heal": snek.snek_command(self.registry.get_group("player").sprite.heal),
            "hurt": snek.snek_command(self.registry.get_group("player").sprite.hurt),
            "dialog": Dialog,
            "take_machinery": snek.snek_command(
                self.registry.get_group("player").sprite.give_machinery
            ),
            "fix_with_tech": snek.snek_command(lambda tech: print("Fixing with", tech)),
            # vector operation
            "vec": snek.snek_command(lambda *args: pygame.Vector2(*args)),
            "norm": snek.snek_command(lambda vec: vec.copy() or vec.normalize()),
            "randinrect": snek.snek_command(util.randinrect),
            "randincircle": snek.snek_command(util.randincircle),
            "direc": snek.snek_command(util.direction),
            # sprite operation
            "move": self.move,
            "immobilize": self.immobilize,
            "mobilize": self.mobilize,
            "face": self.face,
            "get_velocity": snek.snek_command(
                lambda sprite_id: self.get_sprite(sprite_id).velocity
            ),
        }
        self.program = snek.SNEKProgram(self.loader.load(script), namespace, api)

    def get_sprite(self, sprite_id):
        return self.registry.get_group("scriptable").get_by_id(sprite_id)

    @snek.snek_command
    def move(self, sprite_id, veloc):
        self.get_sprite(sprite_id).desired_velocity = veloc

    @snek.snek_command
    def immobilize(self, sprite_id):
        self.get_sprite(sprite_id).immobilize()

    @snek.snek_command
    def mobilize(self, sprite_id):
        self.get_sprite(sprite_id).mobilize()

    @snek.snek_command
    def face(self, sprite_id, direction):
        self.get_sprite(sprite_id).face(direction)

    def update(self, dt):
        self.program.cycle()

    def finished(self):
        return not self.program.running
