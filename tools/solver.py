"""Finds a path through a level with the same movement rules as the player.

Used by the tests to prove every level can be finished, and by
capture_screenshots.py to play the game.
"""
from collections import deque
from typing import Dict, List, Optional, Tuple

import pygame

from escape_game import settings as s
from escape_game.level import Level

Step = Tuple[int, int]
STEPS: Tuple[Step, ...] = (
    (s.PLAYER_SPEED, 0),
    (0, -s.PLAYER_SPEED),
    (0, s.PLAYER_SPEED),
    (-s.PLAYER_SPEED, 0),
)


def find_path(level: Level) -> Optional[List[Step]]:
    """Shortest list of per-frame moves from the spawn to the right edge."""
    blocked = level.walls + level.traps
    start = s.PLAYER_SPAWN
    came_from: Dict[Tuple[int, int], Tuple[Tuple[int, int], Step]] = {}
    queue = deque([start])
    seen = {start}
    rect = pygame.Rect(0, 0, s.PLAYER_SIZE, s.PLAYER_SIZE)

    while queue:
        pos = queue.popleft()
        if pos[0] >= s.SCREEN_WIDTH:
            path: List[Step] = []
            while pos != start:
                pos, step = came_from[pos]
                path.append(step)
            return path[::-1]
        for step in STEPS:
            x, y = pos[0] + step[0], pos[1] + step[1]
            rect.topleft = (x, y)
            if (x, y) in seen or x < 0 or rect.top < s.HUD_HEIGHT or rect.bottom > s.SCREEN_HEIGHT:
                continue
            seen.add((x, y))
            if rect.collidelist(blocked) == -1:
                came_from[(x, y)] = (pos, step)
                queue.append((x, y))
    return None
