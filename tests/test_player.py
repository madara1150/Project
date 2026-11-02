import pygame

from escape_game import settings as s
from escape_game.player import STAND, WALK, Player


def test_slides_along_a_wall_when_moving_diagonally(app):
    player = Player()
    wall = pygame.Rect(player.rect.right, 0, 30, s.SCREEN_HEIGHT)
    start_x, start_y = player.rect.topleft

    player.move(2, 2, [wall])

    assert player.rect.topleft == (start_x, start_y + 2)


def test_cannot_walk_through_walls(app):
    player = Player()
    wall = pygame.Rect(player.rect.right + 1, 0, 30, s.SCREEN_HEIGHT)

    for _ in range(10):
        player.move(2, 0, [wall])

    assert not player.rect.colliderect(wall)


def test_stays_inside_the_play_area(app):
    player = Player()
    for _ in range(500):
        player.move(-2, -2, [])
    assert player.rect.topleft == (0, s.HUD_HEIGHT)

    for _ in range(500):
        player.move(0, 2, [])
    assert s.SCREEN_HEIGHT - s.PLAYER_SPEED < player.rect.bottom <= s.SCREEN_HEIGHT


def test_action_follows_movement(app):
    player = Player()
    player.move(2, 0, [])
    assert player.action == WALK
    player.move(0, 0, [])
    assert player.action == STAND
