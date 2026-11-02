"""Game-wide constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PICTURE_DIR = ROOT / "picture"
SOUND_DIR = ROOT / "sound"
LEVEL_DIR = ROOT / "levels"
SAVE_FILE = ROOT / "save.json"
FONT_FILE = PICTURE_DIR / "font" / "8-BIT WONDER.TTF"

TITLE = "Escape Game"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
FPS = 60
MAX_FRAME_TIME = 0.1  # seconds; stops a stalled window from draining the timer

# Level grid
TILE_SIZE = 30
ROWS = 25
COLS = 34
TILE_TYPES = 21
TRAP_TILE = 20  # every lower tile id is a wall
LEVEL_COUNT = 13
HUD_HEIGHT = 63
HUD_ROWS = 2  # rows hidden behind the HUD; level files keep decoration there
TRAP_MARGIN = 5  # the portal art is round, so its hitbox sits inside the tile

# Player
PLAYER_SIZE = 20
PLAYER_SPEED = 2  # pixels per frame
PLAYER_SPAWN = (10, 365)
ANIMATION_COOLDOWN = 100  # milliseconds per frame

# Rules
LEVELS_TO_WIN = 10
TIME_LIMIT = 350  # seconds for the whole run
TIME_WARNING = 30  # seconds left when the HUD timer starts flashing

# Audio
MUSIC_VOLUME = 0.6
SFX_VOLUME = 1.0
MENU_MUSIC = "Kevin MacLeod Pixelland NO COPYRIGHT 8bit Music.wav"
GAME_MUSIC = "Tristan Lohengrin Happy 8bit Loop 01 NO COPYRIGHT 8bit Music.wav"
CLICK_SOUND = "Click.wav"
OVER_SOUND = "Noob.mp3"
CLEAR_SOUND = "handclap.mp3"

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_RED = (140, 0, 0)
YELLOW = (255, 235, 90)
ORANGE = (255, 165, 44)
FLOOR = (14, 12, 20)
