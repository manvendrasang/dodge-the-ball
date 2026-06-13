# pylint: disable=missing-class-docstring, missing-function-docstring, missing-module-docstring, unused-import, no-member, attribute-defined-outside-init

import random
import math
import pygame
import constants as C
from constants import BALL_COLORS, WHITE, BG

# Lightweight standalone simulation for the menu attract-mode preview.
# Does not touch real game state, scores, or audio — purely visual.

class _AIBall:
    def __init__(self, w, h):
        self.r     = random.randint(10, 20)
        self.x     = random.uniform(self.r, w - self.r)
        self.y     = random.uniform(self.r, h - self.r)
        self.angle = random.uniform(0, 360)
        self.speed = random.uniform(2.0, 4.0)
        self.color = random.choice(BALL_COLORS)

    def update(self, w, h):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if self.x - self.r < 0 or self.x + self.r > w:
            self.angle = 180 - self.angle
            self.x = max(self.r, min(w - self.r, self.x))
        if self.y - self.r < 0 or self.y + self.r > h:
            self.angle *= -1
            self.y = max(self.r, min(h - self.r, self.y))

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        gr = self.r + 5
        gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*self.color, 50), (gr, gr), gr)
        surface.blit(gs, (cx - gr, cy - gr))
        pygame.draw.circle(surface, self.color, (cx, cy), self.r)


class AttractMode:
    """
    AI-controlled preview that plays itself on the menu background
    after the player has been idle for a while.
    """
    NUM_BALLS  = 4
    AI_SPEED   = 5.5   # px/frame the AI cursor can move
    TARGET_W   = 20

    def __init__(self):
        self._w = C.WIDTH
        self._h = C.HEIGHT
        self._reset()

    def _reset(self):
        self._w = C.WIDTH
        self._h = C.HEIGHT
        self.balls  = [_AIBall(self._w, self._h) for _ in range(self.NUM_BALLS)]
        self.ai_x   = self._w / 2
        self.ai_y   = self._h / 2
        self.tx     = random.uniform(self.TARGET_W, self._w - self.TARGET_W)
        self.ty     = random.uniform(self.TARGET_W, self._h - self.TARGET_W)
        self.score  = 0
        self._trail = []

    def update(self):
        # resolution may have changed since init
        if self._w != C.WIDTH or self._h != C.HEIGHT:
            self._reset()

        for b in self.balls:
            b.update(self._w, self._h)

        # AI: move toward target while avoiding nearby balls
        dx = self.tx - self.ai_x
        dy = self.ty - self.ai_y
        dist = math.hypot(dx, dy)
        move_x, move_y = 0.0, 0.0
        if dist > 1:
            move_x = dx / dist
            move_y = dy / dist

        # avoidance: steer away from any ball within danger radius
        for b in self.balls:
            bx, by = b.x - self.ai_x, b.y - self.ai_y
            bdist  = math.hypot(bx, by)
            danger = b.r + 60
            if bdist < danger and bdist > 0:
                # push away proportional to how close it is
                strength = (danger - bdist) / danger
                move_x  -= (bx / bdist) * strength * 1.8
                move_y  -= (by / bdist) * strength * 1.8

        norm = math.hypot(move_x, move_y)
        if norm > 0:
            move_x /= norm
            move_y /= norm

        self.ai_x += move_x * self.AI_SPEED
        self.ai_y += move_y * self.AI_SPEED
        self.ai_x = max(10, min(self._w - 10, self.ai_x))
        self.ai_y = max(10, min(self._h - 10, self.ai_y))

        # trail
        self._trail.append((self.ai_x, self.ai_y))
        if len(self._trail) > 14:
            self._trail.pop(0)

        # collect target
        tcx, tcy = self.tx + self.TARGET_W/2, self.ty + self.TARGET_W/2
        if math.hypot(self.ai_x - tcx, self.ai_y - tcy) <= 10 + self.TARGET_W:
            self.score += 1
            self.tx = random.uniform(self.TARGET_W, self._w - self.TARGET_W)
            self.ty = random.uniform(self.TARGET_W, self._h - self.TARGET_W)

        # "death" — if a ball touches AI cursor, just nudge it away hard (never truly dies)
        for b in self.balls:
            if math.hypot(self.ai_x - b.x, self.ai_y - b.y) <= b.r + 10:
                away_x = self.ai_x - b.x
                away_y = self.ai_y - b.y
                d = math.hypot(away_x, away_y) or 1
                self.ai_x += (away_x/d) * 8
                self.ai_y += (away_y/d) * 8
                self.ai_x = max(10, min(self._w - 10, self.ai_x))
                self.ai_y = max(10, min(self._h - 10, self.ai_y))

    def draw(self, surface):
        # dim everything slightly so it reads as "background"
        for b in self.balls:
            b.draw(surface)
        # target
        pygame.draw.rect(surface, (200, 80, 140),
                        (self.tx, self.ty, self.TARGET_W, self.TARGET_W), border_radius=3)
        pygame.draw.rect(surface, WHITE,
                        (self.tx, self.ty, self.TARGET_W, self.TARGET_W), 1, border_radius=3)
        # trail
        n = len(self._trail)
        for i, (x, y) in enumerate(self._trail):
            frac  = (i + 1) / max(n, 1)
            r     = max(1, int(8 * frac))
            alpha = int(90 * frac * frac)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (r, r), r)
            surface.blit(s, (int(x) - r, int(y) - r))
        # AI cursor
        pygame.draw.circle(surface, (220, 220, 230), (int(self.ai_x), int(self.ai_y)), 10)
        pygame.draw.circle(surface, WHITE, (int(self.ai_x), int(self.ai_y)), 10, 1)

    def draw_label(self, surface):
        lbl  = C.FONT_SMALL.render(f"AUTOPLAY DEMO   SCORE {self.score}", True, (90, 92, 120))
        surface.blit(lbl, (C.WIDTH//2 - lbl.get_width()//2, C.HEIGHT - 36))
