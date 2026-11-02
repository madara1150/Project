"""Every screen of the game. The App runs exactly one scene at a time."""
import random
from typing import List, Optional, Set, Tuple

import pygame

from . import settings as s
from .assets import load_image, load_tiles, load_trap_frames
from .level import Level
from .player import Player
from .ui import Button, draw_text, format_time

LEFT_KEYS = (pygame.K_a, pygame.K_LEFT)
RIGHT_KEYS = (pygame.K_d, pygame.K_RIGHT)
UP_KEYS = (pygame.K_w, pygame.K_UP)
DOWN_KEYS = (pygame.K_s, pygame.K_DOWN)
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

CENTER_X = s.SCREEN_WIDTH // 2


def restart_button(**anchor: Tuple[int, int]) -> Button:
    size = (270, 72)
    return Button(
        load_image("Button/restart/restart1.png", size),
        load_image("Button/restart/restart2.png", size),
        **anchor,
    )


def exit_button(size: Tuple[int, int] = (204, 72), **anchor: Tuple[int, int]) -> Button:
    return Button(
        load_image("Button/Exit/ExitN.png", size),
        load_image("Button/Exit/ExitP.png", size),
        **anchor,
    )


class Scene:
    def __init__(self, app) -> None:
        self.app = app

    def enter(self) -> None:
        """Called every time the scene becomes the active one."""

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def click(self) -> None:
        self.app.audio.play_sound(s.CLICK_SOUND)


class MenuScene(Scene):
    CHARACTER = pygame.Rect(398, 142, 223, 400)
    ZOOM_TIME = 0.8

    def __init__(self, app) -> None:
        super().__init__(app)
        self.background = load_image("Button/BG/intro2.png", (s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        self.start = Button(
            load_image("Button/Start/StartN.png", (210, 70)),
            load_image("Button/Start/StartP.png", (210, 70)),
            midright=(CENTER_X + 75, 640),
        )
        self.map = Button(
            load_image("Button/Map/MapN.png", (147, 70)),
            load_image("Button/Map/MapP.png", (147, 70)),
            midleft=(CENTER_X + 95, 640),
        )
        self.exit = exit_button((130, 46), topright=(s.SCREEN_WIDTH - 16, 16))
        self.credit = Button(
            load_image("Button/TJAK (Credit)/TJAK.png", (200, 47)),
            load_image("Button/TJAK (Credit)/TJAKmap.png", (200, 47)),
            topleft=(16, 16),
        )
        self.zoom = load_image("Player/player_flip.png", (900, 800))
        self.zoom_left = 0.0

    def enter(self) -> None:
        self.app.audio.play_music(s.MENU_MUSIC)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.start.clicked(event) or (event.type == pygame.KEYDOWN and event.key in CONFIRM_KEYS):
            self.click()
            self.app.change(GameScene(self.app))
        elif self.map.clicked(event):
            self.click()
            self.app.change(LevelSelectScene(self.app))
        elif self.credit.clicked(event):
            self.click()
            self.app.change(CreditScene(self.app))
        elif self.exit.clicked(event):
            self.click()
            self.app.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.CHARACTER.collidepoint(event.pos):
            self.zoom_left = self.ZOOM_TIME

    def update(self, dt: float) -> None:
        self.zoom_left = max(0.0, self.zoom_left - dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        if self.zoom_left:
            surface.fill(s.ORANGE, self.CHARACTER)
            surface.blit(self.zoom, (60, -45))
        for button in (self.start, self.map, self.exit, self.credit):
            button.draw(surface)
        if self.app.best_time is not None:
            best = format_time(self.app.best_time)
            draw_text(surface, f"BEST {best}", 22, s.DARK_RED, "center", (CENTER_X, 712))


class CreditScene(Scene):
    NAMES = (
        "CREDIT BY",
        "",
        "Tanatip Singhanon",
        "Akhabhop Khunkitti",
        "Ken Muraki",
        "Jeerachaya Chareonphol",
    )
    SCROLL_SPEED = 75  # pixels per second
    LINE_HEIGHT = 70

    def __init__(self, app) -> None:
        super().__init__(app)
        self.y = float(s.SCREEN_HEIGHT)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.app.change(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.y -= self.SCROLL_SPEED * dt
        if self.y < -self.LINE_HEIGHT * len(self.NAMES):
            self.app.change(MenuScene(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(s.ORANGE)
        for i, name in enumerate(self.NAMES):
            y = int(self.y) + i * self.LINE_HEIGHT
            draw_text(surface, name, 30, s.DARK_RED, "center", (CENTER_X, y))


class LevelSelectScene(Scene):
    COLUMNS = 5
    THUMB = (170, 117)
    GAP = 20
    TOP = 130

    def __init__(self, app) -> None:
        super().__init__(app)
        self.back = Button(
            load_image("Button/Back/back1.png", (54, 54)),
            load_image("Button/Back/back2.png", (54, 54)),
            topleft=(20, 20),
        )
        self.buttons: List[Button] = []
        tiles = load_tiles()
        width = self.COLUMNS * self.THUMB[0] + (self.COLUMNS - 1) * self.GAP
        left = (s.SCREEN_WIDTH - width) // 2
        for number in range(s.LEVEL_COUNT):
            maze = Level(number).render(tiles).subsurface(
                (0, s.HUD_ROWS * s.TILE_SIZE, s.SCREEN_WIDTH, s.SCREEN_HEIGHT - s.HUD_ROWS * s.TILE_SIZE)
            )
            thumb = pygame.transform.smoothscale(maze, self.THUMB)
            hover = thumb.copy()
            pygame.draw.rect(hover, s.YELLOW, hover.get_rect(), 4)
            row, col = divmod(number, self.COLUMNS)
            x = left + col * (self.THUMB[0] + self.GAP)
            y = self.TOP + row * (self.THUMB[1] + self.GAP + 34)
            self.buttons.append(Button(thumb, hover, topleft=(x, y)))

    def handle_event(self, event: pygame.event.Event) -> None:
        escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        if self.back.clicked(event) or escape:
            self.click()
            self.app.change(MenuScene(self.app))
            return
        for number, button in enumerate(self.buttons):
            if button.clicked(event):
                self.click()
                self.app.change(GameScene(self.app, number))
                return

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(s.ORANGE)
        draw_text(surface, "SELECT MAP", 40, s.DARK_RED, "center", (CENTER_X, 62))
        self.back.draw(surface)
        for number, button in enumerate(self.buttons):
            button.draw(surface)
            pos = (button.rect.centerx, button.rect.bottom + 16)
            draw_text(surface, f"LEVEL {number + 1}", 14, s.BLACK, "center", pos)


class GameScene(Scene):
    SPIN_SPEED = 12  # portal frames per second

    def __init__(self, app, start_level: Optional[int] = None) -> None:
        super().__init__(app)
        if start_level is None:
            start_level = random.randrange(s.LEVEL_COUNT)
        self.start_level = start_level
        self.time_left = float(s.TIME_LIMIT)
        self.cleared = 0
        self.player = Player()
        self.keys: Set[int] = set()
        self.started = False
        self.spin = 0.0
        self.tiles = load_tiles()
        self.trap_frames = load_trap_frames()
        self.hud = load_image("Button/menu/orange.jpg", (s.SCREEN_WIDTH, s.HUD_HEIGHT))
        self.menu = Button(load_image("Button/menu/menu1.png", (50, 50)), topright=(s.SCREEN_WIDTH - 20, 7))
        self.load_level(start_level)

    def load_level(self, number: int) -> None:
        self.level = Level(number)
        self.level_surface = self.level.render(self.tiles)
        self.player.respawn()

    def enter(self) -> None:
        self.keys.clear()  # keys released while paused never reach this scene
        if self.started:
            self.app.audio.resume_music()
        else:
            self.started = True
            self.app.audio.play_music(s.GAME_MUSIC)

    def pause(self) -> None:
        self.click()
        self.app.audio.pause_music()
        self.app.change(PauseScene(self.app, self))

    def restart(self) -> "GameScene":
        return GameScene(self.app, self.start_level)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause()
            else:
                self.keys.add(event.key)
        elif event.type == pygame.KEYUP:
            self.keys.discard(event.key)
        elif event.type == pygame.WINDOWFOCUSLOST or self.menu.clicked(event):
            self.pause()

    def held(self, keys: Tuple[int, int]) -> bool:
        return not self.keys.isdisjoint(keys)

    def update(self, dt: float) -> None:
        self.time_left -= dt
        self.spin += dt * self.SPIN_SPEED
        if self.time_left <= 0:
            self.finish(GameOverScene(self.app, self, "TIME IS UP"))
            return

        dx = (self.held(RIGHT_KEYS) - self.held(LEFT_KEYS)) * s.PLAYER_SPEED
        dy = (self.held(DOWN_KEYS) - self.held(UP_KEYS)) * s.PLAYER_SPEED
        self.player.move(dx, dy, self.level.walls)
        self.player.update_animation(pygame.time.get_ticks())

        if self.player.rect.collidelist(self.level.traps) != -1:
            self.finish(GameOverScene(self.app, self, "THE PORTAL GOT YOU"))
        elif self.player.rect.left >= s.SCREEN_WIDTH:
            self.next_level()

    def next_level(self) -> None:
        self.cleared += 1
        if self.cleared >= s.LEVELS_TO_WIN:
            self.finish(GameClearScene(self.app, self, s.TIME_LIMIT - self.time_left))
        else:
            self.load_level((self.level.number + 1) % s.LEVEL_COUNT)

    def finish(self, scene: Scene) -> None:
        self.app.audio.stop_music()
        self.app.change(scene)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.level_surface, (0, 0))
        frame = self.trap_frames[int(self.spin) % len(self.trap_frames)]
        for rect in self.level.trap_tiles:
            surface.blit(frame, frame.get_rect(center=rect.center))
        self.player.draw(surface)
        self.draw_hud(surface)

    def draw_hud(self, surface: pygame.Surface) -> None:
        surface.blit(self.hud, (0, 0))
        y = s.HUD_HEIGHT // 2
        low_time = self.time_left <= s.TIME_WARNING
        flash = low_time and int(self.time_left * 4) % 2 == 0
        time_color = s.WHITE if flash else s.RED if low_time else s.DARK_RED
        draw_text(surface, f"TIME {format_time(self.time_left)}", 20, time_color, "midleft", (20, y))
        draw_text(surface, f"LEVEL {self.level.number + 1}", 20, s.DARK_RED, "center", (CENTER_X - 40, y))
        stage = f"STAGE {self.cleared + 1} OF {s.LEVELS_TO_WIN}"
        draw_text(surface, stage, 20, s.DARK_RED, "midright", (s.SCREEN_WIDTH - 100, y))
        self.menu.draw(surface)


class PauseScene(Scene):
    def __init__(self, app, game: GameScene) -> None:
        super().__init__(app)
        self.game = game
        self.resume = Button(load_image("Button/menu/resume1.png", (232, 102)), center=(CENTER_X, 270))
        self.restart = restart_button(center=(CENTER_X, 400))
        self.exit = exit_button(center=(CENTER_X, 510))
        self.shade = pygame.Surface((s.SCREEN_WIDTH, s.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.shade.fill((0, 0, 0, 170))

    def handle_event(self, event: pygame.event.Event) -> None:
        escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        if self.resume.clicked(event) or escape:
            self.click()
            self.app.change(self.game)
        elif self.restart.clicked(event):
            self.click()
            self.app.change(self.game.restart())
        elif self.exit.clicked(event):
            self.click()
            self.app.change(MenuScene(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        self.game.draw(surface)
        surface.blit(self.shade, (0, 0))
        draw_text(surface, "PAUSED", 40, s.WHITE, "center", (CENTER_X, 150))
        for button in (self.resume, self.restart, self.exit):
            button.draw(surface)


class GameOverScene(Scene):
    def __init__(self, app, game: GameScene, reason: str) -> None:
        super().__init__(app)
        self.game = game
        self.reason = reason
        self.title = load_image("Button/over2.png", (368, 182))
        self.restart = restart_button(center=(CENTER_X, 520))
        self.exit = exit_button(center=(CENTER_X, 625))

    def enter(self) -> None:
        self.app.audio.play_sound(s.OVER_SOUND)

    def handle_event(self, event: pygame.event.Event) -> None:
        confirm = event.type == pygame.KEYDOWN and event.key in CONFIRM_KEYS
        if self.restart.clicked(event) or confirm:
            self.click()
            self.app.change(self.game.restart())
        elif self.exit.clicked(event):
            self.click()
            self.app.change(MenuScene(self.app))

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(s.BLACK)
        surface.blit(self.title, self.title.get_rect(center=(CENTER_X, 220)))
        draw_text(surface, self.reason, 22, s.WHITE, "center", (CENTER_X, 370))
        stage = f"STAGE {self.game.cleared + 1} OF {s.LEVELS_TO_WIN}"
        draw_text(surface, stage, 18, s.YELLOW, "center", (CENTER_X, 415))
        self.restart.draw(surface)
        self.exit.draw(surface)


class GameClearScene(Scene):
    FRAME_TIME = 0.042

    def __init__(self, app, game: GameScene, time_used: float) -> None:
        super().__init__(app)
        self.game = game
        self.time_used = time_used
        self.logo = load_image("Button/TJAK (Credit)/TJAK.png", (300, 70))
        self.frames = [load_image(f"animation/walk/{i}.png", (190, 305)) for i in range(25)]
        self.frame_clock = 0.0
        self.restart = restart_button(midleft=(420, 560))
        self.exit = exit_button(midleft=(420, 650))
        self.new_record = False

    def enter(self) -> None:
        self.app.audio.play_sound(s.CLEAR_SOUND)
        self.new_record = self.app.record_time(self.time_used)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.restart.clicked(event):
            self.click()
            self.app.change(self.game.restart())
        elif self.exit.clicked(event):
            self.click()
            self.app.change(MenuScene(self.app))

    def update(self, dt: float) -> None:
        self.frame_clock += dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(s.ORANGE)
        surface.blit(self.logo, self.logo.get_rect(center=(CENTER_X, 110)))
        draw_text(surface, "YOU ESCAPED", 44, s.DARK_RED, "center", (CENTER_X, 210))
        draw_text(surface, "Thank you for playing", 20, s.BLACK, "center", (CENTER_X, 270))

        frame = int(self.frame_clock / self.FRAME_TIME) % len(self.frames)
        surface.blit(self.frames[frame], (130, 370))
        draw_text(surface, f"TIME {format_time(self.time_used)}", 30, s.DARK_RED, "topleft", (420, 370))
        best = "NEW RECORD" if self.new_record else f"BEST {format_time(self.app.best_time)}"
        draw_text(surface, best, 24, s.DARK_RED, "topleft", (420, 430))
        self.restart.draw(surface)
        self.exit.draw(surface)
