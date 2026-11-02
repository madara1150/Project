"""Level data: reading the CSV grids and turning them into collision rects."""
import csv
from typing import List, Sequence

import pygame

from . import settings as s

Grid = List[List[int]]


def load_grid(number: int) -> Grid:
    with open(s.LEVEL_DIR / f"level{number}_data.csv", newline="") as csvfile:
        return [[int(tile) for tile in row] for row in csv.reader(csvfile)]


class Level:
    def __init__(self, number: int) -> None:
        self.number = number
        self.grid = load_grid(number)
        self.walls: List[pygame.Rect] = []
        self.traps: List[pygame.Rect] = []  # hitboxes
        self.trap_tiles: List[pygame.Rect] = []  # where the art is drawn

        for y, row in enumerate(self.grid):
            if y < s.HUD_ROWS:
                continue
            for x, tile in enumerate(row):
                rect = pygame.Rect(x * s.TILE_SIZE, y * s.TILE_SIZE, s.TILE_SIZE, s.TILE_SIZE)
                if tile == s.TRAP_TILE:
                    self.trap_tiles.append(rect)
                    self.traps.append(rect.inflate(-2 * s.TRAP_MARGIN, -2 * s.TRAP_MARGIN))
                elif tile >= 0:
                    self.walls.append(rect)

    def render(self, tiles: Sequence[pygame.Surface]) -> pygame.Surface:
        """Bake the walls into one surface so a frame only needs a single blit."""
        surface = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        surface.fill(s.FLOOR)
        for rect in self.walls:
            x, y = rect.x // s.TILE_SIZE, rect.y // s.TILE_SIZE
            surface.blit(tiles[self.grid[y][x]], rect)
        return surface
