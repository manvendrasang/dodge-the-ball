# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement

import pygame

# window
WIDTH, HEIGHT = 1100, 680
FPS = 60
MODES = ["classic", "shrink", "hardcore"]

# colors
BG        = (30, 30, 38)
P_COLOR   = (249, 231, 159)
WHITE     = (230, 230, 230)
DARK      = (15, 15, 20)
RED       = (203, 67,  53)
YELLOW    = (241, 196, 15)
BLUE      = (46,  134, 193)
GREEN     = (34,  153, 84)
PURPLE    = (136, 78,  160)
ORANGE    = (214, 137, 16)
CYAN      = (0,   255, 255)
TURQUOISE = (64,  224, 208)
PINK      = (255, 105, 180)
BALL_COLORS = [RED, YELLOW, BLUE, GREEN, PURPLE, ORANGE, CYAN, TURQUOISE, PINK]

# powerup types
PU_SLOWMO   = "slowmo"
PU_SHIELD   = "shield"
PU_MULTI30  = "multi30"
PU_MULTI90  = "multi90"

PU_COLOR = {
    PU_SLOWMO:  CYAN,
    PU_SHIELD:  GREEN,
    PU_MULTI30: YELLOW,
    PU_MULTI90: ORANGE,
}
PU_LABEL = {
    PU_SLOWMO:  "SLOW",
    PU_SHIELD:  "SHIELD",
    PU_MULTI30: "x2 30s",
    PU_MULTI90: "x2 90s",
}
PU_DURATION = {
    PU_SLOWMO:  8  * FPS,
    PU_SHIELD:  6  * FPS,
    PU_MULTI30: 30 * FPS,
    PU_MULTI90: 90 * FPS,
}
PU_SPAWN_INTERVAL = 15 * FPS  # every 15s a powerup may spawn
PU_CHANCE         = 0.45      # 45% chance each interval

# ball spawn schedule per mode: list of (score_threshold, base_speed)
# after the list is exhausted balls spawn every PERIODIC_BALL_INTERVAL score
BALL_SCHEDULE = {
    "classic":   [(0,5),(2,5),(5,6),(10,7),(15,8),(20,9),(30,10)],
    "shrink":    [(0,5),(2,5),(5,6),(10,7),(15,8),(20,9),(30,10)],
    "hardcore":  [(0,6),(2,6),(5,7),(8,8),(12,9),(18,10),(25,11),(35,12)],
}
BALL_MAX_SCORE = {
    "classic":  50,
    "shrink":   50,
    "hardcore": 70,
}
PERIODIC_BALL_INTERVAL = 10  # add 1 ball every N score after schedule exhausted

# speed scaling: speed = base + k * log(1 + score * factor)
# keeps increasing but flattens
SPEED_K = {
    "classic":  1.4,
    "shrink":   1.4,
    "hardcore": 2.2,
}
SPEED_FACTOR = 0.18

# ball mix: probability a new ball is "heavy" (large slow)
HEAVY_CHANCE  = 0.30
HEAVY_RADIUS  = 22
HEAVY_SPEED_M = 0.55  # multiplied on base speed
LIGHT_RADIUS  = 12
LIGHT_SPEED_M = 1.40

# homing balls (hardcore only)
HOMING_ACTIVATE_SCORE = 20
HOMING_CHANCE         = 0.35  # chance a new ball in hardcore is homing
HOMING_TURN_RATE      = 1.8   # degrees per frame toward player

# shrink zone
SHRINK_INITIAL_MARGIN = 0
SHRINK_STEP           = 18    # px per shrink event
SHRINK_INTERVAL       = 12 * FPS  # every 12s
SHRINK_MIN_SIZE       = 200   # minimum zone dimension

# walls (hardcore)
WALL_SPAWN_INTERVAL   = 18 * FPS
WALL_DURATION         = 6  * FPS
WALL_THICKNESS        = 18
WALL_COLOR            = (180, 60, 60)
WALL_CHANCE           = 0.6

# player
P_RADIUS     = 10
BALL_RADIUS  = P_RADIUS + 2  # default, overridden per type

# fonts (loaded once in main after pygame.init)
FONT_TITLE  = None
FONT_HUD    = None
FONT_SMALL  = None
FONT_BIG    = None

def init_fonts():
    global FONT_TITLE, FONT_HUD, FONT_SMALL, FONT_BIG
    FONT_TITLE = pygame.font.SysFont("Agency FB", 90)
    FONT_BIG   = pygame.font.SysFont("Agency FB", 60)
    FONT_HUD   = pygame.font.SysFont("Forte", 28)
    FONT_SMALL = pygame.font.SysFont("Forte", 20)