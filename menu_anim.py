# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, no-member, unused-import, attribute-defined-outside-init

import random
import math
import pygame
import constants as C
from constants import BALL_COLORS, BG

# lightweight ball for menu background only
class _MenuBall:
    def __init__(self):
        self.reset(spawn=True)

    def reset(self, spawn=False):
        self.r     = random.randint(8, 22)
        self.x     = random.uniform(self.r, C.WIDTH  - self.r)
        self.y     = random.uniform(self.r, C.HEIGHT - self.r) if spawn else -self.r
        self.angle = random.uniform(-180, 180)
        self.speed = random.uniform(1.2, 2.8)
        self.color = random.choice(BALL_COLORS)
        self._pulse = random.randint(0, 360)

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if self.x - self.r < 0 or self.x + self.r > C.WIDTH:
            self.angle = 180 - self.angle
            self.x = max(self.r, min(C.WIDTH - self.r, self.x))
        if self.y - self.r < 0 or self.y + self.r > C.HEIGHT:
            self.angle *= -1
            self.y = max(self.r, min(C.HEIGHT - self.r, self.y))
        self._pulse = (self._pulse + 2) % 360

    def draw(self, surface):
        # dim neon glow, clearly behind UI
        pulse = (math.sin(math.radians(self._pulse)) + 1) / 2
        alpha = int(30 + pulse * 25)
        cx, cy = int(self.x), int(self.y)
        gr = self.r + 5
        gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, alpha), (gr, gr), gr)
        surface.blit(gs, (cx - gr, cy - gr))
        body_s = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA)
        pygame.draw.circle(body_s, (*self.color, int(60 + pulse*40)), (self.r, self.r), self.r)
        surface.blit(body_s, (cx - self.r, cy - self.r))


class MenuAnimator:
    NUM_BALLS = 14

    def __init__(self):
        self._balls = [_MenuBall() for _ in range(self.NUM_BALLS)]
        self._grid_offset = 0

    def update(self):
        self._grid_offset = (self._grid_offset + 0.4) % 60
        for b in self._balls:
            b.update()

    def draw(self, surface):
        # scrolling grid
        off = int(self._grid_offset)
        for x in range(-60 + off, C.WIDTH + 60, 60):
            pygame.draw.line(surface, (18, 20, 34), (x, 0), (x, C.HEIGHT))
        for y in range(-60 + off, C.HEIGHT + 60, 60):
            pygame.draw.line(surface, (18, 20, 34), (0, y), (C.WIDTH, y))
        for b in self._balls:
            b.draw(surface)
