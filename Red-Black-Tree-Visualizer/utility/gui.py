import pygame
from pygame import Vector2

from utility.enums import Color


def drawTextWithOutline(visualizer, text, font_type, font_size, color, center_x, center_y, fitted_width=None):
    for _ in range(3):
        font = pygame.font.SysFont(font_type, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        if fitted_width is not None and text_rect.width > fitted_width:
            font_size = int(font_size * fitted_width / text_rect.width)
        else:
            break

    text_surface_outline = font.render(text, True, Color.OUTLINE_BLACK.value)
    text_rect_outline = text_surface_outline.get_rect(center=(center_x, center_y))

    outline_thickness = 1
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            visualizer.screen.blit(text_surface_outline, text_rect_outline.move(dx, dy))

    visualizer.screen.blit(text_surface, text_rect)


def drawAALine(visualizer, start_pos, end_pos, thickness=1.0):
    if start_pos == end_pos:
        return

    if start_pos[1] > end_pos[1]:
        start_pos, end_pos = end_pos, start_pos

    thickness = max(1, int(thickness * visualizer.zoom))
    start_pos = Vector2((start_pos[0] + visualizer.x_offset) * visualizer.zoom,
                        (start_pos[1] + visualizer.y_offset) * visualizer.zoom)
    end_pos = Vector2((end_pos[0] + visualizer.x_offset) * visualizer.zoom,
                      (end_pos[1] + visualizer.y_offset) * visualizer.zoom)

    if thickness == 1:
        pygame.draw.aaline(visualizer.screen, Color.OUTLINE_BLACK.value, start_pos, end_pos)
    elif thickness > 1:
        direction = (end_pos - start_pos).normalize()
        perp = Vector2(-direction.y, direction.x) * (thickness / 2.0)

        points = [
            start_pos + perp,
            start_pos - perp,
            end_pos - perp,
            end_pos + perp
        ]

        pygame.draw.polygon(visualizer.screen, Color.OUTLINE_BLACK.value, points)


class Button:
    def __init__(self, visualizer, x, y, w, h, text, font, font_size, color, font_color):
        self.visualizer = visualizer
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.font_size = font_size
        self.color = color
        self.font_color = font_color
        self.active = False

    def draw(self):
        pygame.draw.rect(self.visualizer.screen, self.color, self.rect)

        drawTextWithOutline(self.visualizer, self.text, self.font, self.font_size,
                            self.font_color, self.rect.centerx, self.rect.centery, self.rect.width)
