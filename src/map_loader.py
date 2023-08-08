import pygame

import arg
import common
import enemy
import npc
import pickup
import player
import puzzle
import pytmx
import teleport
from bush import animation, asset_handler, entity, physics
from bush.mapping import group, mapping, parallax


class MapLoader(mapping.MapLoader):
    def __init__(self):
        self.sprite_classes = {
            "eel": enemy.EelHead,
            "pushblock": puzzle.Pushblock,
            "conveyor": puzzle.Drifter,
            "pressure-plate": puzzle.PressurePlate,
            "key": pickup.Key,
            "switch": puzzle.Switch,
            "machinery": pickup.Machinery,
            "fish": enemy.Fish,
            "oxygen": pickup.Oxygen,
            "health": pickup.Health,
            "zap-portal": puzzle.ZapPortal,
            "zap": puzzle.Zap,
            "lock": puzzle.Lock,
            "old-man": npc.OldMan,
            "tinker": npc.Tinker,
            "teleport": teleport.Teleport,
        }
        self.player = None
        self.default_player_layer = 4  # second layer (default sub)
        self.mask_loader = asset_handler.AssetHandler("masks")
        self.map_size = None
        super().__init__(
            "tiled",
            sprite_creator=self.create_sprite,
            tile_handler=self.handle_tile,
            registry_creators={
                "main": lambda map_size: group.TopDownGroup(
                    common.SCREEN_SIZE,
                    map_size,
                    (0, 0),
                    self.player,
                    True,
                    debug_physics=False,
                ),
                "player": lambda x: pygame.sprite.GroupSingle(self.player),
                "collision": lambda x: pygame.sprite.Group(),
                "scriptable": lambda x: group.EntityGroup(),
                "interactable": lambda x: pygame.sprite.Group(),
                "communicators": lambda x: group.EntityGroup(),
                "enemies": lambda x: pygame.sprite.Group(),
                "pickups": lambda x: pygame.sprite.Group(),
            },
        )

    def handle_tile(self, tile, sprite_group):
        terrain = tile.properties.get("terrain", None)
        if tile.image is None:
            tile_image = pygame.Surface((0, 0))
        elif isinstance(tile.image, animation.Animation):
            tile_image = tile.image.image()
        else:
            tile_image = tile.image
        mask = tile.properties.get("mask", None) or pygame.mask.from_surface(tile_image)
        if terrain:
            if terrain not in self.current_registry.list_masks():
                self.current_registry.add_mask(terrain, pygame.Mask(self.map_size))
            self.current_registry.get_mask(terrain).draw(mask, tile.pos)
        groups = tile.properties.get("groups", "main").split(", ")
        sprite_groups = [self.current_registry.get_group(i) for i in groups]
        if groups:
            sprite = entity.Entity(
                tile.pos,
                pygame.Surface((16, 16), pygame.SRCALPHA),
                sprite_groups,
                topleft=True,
                no_debug=True,
            )
            if "collision" in groups:
                sprite.physics_data = physics.PhysicsData(
                    physics.TYPE_STATIC, self.current_registry.get_group("collision")
                )
                sprite.mask = mask

    def create_sprite(self, obj, sprite_group):
        if obj.type is None:
            groups = obj.properties.get("groups", "main").split(", ")
            sprite = entity.Entity(
                pos=obj.pos,
                layer=obj.layer * 3 + 1,
                groups=(*[self.current_registry.get_group(key) for key in groups],),
                id=obj.name,
                surface=obj.image,
                topleft=True,
            )
            if "collision" in groups:
                mask = obj.properties.get("mask", None)
                if mask is None:
                    mask = pygame.mask.from_surface(sprite.image)
                else:
                    mask = pygame.mask.from_surface(self.mask_loader.load(mask))
                sprite.physics_data = physics.PhysicsData(
                    physics.TYPE_STATIC, self.current_registry.get_group("collision")
                )
                sprite.mask = mask
            return
        obj.properties.pop("width", None)
        obj.properties.pop("height", None)
        if obj.name is not None:
            obj.properties["id"] = obj.name
        self.sprite_classes[obj.type](
            arg.from_mapping_object(obj, self.current_registry)
        )

    def load(self, tmx_map, player_pos=None):
        self.player = self.player or player.Player(common.SCREEN_SIZE)
        if not isinstance(tmx_map, pytmx.TiledMap):
            tmx_map = self.loader.load(tmx_map, self.cache_files)
        self.map_size = pygame.Vector2(
            tmx_map.width * tmx_map.tilewidth, tmx_map.height * tmx_map.tileheight
        )
        self.current_registry, properties = super().load(tmx_map)
        sprite_group = self.current_registry.get_group("main")
        if player_pos is None:
            player_pos = pygame.Vector2(
                [
                    int(i)
                    for i in tmx_map.properties.get("player_pos", "48, 48").split(", ")
                ]
            )
        self.player.reset(
            player_pos,
            properties.get("player_layer", self.default_player_layer),
            self.current_registry,
            "underwater" in properties.get("area", "inside"),
        )
        self.current_registry.get_group("main").add(sprite_group)

        physics.optimize_for_physics(self.current_registry.get_group("collision"))
        for key in common.TERRAINS:
            if key not in self.current_registry.list_masks():
                self.current_registry.add_mask(key, pygame.Mask(self.map_size))

        tiles = self.loader.load_spritesheet("tileset.png", (16, 16))
        map_type = properties.get("area")
        image = None
        parallax_factor = 0.75
        if map_type == "overworld":
            image = animation.Animation(tiles[100:104] + tiles[116:120], 100)
        if map_type == "underwater":
            image = tiles[39]
            parallax_factor = 0.25
        bg = entity.Entity((0, 0))
        if image:
            bg = parallax.LoopedSurface(image, parallax_factor, self.map_size, layer=-1)
        return (
            self.current_registry,
            properties,
            bg,
        )
