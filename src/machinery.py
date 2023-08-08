import pygame.mask

import common
from bush import asset_handler, entity, physics


class Machine(entity.Entity):
    registry_groups = ("main", "collision", "interactable")

    def __init__(self, data):
        img = asset_handler.glob_loader.load("parts.png")
        sub = img.subsurface
        self.parts = {
            "machinery1": (sub((0, 0, 16, 16)), (16, 16)),
            "machinery2": (sub((0, 30, 18, 16)), (46, 16)),
            "machinery3": (sub((0, 16, 22, 16)), (64, 16)),
            "machinery4": (sub((32, 16, 16, 8)), (70, 47)),
            "machinery5": (sub((0, 0, 0, 0)), (0, 0)),
        }
        data.surface = asset_handler.glob_loader.load("machine.png")
        print("dpos", data.pos)
        super().__init__(
            data.pos,
            data.surface,
            [data.registry.get_group(i) for i in self.registry_groups],
            "THE MACHINE",
            data.layer,
            data.topleft,
            True,
        )
        print(data.registry.get_group("THE MACHINE").sprite)
        self.physics_data = physics.PhysicsData(
            physics.TYPE_STATIC, data.registry.get_group("collision")
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.missing = set(self.parts.keys())
        self.fixed = False

    def update(self, dt):
        super().update(dt)
        for part in common.parts:
            self.image.blit(*self.parts[part])
            self.missing.remove(part)
        if not self.missing:
            self.fixed = True

    def interact(self):
        if self.fixed:
            pygame.event.post(
                pygame.Event(
                    common.DIALOG,
                    {
                        "prompt": "Looking at the readout, you realize that there is a bacteria in the water that can be taken out with simple antibiotics.  The planet is saved.",
                        "answers": (),
                        "on_kill": lambda x: 0,
                    },
                )
            )
        else:
            pygame.event.post(
                pygame.Event(
                    common.DIALOG,
                    {
                        "prompt": "Looks like it's still broken.",
                        "answers": (),
                        "on_kill": lambda x: 0,
                    },
                )
            )
