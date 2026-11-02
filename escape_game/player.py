"""The player character."""
from typing import List, Sequence

import pygame

from . import settings as s
from .assets import load_image

STAND, WALK = 0, 1
SPRITE_SIZE = (17, 28)  # taller than the hitbox so the character is not squashed


class Player:
    def __init__(self) -> None:
        self.rect = pygame.Rect(*s.PLAYER_SPAWN, s.PLAYER_SIZE, s.PLAYER_SIZE)
        self.flip = False
        self.action = STAND
        self.frame_index = 0
        self.update_time = 0
        self.animations: List[List[pygame.Surface]] = [
            [load_image(f"animation/stand/{i}.png", SPRITE_SIZE) for i in range(5)],
            [load_image(f"animation/walk/{i}.png", SPRITE_SIZE) for i in range(25)],
        ]

    def respawn(self) -> None:
        self.rect.topleft = s.PLAYER_SPAWN

    def move(self, dx: int, dy: int, walls: Sequence[pygame.Rect]) -> None:
        """Move one axis at a time so the player slides along walls."""
        if dx:
            self.flip = dx < 0
        self.rect.x += dx
        if self.rect.left < 0 or self.rect.collidelist(walls) != -1:
            self.rect.x -= dx
        self.rect.y += dy
        out_of_bounds = self.rect.top < s.HUD_HEIGHT or self.rect.bottom > s.SCREEN_HEIGHT
        if out_of_bounds or self.rect.collidelist(walls) != -1:
            self.rect.y -= dy
        self.set_action(WALK if dx or dy else STAND)

    def set_action(self, action: int) -> None:
        if action != self.action:
            self.action = action
            self.frame_index = 0

    def update_animation(self, now: int) -> None:
        if now - self.update_time > s.ANIMATION_COOLDOWN:
            self.update_time = now
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.action])

    def draw(self, surface: pygame.Surface) -> None:
        image = self.animations[self.action][self.frame_index]
        image = pygame.transform.flip(image, self.flip, False)
        surface.blit(image, image.get_rect(midbottom=self.rect.midbottom))
