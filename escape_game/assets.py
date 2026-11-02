"""Image, font and audio loading."""
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import pygame

from . import settings as s


@lru_cache(maxsize=None)
def load_image(name: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """Load an image relative to picture/. Call after the display is created."""
    image = pygame.image.load(str(s.PICTURE_DIR / name)).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image


@lru_cache(maxsize=None)
def load_font(size: int) -> pygame.font.Font:
    return pygame.font.Font(str(s.FONT_FILE), size)


def load_tiles() -> List[pygame.Surface]:
    tile = (s.TILE_SIZE, s.TILE_SIZE)
    return [load_image(f"map/{i}.png", tile) for i in range(s.TILE_TYPES)]


def load_trap_frames(count: int = 8) -> List[pygame.Surface]:
    """Rotated copies of the portal tile, used to make it spin."""
    tile = load_image(f"map/{s.TRAP_TILE}.png", (s.TILE_SIZE, s.TILE_SIZE))
    return [pygame.transform.rotate(tile, i * 360 / count) for i in range(count)]


class Audio:
    """Music and sound effects. Every call is a no-op without an audio device."""

    def __init__(self) -> None:
        self.enabled = pygame.mixer.get_init() is not None
        self.muted = False
        self._sounds: Dict[str, pygame.mixer.Sound] = {}

    def play_music(self, name: str) -> None:
        if not self.enabled:
            return
        pygame.mixer.music.load(str(s.SOUND_DIR / name))
        pygame.mixer.music.set_volume(0 if self.muted else s.MUSIC_VOLUME)
        pygame.mixer.music.play(-1)

    def pause_music(self) -> None:
        if self.enabled:
            pygame.mixer.music.pause()

    def resume_music(self) -> None:
        if self.enabled:
            pygame.mixer.music.unpause()

    def stop_music(self) -> None:
        if self.enabled:
            pygame.mixer.music.stop()

    def play_sound(self, name: str) -> None:
        if not self.enabled or self.muted:
            return
        if name not in self._sounds:
            self._sounds[name] = pygame.mixer.Sound(str(s.SOUND_DIR / name))
            self._sounds[name].set_volume(s.SFX_VOLUME)
        self._sounds[name].play()

    def toggle_mute(self) -> None:
        self.muted = not self.muted
        if self.enabled:
            pygame.mixer.music.set_volume(0 if self.muted else s.MUSIC_VOLUME)
            if self.muted:
                pygame.mixer.stop()
