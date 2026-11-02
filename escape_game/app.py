"""Window, main loop and state shared between scenes."""
from pathlib import Path

import pygame

from . import settings as s
from . import storage
from .assets import Audio, load_image
from .scenes import MenuScene, Scene


class App:
    def __init__(self, save_file: Path = s.SAVE_FILE) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        pygame.display.set_caption(s.TITLE)
        pygame.display.set_icon(load_image("Button/icon.png"))
        self.clock = pygame.time.Clock()
        self.audio = Audio()
        self.save_file = save_file
        self.best_time = storage.load_best_time(save_file)
        self.running = True
        self.scene: Scene = MenuScene(self)
        self.scene.enter()

    def change(self, scene: Scene) -> None:
        self.scene = scene
        scene.enter()

    def quit(self) -> None:
        self.running = False

    def record_time(self, seconds: float) -> bool:
        """Store a clear time; True when it beats the previous best."""
        if self.best_time is not None and seconds >= self.best_time:
            return False
        self.best_time = seconds
        storage.save_best_time(self.save_file, seconds)
        return True

    def tick(self, dt: float) -> None:
        """Advance the game by one frame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.audio.toggle_mute()
            else:
                self.scene.handle_event(event)
        self.scene.update(dt)
        self.scene.draw(self.screen)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(s.FPS) / 1000
            self.tick(min(dt, s.MAX_FRAME_TIME))
            pygame.display.flip()
        pygame.quit()


def main() -> None:
    App().run()
