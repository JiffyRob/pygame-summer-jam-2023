import game_object
from bush import animation, asset_handler

NPC_LENGTHS = (
    200,
    200,
    100,
    250,
    250,
    250,
    250,
    250,
    250,
    250,
    250,
    100,
    100,
    100,
    500,
    500,
)
NPC_FRAMES = asset_handler.glob_loader.load_spritesheet("npcs.png")


class NPC(game_object.GameObject):
    registry_groups = ("main", "collision", "interactable", "scriptable")

    def __init__(self, data, anim_dict):
        super().__init__(data, anim_dict)
        self.script = data.misc.get("script")

    def interact(self):
        if not self.script_stack:
            self.run_script(self.script)
        self.state = "transition"

    def update_state(self, dt):
        if self.state == "transition" and self.anim.done():
            self.state = "talking"
        if self.state == "transition_reverse" and self.anim.done():
            self.state = "idle"
            for key in {"transition", "transition_reverse"}:
                self.anim_dict[key].reset()
        if not self.script_stack and self.state == "talking":
            self.state = "transition_reverse"


class OldMan(NPC):
    def __init__(self, data):
        anim_dict = {
            "idle": animation.Animation(NPC_FRAMES[3:7], NPC_LENGTHS[3:7]),
            "transition_reverse": animation.OnceAnimation(
                NPC_FRAMES[1:4], NPC_LENGTHS[1:4]
            ),
            "transition": animation.OnceAnimation(
                NPC_FRAMES[3:0:-1], NPC_LENGTHS[3:0:-1]
            ),
            "talking": animation.Animation(NPC_FRAMES[:2], NPC_LENGTHS[:2]),
        }
        data.misc["script"] = "old-man.snk"
        super().__init__(data, anim_dict)


class Tinker(NPC):
    def __init__(self, data):
        anim_dict = {
            "idle": animation.Animation(NPC_FRAMES[7:11], NPC_LENGTHS[7:11]),
            "transition": animation.OnceAnimation(
                NPC_FRAMES[10:15], NPC_LENGTHS[10:15]
            ),
            "transition_reverse": animation.OnceAnimation(
                NPC_FRAMES[14:9:-1], NPC_LENGTHS[14:9:-1]
            ),
            "talking": animation.Animation(NPC_FRAMES[14:16], NPC_LENGTHS[14:16]),
        }
        data.misc["script"] = "tinker.snk"
        super().__init__(data, anim_dict)
