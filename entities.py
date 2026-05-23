# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member

import random
import math
import pygame
import constants as C
from constants import *

class Ball:
    def __init__(self, speed, homing=False, heavy=False):
        self.homing  = homing
        self.heavy   = heavy
        self.r       = HEAVY_RADIUS if heavy else LIGHT_RADIUS
        spd_mult     = HEAVY_SPEED_M if heavy else LIGHT_SPEED_M
        self.speed   = speed * spd_mult
        self.base_speed = self.speed
        self.color   = random.choice(BALL_COLORS)
        self.angle   = random.uniform(-180, 180)
        self.x       = WIDTH  / 2
        self.y       = HEIGHT / 2
        self.slowmo  = False

    def set_position_random_edge(self):
        side = random.randint(0, 3)
        if side == 0:
            self.x, self.y = random.uniform(self.r, WIDTH - self.r), self.r
        elif side == 1:
            self.x, self.y = WIDTH - self.r, random.uniform(self.r, HEIGHT - self.r)
        elif side == 2:
            self.x, self.y = random.uniform(self.r, WIDTH - self.r), HEIGHT - self.r
        else:
            self.x, self.y = self.r, random.uniform(self.r, HEIGHT - self.r)
        dx = WIDTH/2 - self.x
        dy = HEIGHT/2 - self.y
        self.angle = math.degrees(math.atan2(dy, dx)) + random.uniform(-40, 40)

    def update_speed(self, score, mode):
        k = SPEED_K[mode]
        bonus = k * math.log(1 + score * SPEED_FACTOR)
        spd_mult = HEAVY_SPEED_M if self.heavy else LIGHT_SPEED_M
        self.speed = (self.base_speed / spd_mult + bonus) * spd_mult
        if self.slowmo:
            self.speed *= 0.38

    def move(self, player_pos, zone_rect=None):
        effective_speed = self.speed
        if self.homing and player_pos:
            dx  = player_pos[0] - self.x
            dy  = player_pos[1] - self.y
            target_angle = math.degrees(math.atan2(dy, dx))
            diff = (target_angle - self.angle + 360) % 360
            if diff > 180:
                diff -= 360
            turn = max(-HOMING_TURN_RATE, min(HOMING_TURN_RATE, diff))
            self.angle += turn
        self.x += effective_speed * math.cos(math.radians(self.angle))
        self.y += effective_speed * math.sin(math.radians(self.angle))
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, WIDTH, HEIGHT)
        if self.x - self.r < bounds.left or self.x + self.r > bounds.right:
            self.angle = 180 - self.angle
            self.x = max(bounds.left + self.r, min(bounds.right - self.r, self.x))
        if self.y - self.r < bounds.top or self.y + self.r > bounds.bottom:
            self.angle *= -1
            self.y = max(bounds.top + self.r, min(bounds.bottom - self.r, self.y))

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color,
            (self.x - self.r, self.y - self.r, self.r * 2, self.r * 2))
        if self.homing:
            pygame.draw.ellipse(surface, WHITE,
                (self.x - self.r, self.y - self.r, self.r * 2, self.r * 2), 2)

    def collides_with_player(self, px, py, p_radius):
        return math.hypot(px - self.x, py - self.y) <= self.r + p_radius


class Target:
    def __init__(self):
        self.w = 20
        self.h = 20
        self.x = WIDTH  // 2
        self.y = HEIGHT // 2
        self.color = random.choice(BALL_COLORS)

    def respawn(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, WIDTH, HEIGHT)
        margin = self.w * 2
        self.x = random.randint(bounds.left + margin, bounds.right  - margin)
        self.y = random.randint(bounds.top  + margin, bounds.bottom - margin)
        self.color = random.choice(BALL_COLORS)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, WHITE,      (self.x, self.y, self.w, self.h), 2)

    def player_overlap(self, px, py, p_radius):
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        return math.hypot(px - cx, py - cy) <= p_radius + self.w


class PowerUp:
    RADIUS = 14

    def __init__(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, WIDTH, HEIGHT)
        m = self.RADIUS + 20
        self.x = random.randint(bounds.left + m, bounds.right  - m)
        self.y = random.randint(bounds.top  + m, bounds.bottom - m)
        self.kind  = random.choice([PU_SLOWMO, PU_SHIELD, PU_MULTI30, PU_MULTI90])
        self.color = PU_COLOR[self.kind]
        self.alive = True
        self._pulse = 0

    def draw(self, surface):
        self._pulse = (self._pulse + 3) % 360
        scale = 1 + 0.12 * math.sin(math.radians(self._pulse))
        r = int(self.RADIUS * scale)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)
        pygame.draw.circle(surface, WHITE,      (int(self.x), int(self.y)), r, 2)
        lbl = C.FONT_SMALL.render(PU_LABEL[self.kind], True, DARK)
        surface.blit(lbl, (self.x - lbl.get_width()//2, self.y - lbl.get_height()//2))

    def player_overlap(self, px, py, p_radius):
        return math.hypot(px - self.x, py - self.y) <= self.RADIUS + p_radius


class Wall:
    def __init__(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, WIDTH, HEIGHT)
        horiz  = random.random() < 0.5
        margin = 80
        if horiz:
            y = random.randint(bounds.top + margin, bounds.bottom - margin)
            length = random.randint(int(bounds.width * 0.25), int(bounds.width * 0.5))
            x = random.randint(bounds.left, bounds.right - length)
            self.rect = pygame.Rect(x, y, length, WALL_THICKNESS)
        else:
            x = random.randint(bounds.left + margin, bounds.right - margin)
            length = random.randint(int(bounds.height * 0.25), int(bounds.height * 0.5))
            y = random.randint(bounds.top, bounds.bottom - length)
            self.rect = pygame.Rect(x, y, WALL_THICKNESS, length)
        self.timer = WALL_DURATION
        self.alive = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, surface):
        alpha = min(255, int(255 * self.timer / WALL_DURATION))
        color = (WALL_COLOR[0], WALL_COLOR[1], WALL_COLOR[2])
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((*color, alpha))
        surface.blit(s, self.rect.topleft)

    def blocks_player(self, px, py, p_radius):
        expanded = self.rect.inflate(p_radius * 2, p_radius * 2)
        return expanded.collidepoint(px, py)
