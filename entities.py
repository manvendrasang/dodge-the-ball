# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, multiple-statements, unused-import

import random
import math
import pygame
import constants as C
from constants import *

class Ball:
    SPAWN_FRAMES = 22  # length of entry animation

    def __init__(self, speed, homing=False, heavy=False):
        self.homing       = homing
        self.heavy        = heavy
        self.r            = HEAVY_RADIUS if heavy else LIGHT_RADIUS
        spd_mult          = HEAVY_SPEED_M if heavy else LIGHT_SPEED_M
        self.speed        = speed * spd_mult
        self.base_speed   = self.speed
        self.color        = random.choice(BALL_COLORS)
        self.angle        = random.uniform(-180, 180)
        self.x            = C.WIDTH  / 2
        self.y            = C.HEIGHT / 2
        self.slowmo       = False
        self.spawn_frames = self.SPAWN_FRAMES  # counts down to 0

    def set_position_random_edge(self):
        side = random.randint(0, 3)
        if side == 0:   self.x, self.y = random.uniform(self.r, C.WIDTH-self.r), self.r
        elif side == 1: self.x, self.y = C.WIDTH-self.r, random.uniform(self.r, C.HEIGHT-self.r)
        elif side == 2: self.x, self.y = random.uniform(self.r, C.WIDTH-self.r), C.HEIGHT-self.r
        else:           self.x, self.y = self.r, random.uniform(self.r, C.HEIGHT-self.r)
        dx = C.WIDTH/2 - self.x
        dy = C.HEIGHT/2 - self.y
        self.angle = math.degrees(math.atan2(dy, dx)) + random.uniform(-40, 40)

    def update_speed(self, score, mode):
        k        = SPEED_K[mode]
        bonus    = k * math.log(1 + score * SPEED_FACTOR)
        spd_mult = HEAVY_SPEED_M if self.heavy else LIGHT_SPEED_M
        self.speed = (self.base_speed / spd_mult + bonus) * spd_mult
        if self.slowmo:
            self.speed *= 0.38

    def move(self, player_pos, zone_rect=None):
        if self.spawn_frames > 0:
            self.spawn_frames -= 1
        if self.homing and player_pos:
            dx = player_pos[0] - self.x
            dy = player_pos[1] - self.y
            target_angle = math.degrees(math.atan2(dy, dx))
            diff = (target_angle - self.angle + 360) % 360
            if diff > 180: diff -= 360
            self.angle += max(-HOMING_TURN_RATE, min(HOMING_TURN_RATE, diff))
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, C.WIDTH, C.HEIGHT)
        if self.x - self.r < bounds.left or self.x + self.r > bounds.right:
            self.angle = 180 - self.angle
            self.x = max(bounds.left + self.r, min(bounds.right  - self.r, self.x))
        if self.y - self.r < bounds.top or self.y + self.r > bounds.bottom:
            self.angle *= -1
            self.y = max(bounds.top  + self.r, min(bounds.bottom - self.r, self.y))

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        # spawn animation
        if self.spawn_frames > 0:
            t     = self.spawn_frames / self.SPAWN_FRAMES  # 1.0→0.0 as animation plays
            frac  = 1.0 - t                                # 0.0→1.0 progress
            # ball zooms from 0 to full size
            draw_r = max(1, int(self.r * frac))
            # expanding ring burst: starts at ball size, expands outward, fades
            ring_r = int(self.r + (self.r * 3) * frac)
            ring_a = int(220 * t)                          # bright at start, gone at end
            if ring_a > 0:
                rs = pygame.Surface((ring_r*2+4, ring_r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(rs, (*self.color, ring_a), (ring_r+2, ring_r+2), ring_r, 3)
                surface.blit(rs, (cx - ring_r - 2, cy - ring_r - 2))
            # secondary tighter ring
            ring2_r = int(self.r * 0.5 + (self.r * 2.5) * frac)
            ring2_a = int(140 * t)
            if ring2_a > 0 and ring2_r > 0:
                rs2 = pygame.Surface((ring2_r*2+4, ring2_r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(rs2, (*self.color, ring2_a), (ring2_r+2, ring2_r+2), ring2_r, 2)
                surface.blit(rs2, (cx - ring2_r - 2, cy - ring2_r - 2))
            # glow scales with ball
            glow_r = draw_r + 5
            glow_s = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (*self.color, int(55 * frac)), (glow_r, glow_r), glow_r)
            surface.blit(glow_s, (cx - glow_r, cy - glow_r))
            if draw_r > 0:
                pygame.draw.circle(surface, self.color, (cx, cy), draw_r)
            return
        # normal draw
        glow_r = self.r + 6
        glow_s = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*self.color, 55), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))
        pygame.draw.circle(surface, self.color, (cx, cy), self.r)
        core_r = max(3, self.r // 3)
        cc = tuple(min(255, v + 120) for v in self.color)
        pygame.draw.circle(surface, cc, (cx, cy), core_r)
        if self.homing:
            pygame.draw.circle(surface, WHITE, (cx, cy), self.r, 2)

    def collides_with_player(self, px, py, p_radius):
        if self.spawn_frames > 0:
            return False  # invulnerable during entry animation
        return math.hypot(px - self.x, py - self.y) <= self.r + p_radius


class Target:
    def __init__(self):
        self.w     = 20
        self.h     = 20
        self.x     = C.WIDTH  // 2
        self.y     = C.HEIGHT // 2
        self.color = random.choice(BALL_COLORS)
        self._pulse = random.randint(0, 360)  # stagger so all targets don't sync

    def respawn(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, C.WIDTH, C.HEIGHT)
        margin = self.w * 2
        self.x = random.randint(bounds.left + margin, bounds.right  - margin)
        self.y = random.randint(bounds.top  + margin, bounds.bottom - margin)
        self.color = random.choice(BALL_COLORS)
        self._pulse = random.randint(0, 360)

    def update(self):
        self._pulse = (self._pulse + 3) % 360

    def draw(self, surface):
        self._pulse = (self._pulse + 3) % 360
        breath = (math.sin(math.radians(self._pulse)) + 1) / 2  # 0..1
        cx, cy = self.x + self.w//2, self.y + self.h//2
        # outer glow breathes in size and alpha
        glow_r  = int((self.w + 6) + breath * 10)
        glow_a  = int(30 + breath * 90)
        gs = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*self.color, glow_a),
                         (0, 0, glow_r*2, glow_r*2), border_radius=6)
        surface.blit(gs, (cx - glow_r, cy - glow_r))
        # inner fill brightens on peak
        bright = tuple(min(255, int(v + breath * 60)) for v in self.color)
        pygame.draw.rect(surface, bright,
                         (self.x, self.y, self.w, self.h), border_radius=3)
        # border alpha also pulses
        border_a = int(160 + breath * 95)
        border_s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(border_s, (255, 255, 255, border_a),
                         (0, 0, self.w, self.h), 2, border_radius=3)
        surface.blit(border_s, (self.x, self.y))

    def player_overlap(self, px, py, p_radius):
        cx = self.x + self.w / 2
        cy = self.y + self.h / 2
        return math.hypot(px - cx, py - cy) <= p_radius + self.w


class PowerUp:
    RADIUS = 14
    GLOW_RADII = [28, 22, 18]  # layered glow rings
    GLOW_ALPHAS = [25, 45, 70]

    def __init__(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, C.WIDTH, C.HEIGHT)
        m = self.RADIUS + 20
        self.x     = random.randint(bounds.left + m, bounds.right  - m)
        self.y     = random.randint(bounds.top  + m, bounds.bottom - m)
        self.kind  = random.choice([PU_SLOWMO, PU_SHIELD, PU_MULTI30, PU_MULTI90, PU_GHOST])
        self.color = PU_COLOR[self.kind]
        self.alive = True
        self._pulse = 0

    def draw(self, surface):
        self._pulse = (self._pulse + 4) % 360
        scale = 1 + 0.15 * math.sin(math.radians(self._pulse))
        r  = int(self.RADIUS * scale)
        cx, cy = int(self.x), int(self.y)
        # layered neon glow
        for gr, ga in zip(self.GLOW_RADII, self.GLOW_ALPHAS):
            gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            pulse_a = int(ga * (0.7 + 0.3 * math.sin(math.radians(self._pulse))))
            pygame.draw.circle(gs, (*self.color, pulse_a), (gr, gr), gr)
            surface.blit(gs, (cx - gr, cy - gr))
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        pygame.draw.circle(surface, WHITE,      (cx, cy), r, 2)

    def player_overlap(self, px, py, p_radius):
        return math.hypot(px - self.x, py - self.y) <= self.RADIUS + p_radius


class Wall:
    def __init__(self, zone_rect=None):
        bounds = zone_rect if zone_rect else pygame.Rect(0, 0, C.WIDTH, C.HEIGHT)
        horiz  = random.random() < 0.5
        margin = 80
        if horiz:
            y      = random.randint(bounds.top + margin, bounds.bottom - margin)
            length = random.randint(int(bounds.width  * 0.25), int(bounds.width  * 0.5))
            x      = random.randint(bounds.left, bounds.right - length)
            self.rect = pygame.Rect(x, y, length, WALL_THICKNESS)
        else:
            x      = random.randint(bounds.left + margin, bounds.right - margin)
            length = random.randint(int(bounds.height * 0.25), int(bounds.height * 0.5))
            y      = random.randint(bounds.top, bounds.bottom - length)
            self.rect = pygame.Rect(x, y, WALL_THICKNESS, length)
        self.timer = WALL_DURATION
        self.alive = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.alive = False

    def draw(self, surface):
        alpha = min(255, int(255 * self.timer / WALL_DURATION))
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((*WALL_COLOR, alpha))
        surface.blit(s, self.rect.topleft)
        # edge glow
        eg = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
        eg.fill((*WALL_COLOR, alpha // 4))
        surface.blit(eg, (self.rect.x - 4, self.rect.y - 4))

    def blocks_player(self, px, py, p_radius):
        return self.rect.inflate(p_radius * 2, p_radius * 2).collidepoint(px, py)
