from dataclasses import dataclass, field
from typing import Any

import pygame

from bush import animation
from bush.mapping import registry as registry_lib


@dataclass
class GameObjectArgs:
    pos: pygame.Vector2 = field(default_factory=pygame.Vector2)
    registry: registry_lib.MapRegistry = registry_lib.MapRegistry()
    surface: pygame.Surface | animation.Animation | None = None
    id: Any = None
    layer: int = 4
    topleft: bool = False
    misc: dict | None = None


def from_mapping_object(obj, registry):
    return GameObjectArgs(
        pos=obj.pos,
        registry=registry,
        surface=obj.image,
        id=obj.name,
        layer=obj.layer * 3 + 1,
        topleft=True,
        misc={"width": obj.width, "height": obj.height, **obj.properties},
    )
