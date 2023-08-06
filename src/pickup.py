import game_object


class Pickup(game_object.GameObject):
    registry_groups = ("main", "pickups")

    def __init__(self, data):
        super().__init__(data)

    def pickup(self):
        pass


class Key(Pickup):
    def pickup(self):
        if self.registry.get_group("player").sprite.get_key():
            self.kill()


class Machinery(Pickup):
    def __init__(self, data):
        super().__init__(data)
        self.value = data.misc["value"]
        print("this gadget is a", self.value)

    def pickup(self):
        if self.registry.get_group("player").sprite.get_machinery(self.value):
            self.kill()


class Oxygen(Pickup):
    def pickup(self):
        if self.registry.get_group("player").sprite.refill_oxygen():
            self.kill()


class Health(Pickup):
    def pickup(self):
        if self.registry.get_group("player").sprite.heal(3):
            self.kill()
