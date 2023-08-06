import math

import pygame

from bush import asset_handler, event_binding, timer

loader = asset_handler.glob_loader

UI_FONT = pygame.font.Font(
    asset_handler.join(loader.base, "hud/TeenyTinyPixls.ttf"), 18
)

NUMBER_FONT = pygame.font.Font(
    asset_handler.join(loader.base, "hud/TeenyTinyPixls.ttf"), 5
)

HEART_IMAGES = loader.load_spritesheet("hud/heart.png")

# button states
STATE_NORMAL = 0
STATE_HOVERED = 1
STATE_CLICKED = 2

# dialog states
STATE_WRITING_PROMPT = 0
STATE_NEEDS_ADVNCED = 1
STATE_GETTING_ANSWER = 2
STATE_COMPLETE = 3

# colors (based on Ninja Adventure palette until palette is finalized)
BLACK = (20, 27, 27)
WHITE = (242, 234, 241)
LIGHT_GREY = (171, 194, 188)
LIGHT_BLUISH_GREY = (184, 220, 229)
DARK_GREY = (78, 82, 74)
BLUISH_GREEN = (74, 82, 112)

BUTTON_BACKGROUND_COLORS = (LIGHT_GREY, LIGHT_BLUISH_GREY, DARK_GREY)
BUTTON_TEXT_COLOR = BLACK
BG_COLOR = BLACK
BORDER_COLOR = BLUISH_GREEN
TEXT_COLOR = WHITE
COLORKEY = (0, 255, 0)

# anchor constants for the Text object
ANCHOR_TOPLEFT = 0
ANCHOR_MIDTOP = 1


class UIGroup(pygame.sprite.LayeredDirty):
    def draw_ui(self, surface):
        self.draw(surface)

    def process_events(self, event):
        for sprite in self.sprites():
            if sprite.pass_event(event):
                break


class UIElement(pygame.sprite.DirtySprite):
    def __init__(self, rect, layer, group):
        super().__init__()
        self.rect = rect
        self.layer = layer
        self.add(group)  # have to add to group after setting layer
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill(COLORKEY)
        self.image.set_colorkey(COLORKEY)
        self.dirty = 2  # dirty sprite function not currently implemented

    def pass_event(self, event):
        pass

    def rebuild(self):
        pass

    def update(self, dt):
        pass


class BGRect(UIElement):
    def __init__(self, rect, layer, group):
        super().__init__(rect, layer, group)
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill(BG_COLOR)
        pygame.draw.rect(self.image, BORDER_COLOR, ((0, 0), self.rect.size), 1)


class Text(UIElement):
    def __init__(self, text, anchor, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = text
        self.anchor = anchor
        self.rebuild()

    def set_text(self, text):
        self.text = text
        self.rebuild()

    def rebuild(self):
        self.image.fill(COLORKEY)
        text_surface = UI_FONT.render(
            self.text, False, TEXT_COLOR, COLORKEY, self.rect.width
        )
        text_rect = text_surface.get_rect()
        if self.anchor:
            text_rect.centerx = self.rect.centerx - self.rect.left
        self.image.blit(text_surface, text_rect.topleft)


class Descriptionbox(UIElement):
    def __init__(self, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = ""
        self.last_text = None
        self.rebuild()

    def set_text(self, text):
        self.text = text
        self.rebuild()

    def pass_event(self, event):
        pass

    def rebuild(self):
        self.image.fill(COLORKEY)
        pygame.draw.rect(self.image, BORDER_COLOR, ((0, 0), self.rect.size), 1)
        text_surface = UI_FONT.render(
            self.text, False, TEXT_COLOR, BG_COLOR, self.rect.width - 2
        )
        self.image.blit(text_surface, (1, 1))
        self.last_text = self.text


class Button(UIElement):
    def __init__(self, text, on_click, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = text
        self.text_surf = UI_FONT.render(self.text, False, BUTTON_TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(
            center=pygame.Vector2(self.rect.center) - self.rect.topleft
        )
        self.state = STATE_NORMAL
        self.on_click = on_click
        self.rebuild()

    def rebuild(self):
        self.image.fill(BUTTON_BACKGROUND_COLORS[self.state])
        pygame.draw.rect(self.image, BORDER_COLOR, ((0, 0), self.rect.size), 1)
        self.image.blit(self.text_surf, self.text_rect.topleft)

    def pass_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                if self.state == STATE_NORMAL:
                    self.state = STATE_HOVERED
                    self.rebuild()
            elif self.state == STATE_HOVERED:
                self.state = STATE_NORMAL
                self.rebuild()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                self.state = STATE_CLICKED
                self.on_click()
                self.rebuild()

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.state = STATE_HOVERED
                    self.rebuild()
                else:
                    self.state = STATE_NORMAL
                    self.rebuild()


class TextInput(UIElement):
    def __init__(self, initial_text, allowed_characters, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = initial_text
        self.allowed_characters = allowed_characters
        self.cursor_on = True
        self.cursor_timer = timer.Timer(500, self.toggle_cursor, True)
        self.rebuild()

    def toggle_cursor(self):
        self.cursor_on = not self.cursor_on
        self.rebuild()

    def rebuild(self):
        self.image.fill(BLACK)
        text_surf = UI_FONT.render(
            self.text + ("|" * self.cursor_on), False, TEXT_COLOR
        )
        text_rect = text_surf.get_rect(left=1, centery=self.rect.height / 2)
        self.image.blit(text_surf, text_rect.topleft)

    def update(self, dt):
        self.cursor_timer.update()

    def pass_event(self, event):
        if event.type == pygame.TEXTINPUT:
            for char in event.text:
                if char in self.allowed_characters:
                    self.text += char
            self.rebuild()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.rebuild()


class HeartMeter(UIElement):
    def __init__(self, sprite, rect, layer, group):
        super().__init__(rect, layer, group)
        self.sprite_to_monitor = sprite
        self.current_data = None
        self.last_data = None
        self.heart_size = pygame.Vector2(HEART_IMAGES[0].get_size())
        self.rebuild()

    def rebuild(self):
        heart_count = math.ceil(
            self.sprite_to_monitor.health_capacity / len(HEART_IMAGES)
        )
        columns = self.rect.width // self.heart_size.x
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        health_left = self.sprite_to_monitor.current_health
        health_per_heart = len(HEART_IMAGES) - 1
        pos = pygame.Vector2()
        for i in range(heart_count):
            if health_left > health_per_heart:
                heart_index = health_per_heart
            else:
                heart_index = health_left
            health_left -= heart_index
            self.image.blit(HEART_IMAGES[heart_index], pos)
            pos.x += self.heart_size.x
            if pos.x + self.heart_size.x >= self.rect.width:
                pos.x = 0
                pos.y += self.heart_size.y
        self.rect.size = self.image.get_size()
        self.last_data = (
            self.sprite_to_monitor.current_health,
            self.sprite_to_monitor.health_capacity,
        )

    def update(self, dt):
        super().update(dt)
        self.current_data = (
            self.sprite_to_monitor.current_health,
            self.sprite_to_monitor.health_capacity,
        )
        if self.current_data != self.last_data:
            self.rebuild()


class MagicMeter(UIElement):
    def __init__(self, sprite, rect, layer, group):
        super().__init__(rect, layer, group)
        self.sprite_to_monitor = sprite
        self.current_data = None
        self.last_data = None
        self.rebuild()

    def rebuild(self):
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, (156, 101, 70), ((0, 0), self.rect.size), 1)
        percent_full = (
            self.sprite_to_monitor.current_mana / self.sprite_to_monitor.mana_capacity
        )
        fill_rect = pygame.Rect(
            1, 1, percent_full * (self.rect.width - 2), self.rect.height - 2
        )
        pygame.draw.rect(self.image, (116, 163, 52), fill_rect)
        self.last_data = (
            self.sprite_to_monitor.current_mana,
            self.sprite_to_monitor.mana_capacity,
        )

    def update(self, dt):
        super().update(dt)
        self.current_data = (
            self.sprite_to_monitor.current_mana,
            self.sprite_to_monitor.mana_capacity,
        )
        if self.current_data != self.last_data:
            self.rebuild()


class Dialog(UIElement):
    def __init__(self, text, answers, on_kill, rect, layer, group):
        super().__init__(rect, layer, group)
        self.text = text
        self.displayed_text = ""
        self.answers = answers
        self.answer_index = 0
        self.chosen_index = None
        self.on_kill = on_kill
        self.add_letter_timer = timer.DTimer(20, self.add_text, True)
        self.kill_timer = timer.DTimer()
        self.image.set_colorkey(COLORKEY)
        self.state = STATE_WRITING_PROMPT
        self.pad = 3
        self.rebuild()

    def update_text(self):
        self.rebuild()

    def add_text(self):
        if not self.text:
            self.state = STATE_GETTING_ANSWER
            self.update_text()
            if not self.answers:
                self.kill_timer = timer.DTimer(1500, self.choose)
                self.state = STATE_COMPLETE
            self.add_letter_timer = timer.DTimer()
        else:
            self.displayed_text += self.text[0]
            self.text = self.text[1:]
            self.update_text()

    def get_full_text(self):
        # beginning prompt
        text = self.displayed_text
        # add all of the choices
        if self.state == STATE_GETTING_ANSWER:
            for i, choice in enumerate(self.answers):
                text += "\n"
                if i == self.answer_index:
                    # put a dash before selected answer
                    text += f"-{choice}"
                else:
                    text += f" {choice}"
        return text

    def rebuild(self):
        self.image.fill(COLORKEY)
        text = self.get_full_text()
        text_surface = UI_FONT.render(
            text, False, TEXT_COLOR, None, self.rect.width - (self.pad * 2)
        )
        text_rect = text_surface.get_rect(
            bottomleft=pygame.Vector2(self.rect.bottomleft)
            + (self.pad, -self.pad)
            - self.rect.topleft
        )
        self.image.blit(text_surface, text_rect.topleft)
        pygame.draw.rect(self.image, BORDER_COLOR, ((0, 0), self.rect.size), 1)

    def choose(self):
        print("chosen")
        self.chosen_index = self.answer_index
        self.state = STATE_COMPLETE
        self.kill()
        self.on_kill(self.get_answer())

    def get_answer(self):
        if not self.answers or self.chosen_index is None:
            return None
        return self.answers[self.chosen_index]

    def update(self, time_delta: float):
        super().update(time_delta)
        self.kill_timer.update(time_delta)
        self.add_letter_timer.update(time_delta)

    def pass_event(self, event):
        if self.state == STATE_GETTING_ANSWER:
            if event.type == event_binding.BOUND_EVENT:
                if event.name == "dialog pointer up":
                    self.answer_index = max(self.answer_index - 1, 0)
                    self.update_text()
                if event.name == "dialog pointer down":
                    self.answer_index = min(
                        self.answer_index + 1, len(self.answers) - 1
                    )
                    self.update_text()
                if event.name == "dialog select":
                    self.choose()
        if self.state == STATE_COMPLETE and not self.answers:
            if event.type == event_binding.BOUND_EVENT:
                if event.name == "dialog select":
                    self.choose()
