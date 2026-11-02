"""Small UI helpers shared by the scenes."""
import math
from typing import Optional, Tuple

import pygame

from . import settings as s
from .assets import load_font


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    color: Tuple[int, int, int],
    anchor: str,
    pos: Tuple[int, int],
) -> pygame.Rect:
    """Draw text with `pos` applied to the named rect anchor, e.g. "center"."""
    # The font's slashed zero reads as an 8; its letter O reads as a zero.
    image = load_font(size).render(text.replace("0", "O"), True, color)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def format_time(seconds: float) -> str:
    # The pixel font has no colon, so times are shown in whole seconds.
    return f"{max(0, math.ceil(seconds))} SEC"


def brighten(image: pygame.Surface) -> pygame.Surface:
    bright = image.copy()
    bright.fill((45, 45, 45, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return bright


class Button:
    def __init__(
        self,
        image: pygame.Surface,
        hover: Optional[pygame.Surface] = None,
        **anchor: Tuple[int, int],
    ) -> None:
        self.image = image
        self.hover = hover or brighten(image)
        self.rect = image.get_rect(**anchor)

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface: pygame.Surface) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        surface.blit(self.hover if hovered else self.image, self.rect)
