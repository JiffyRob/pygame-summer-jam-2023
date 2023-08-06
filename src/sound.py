import pygame


class ChannelRack:
    def __init__(self, channels):
        self._free_channels = [pygame.mixer.Channel(i) for i in range(channels)]
        self._free_channels = [i for i in self._free_channels if i is not None]
        self._used_channels = []

    def _get_least_priority(self):
        return sorted(self._used_channels, key=lambda x: x[0])[0]

    def allocate_channel(self, priority):
        self.free_done()
        if self._free_channels:
            print("using a free channel")
            channel = self._free_channels.pop(-1)
            self._used_channels.append([priority, channel])
        else:
            channel_data = self._get_least_priority()
            least_priority, channel = channel_data
            if priority > least_priority:
                print("overriding a low priority channel")
                channel.stop()
                channel_data[0] = priority
        print(self._free_channels, self._used_channels)
        return channel

    def free_done(self):
        to_free = []
        for channel_data in self._used_channels:
            if not channel_data[1].get_busy():
                to_free.append(channel_data)
        for channel_data in to_free:
            self._used_channels.remove(channel_data)
            self._free_channels.append(channel_data[1])


class SoundManager:
    def __init__(self, loader, channels=8):
        self._channel_rack = ChannelRack(channels)
        self.loader = loader
        self.current_track = None
        self.sound_volume = 1
        self.music_volume = 1

    def play_sound(
        self, path, priority=10, loops=0, volume=1, fade_ms=0, polar_location=(0, 0)
    ):
        sound = self.loader.load(path)
        channel = self._channel_rack.allocate_channel(priority)
        if channel is not None:  # if all channels are in use and of higher priority
            channel.set_source_location(*polar_location)
            channel.set_volume(volume * self.sound_volume)
            channel.play(sound, loops, 0, fade_ms)
        return channel is not None

    def set_sound_volume(self, value):
        self.sound_volume = pygame.math.clamp(value, 0, 1)
        return self.sound_volume

    def get_sound_value(self):
        return self.sound_volume

    def set_music_volume(self, value):
        self.music_volume = pygame.math.clamp(value, 0, 1)
        return self.music_volume

    def get_music_volume(self, value):
        return self.music_volume

    def switch_track(self, track, volume=1, loops=0, start=0.0, fade_ms=0):
        track = self.loader.join(track)
        if track != self.current_track:
            pygame.mixer.music.set_volume(self.music_volume * volume)
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(loops, start, fade_ms)
            self.current_track = track


if __name__ == "__main__":
    from bush import asset_handler

    pygame.init()
    pygame.display.set_mode((100, 100))
    loader = asset_handler.AssetHandler("assets/music")

    manager = SoundManager(loader, 2)
    # pygame.time.delay(10000000)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("play sound")
                    manager.play_sound("Alert2.wav", 10, 0, 0.6, 1000)
                if event.key == pygame.K_DOWN:
                    print("play sound")
                    manager.play_sound("Alert2.wav", 5, 0, 0.6, 1000)
                if event.key == pygame.K_LEFT:
                    manager.switch_track("jam-overworld.wav", 0.3, -1, fade_ms=1000)
                if event.key == pygame.K_RIGHT:
                    manager.switch_track("Undersea.mp3", 0.3, -1, fade_ms=1000)
        pygame.display.flip()
        clock.tick(60)
