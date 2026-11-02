import json

import pygame
import pytest

from conftest import FRAME, click, play_level, press, release
from escape_game import settings as s
from escape_game import storage
from escape_game.scenes import (
    CreditScene,
    GameClearScene,
    GameOverScene,
    GameScene,
    LevelSelectScene,
    MenuScene,
    PauseScene,
)


def test_menu_buttons_open_their_scenes(app):
    click(app.scene.map.rect.center)
    app.tick(FRAME)
    assert isinstance(app.scene, LevelSelectScene)

    click(app.scene.buttons[7].rect.center)
    app.tick(FRAME)
    assert isinstance(app.scene, GameScene)
    assert app.scene.level.number == 7


def test_credit_returns_to_the_menu_by_itself(app):
    click(app.scene.credit.rect.center)
    app.tick(FRAME)
    assert isinstance(app.scene, CreditScene)

    for _ in range(60 * 30):
        app.tick(FRAME)
    assert isinstance(app.scene, MenuScene)


def test_menu_exit_stops_the_app(app):
    click(app.scene.exit.rect.center)
    app.tick(FRAME)
    assert not app.running


def test_player_moves_once_per_frame(app, game):
    press(pygame.K_d)
    start = game.player.rect.x
    app.tick(FRAME)
    app.tick(FRAME)
    assert game.player.rect.x == start + 2 * s.PLAYER_SPEED


def test_arrow_keys_also_move_the_player(app, game):
    press(pygame.K_RIGHT)
    start = game.player.rect.x
    app.tick(FRAME)
    assert game.player.rect.x == start + s.PLAYER_SPEED


def test_timer_counts_real_time_not_frames(app, game):
    start = game.time_left
    app.tick(0.5)
    assert game.time_left == pytest.approx(start - 0.5)


def test_reaching_the_right_edge_loads_the_next_level(app, game):
    play_level(app, game)
    assert app.scene is game
    assert game.level.number == 1
    assert game.cleared == 1
    assert game.player.rect.topleft == s.PLAYER_SPAWN


def test_level_numbers_wrap_around(app):
    game = GameScene(app, s.LEVEL_COUNT - 1)
    app.change(game)
    play_level(app, game)
    assert game.level.number == 0


def test_portal_ends_the_run(app, game):
    game.player.rect.center = game.level.traps[0].center
    app.tick(FRAME)
    assert isinstance(app.scene, GameOverScene)


def test_time_out_ends_the_run(app, game):
    game.time_left = FRAME / 2
    app.tick(FRAME)
    assert isinstance(app.scene, GameOverScene)


def test_game_over_restart_begins_a_fresh_run(app, game):
    game.cleared = 4
    game.time_left = 1
    game.load_level(5)
    game.player.rect.center = game.level.traps[0].center
    app.tick(FRAME)

    click(app.scene.restart.rect.center)
    app.tick(FRAME)

    restarted = app.scene
    assert isinstance(restarted, GameScene) and restarted is not game
    assert restarted.level.number == 0
    assert restarted.cleared == 0
    assert restarted.time_left > s.TIME_LIMIT - 1


def test_pause_freezes_the_timer_and_resume_keeps_the_run(app, game):
    press(pygame.K_ESCAPE)
    app.tick(FRAME)
    assert isinstance(app.scene, PauseScene)

    time_left = game.time_left
    for _ in range(30):
        app.tick(FRAME)
    assert game.time_left == time_left

    click(app.scene.resume.rect.center)
    app.tick(FRAME)
    assert app.scene is game


def test_key_released_during_pause_does_not_stick(app, game):
    press(pygame.K_d)
    app.tick(FRAME)
    press(pygame.K_ESCAPE)
    app.tick(FRAME)
    release(pygame.K_d)
    app.tick(FRAME)
    press(pygame.K_ESCAPE)
    app.tick(FRAME)

    x = game.player.rect.x
    app.tick(FRAME)
    assert game.player.rect.x == x


def test_pause_exit_returns_to_the_menu(app, game):
    click(game.menu.rect.center)
    app.tick(FRAME)
    click(app.scene.exit.rect.center)
    app.tick(FRAME)
    assert isinstance(app.scene, MenuScene)


def test_clearing_ten_levels_wins_and_saves_the_best_time(app, game):
    for _ in range(s.LEVELS_TO_WIN):
        play_level(app, game)

    assert isinstance(app.scene, GameClearScene)
    assert app.scene.new_record
    saved = json.loads(app.save_file.read_text())["best_time"]
    assert saved == pytest.approx(s.TIME_LIMIT - game.time_left)


def test_slower_run_keeps_the_old_record(app):
    assert app.record_time(100)
    assert not app.record_time(120)
    assert app.best_time == 100
    assert app.record_time(90)


def test_every_scene_draws(app, game):
    for scene in (
        game,
        PauseScene(app, game),
        GameOverScene(app, game, "TIME IS UP"),
        LevelSelectScene(app),
        CreditScene(app),
        MenuScene(app),
    ):
        scene.draw(app.screen)
    clear = GameClearScene(app, game, 123)
    clear.enter()
    clear.draw(app.screen)


@pytest.mark.parametrize("content", ["", "not json", "[]", '{"best_time": "x"}', '{"best_time": -1}'])
def test_broken_save_file_is_ignored(tmp_path, content):
    path = tmp_path / "save.json"
    path.write_text(content)
    assert storage.load_best_time(path) is None


def test_missing_save_file_is_ignored(tmp_path):
    assert storage.load_best_time(tmp_path / "nope.json") is None


def test_game_runs_without_an_audio_device(app, game):
    pygame.mixer.quit()
    app.audio.enabled = False
    game.time_left = FRAME / 2
    app.tick(FRAME)
    assert isinstance(app.scene, GameOverScene)
