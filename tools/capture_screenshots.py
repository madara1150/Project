"""Regenerates the README images by playing the real game without a window.

Usage: python -m tools.capture_screenshots   (needs Pillow, see requirements-dev.txt)
"""
import os
import tempfile
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from PIL import Image

from escape_game import settings as s
from escape_game.app import App
from escape_game.scenes import (
    CreditScene,
    GameClearScene,
    GameOverScene,
    GameScene,
    LevelSelectScene,
    MenuScene,
    PauseScene,
)
from tools.solver import find_path

OUTPUT = s.ROOT / "docs" / "screenshots"
FRAME = 1 / s.FPS
GIF_LEVEL = 0
GIF_EVERY = 5  # keep one frame in five
GIF_SIZE = (500, 375)
KEYS = {
    (s.PLAYER_SPEED, 0): pygame.K_d,
    (-s.PLAYER_SPEED, 0): pygame.K_a,
    (0, -s.PLAYER_SPEED): pygame.K_w,
    (0, s.PLAYER_SPEED): pygame.K_s,
}


def save(app, name):
    app.scene.draw(app.screen)
    pygame.image.save(app.screen, str(OUTPUT / name))


def to_gif_frame(surface):
    small = pygame.transform.smoothscale(surface, GIF_SIZE)
    raw = pygame.image.tostring(small, "RGB")
    return Image.frombytes("RGB", GIF_SIZE, raw).quantize(64)


def play(app, game, steps, frames=None):
    """Follow solver steps through the event queue, like a person would."""
    held = None
    for index, step in enumerate(steps):
        key = KEYS[step]
        if key != held:
            if held is not None:
                pygame.event.post(pygame.event.Event(pygame.KEYUP, key=held))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
            held = key
        app.tick(FRAME)
        if frames is not None and index % GIF_EVERY == 0:
            frames.append(to_gif_frame(app.screen))
    if held is not None:
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=held))
    app.tick(FRAME)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    save_file = Path(tempfile.mkdtemp()) / "save.json"
    app = App(save_file=save_file)
    app.record_time(214)  # so the menu shows the best-time line

    app.change(MenuScene(app))
    save(app, "menu.png")

    app.change(LevelSelectScene(app))
    save(app, "level-select.png")

    credit = CreditScene(app)
    credit.y = 180
    app.change(credit)
    save(app, "credit.png")

    # Gameplay: walk level 0 for the GIF, then stop partway through level 5.
    game = GameScene(app, GIF_LEVEL)
    app.change(game)
    frames = []
    play(app, game, find_path(game.level), frames)
    frames[0].save(
        OUTPUT / "gameplay.gif",
        save_all=True,
        append_images=frames[1:],
        duration=int(GIF_EVERY * FRAME * 1000),
        loop=0,
        optimize=True,
    )

    game = GameScene(app, 5)
    app.change(game)
    steps = find_path(game.level)
    play(app, game, steps[: len(steps) * 2 // 3])
    save(app, "gameplay.png")

    app.change(PauseScene(app, game))
    save(app, "pause.png")

    app.change(GameOverScene(app, game, "THE PORTAL GOT YOU"))
    save(app, "game-over.png")

    app.change(GameClearScene(app, game, 198))
    save(app, "game-clear.png")


if __name__ == "__main__":
    main()
