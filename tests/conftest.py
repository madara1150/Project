import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from escape_game import settings as s
from escape_game.app import App
from escape_game.scenes import GameScene
from tools.solver import find_path

FRAME = 1 / s.FPS
KEY_FOR_STEP = {
    (s.PLAYER_SPEED, 0): pygame.K_d,
    (-s.PLAYER_SPEED, 0): pygame.K_a,
    (0, -s.PLAYER_SPEED): pygame.K_w,
    (0, s.PLAYER_SPEED): pygame.K_s,
}


@pytest.fixture
def app(tmp_path):
    return App(save_file=tmp_path / "save.json")


@pytest.fixture
def game(app):
    scene = GameScene(app, 0)
    app.change(scene)
    return scene


def press(key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))


def release(key):
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=key))


def click(pos):
    pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))


def play_level(app, game):
    """Walk the solver's route through the current level with key events."""
    held = None
    for step in find_path(game.level):
        key = KEY_FOR_STEP[step]
        if key != held:
            if held is not None:
                release(held)
            press(key)
            held = key
        app.tick(FRAME)
    release(held)
    app.tick(FRAME)
