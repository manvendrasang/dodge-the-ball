# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, broad-exception-caught

import pygame

# window - updated at runtime by set_resolution()
WIDTH, HEIGHT = 1100, 680
FPS   = 60
MODES = ["classic", "shrink", "hardcore"]

def set_resolution(w, h):
    """Called once after pygame.init() with the actual display size."""
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = w, h

# theme colors - high contrast dark neon
BG        = (10,  12,  20)   # near-black blue-tinted
BG2       = (16,  18,  32)   # slightly lighter for panels
P_COLOR   = (255, 255, 255)
WHITE     = (240, 240, 255)
DARK      = (8,   8,   16)
DIM       = (60,  62,  80)
RED       = (255, 55,  55)
YELLOW    = (255, 210, 30)
BLUE      = (30,  140, 255)
GREEN     = (40,  230, 100)
PURPLE    = (180, 60,  255)
ORANGE    = (255, 140, 20)
CYAN      = (0,   240, 255)
TURQUOISE = (0,   220, 180)
PINK      = (255, 60,  180)
BALL_COLORS = [RED, YELLOW, BLUE, GREEN, PURPLE, ORANGE, CYAN, TURQUOISE, PINK]

# button colors - visible even without hover
BTN_LEADER = (40,  44,  80)
BTN_QUIT   = (80,  20,  20)
BTN_LEADER_H = (80,  90,  180)
BTN_QUIT_H   = (180, 40,  40)

# powerup types
PU_SLOWMO  = "slowmo"
PU_SHIELD  = "shield"
PU_MULTI30 = "multi30"
PU_MULTI90 = "multi90"
PU_GHOST   = "ghost"

PU_COLOR = {
    PU_SLOWMO:  CYAN,
    PU_SHIELD:  GREEN,
    PU_MULTI30: YELLOW,
    PU_MULTI90: ORANGE,
    PU_GHOST:   (200, 200, 255),
}
PU_LABEL = {
    PU_SLOWMO:  "SLOW",
    PU_SHIELD:  "SHIELD",
    PU_MULTI30: "x2 30s",
    PU_MULTI90: "x2 90s",
    PU_GHOST:   "GHOST",
}
PU_DURATION = {
    PU_SLOWMO:  8  * FPS,
    PU_SHIELD:  6  * FPS,
    PU_MULTI30: 30 * FPS,
    PU_MULTI90: 90 * FPS,
    PU_GHOST:   5  * FPS,
}
PU_SPAWN_INTERVAL = 15 * FPS
PU_CHANCE         = 0.45

# ball schedule
BALL_SCHEDULE = {
    "classic":  [(0,5),(2,5),(5,6),(10,7),(15,8),(20,9),(30,10)],
    "shrink":   [(0,5),(2,5),(5,6),(10,7),(15,8),(20,9),(30,10)],
    "hardcore": [(0,6),(2,6),(5,7),(8,8),(12,9),(18,10),(25,11),(35,12)],
}
BALL_MAX_SCORE = {"classic":50,"shrink":50,"hardcore":70}
PERIODIC_BALL_INTERVAL = 10

# speed scaling
SPEED_K      = {"classic":1.4,"shrink":1.4,"hardcore":2.2}
SPEED_FACTOR = 0.18

# ball types
HEAVY_CHANCE  = 0.30
HEAVY_RADIUS  = 22
HEAVY_SPEED_M = 0.55
LIGHT_RADIUS  = 12
LIGHT_SPEED_M = 1.40

# homing
HOMING_ACTIVATE_SCORE = 20
HOMING_CHANCE         = 0.35
HOMING_TURN_RATE      = 1.8

# shrink zone
SHRINK_STEP     = 18
SHRINK_INTERVAL = 12 * FPS
SHRINK_MIN_SIZE = 200

# walls
WALL_SPAWN_INTERVAL = 18 * FPS
WALL_DURATION       = 6  * FPS
WALL_THICKNESS      = 18
WALL_COLOR          = (200, 50, 50)
WALL_CHANCE         = 0.6

# player
P_RADIUS   = 10
BALL_RADIUS = P_RADIUS + 2

# trail
TRAIL_LEN    = 18
TRAIL_SHRINK = 0.82  # radius multiplier per older point

# fonts
FONT_TITLE = None
FONT_HUD   = None
FONT_SMALL = None
FONT_BIG   = None

def init_fonts():
    global FONT_TITLE, FONT_HUD, FONT_SMALL, FONT_BIG
    # crisp geometric fonts - fall back gracefully on Windows
    for name in ("Bahnschrift", "Consolas", "Segoe UI", "Arial"):
        try:
            FONT_TITLE = pygame.font.SysFont(name, 88, bold=True)
            FONT_BIG   = pygame.font.SysFont(name, 58, bold=True)
            FONT_HUD   = pygame.font.SysFont(name, 26, bold=False)
            FONT_SMALL = pygame.font.SysFont(name, 19, bold=False)
            break
        except Exception:
            continue
