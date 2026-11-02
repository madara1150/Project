import pytest

from escape_game import settings as s
from escape_game.level import Level, load_grid
from tools.solver import find_path


@pytest.mark.parametrize("number", range(s.LEVEL_COUNT))
def test_grid_shape_and_tiles(number):
    grid = load_grid(number)
    assert len(grid) == s.ROWS
    assert all(len(row) == s.COLS for row in grid)
    assert all(-1 <= tile <= s.TRAP_TILE for row in grid for tile in row)


@pytest.mark.parametrize("number", range(s.LEVEL_COUNT))
def test_level_can_be_finished(number):
    assert find_path(Level(number)) is not None


def test_ten_levels_fit_in_the_time_limit():
    """A perfect run of the longest ten levels must leave room for mistakes."""
    seconds = [len(find_path(Level(n))) / s.FPS for n in range(s.LEVEL_COUNT)]
    longest_run = max(
        sum(seconds[(start + i) % s.LEVEL_COUNT] for i in range(s.LEVELS_TO_WIN))
        for start in range(s.LEVEL_COUNT)
    )
    assert longest_run < s.TIME_LIMIT * 2 / 3
