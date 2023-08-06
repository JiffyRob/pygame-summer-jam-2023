import pygame

import gui


def create_menu(
    menu_name,
    button_names,
    button_functions,
    screen_size,
    return_container=False,
    return_skipped=False,
):
    menu = gui.UIGroup()
    container_rect = pygame.Rect(
        (0, 0),
        (screen_size.x * 0.8, screen_size.y * 0.8),
    )
    container_rect.center = screen_size / 2
    container = gui.BGRect(container_rect, 1, menu)
    height = 30
    rect = pygame.Rect(0, 10, container_rect.width * 0.8, height)
    rect.centerx = container_rect.width / 2
    rect.topleft += pygame.Vector2(container_rect.topleft)
    gui.Text(menu_name, gui.ANCHOR_MIDTOP, rect, 2, menu)
    skipped = []
    for i, button_name, on_click in zip(
        range(len(button_names)), button_names, button_functions
    ):
        rect = pygame.Rect(
            (0, (i + 1) * (height + 2) + 10, container_rect.width - 16, 30)
        )
        rect.centerx = container_rect.width / 2
        rect.topleft += pygame.Vector2(container_rect.topleft)
        if button_name == ":SKIP":
            skipped.append(rect)
            continue
        gui.Button(button_name, on_click, rect, 2, menu)
    return_values = [menu]
    if return_container:
        return_values.append(container)
    if return_skipped:
        return_values.append(skipped)
    if len(return_values) == 1:
        return return_values[0]
    return return_values


def get_dialog_rect(screen_size):
    rect = pygame.Rect(0, 0, screen_size.x * 0.75, screen_size.y * 0.3)
    rect.bottom = screen_size.y - 4
    rect.centerx = screen_size.x // 2
    return rect
