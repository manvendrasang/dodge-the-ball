# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument, unused-variable

import random
import math
import pygame
from constants import *
from entities import Ball, Target, PowerUp, Wall
from effects import EffectsManager
from scores import submit_score
from ui import draw_hud

# pre-allocated glow surface pool for trail (avoids per-frame alloc)
_TRAIL_SURFS = {}
def _get_trail_surf(r, alpha, color=(255, 255, 255)):
    key = (r, alpha, color)
    if key not in _TRAIL_SURFS:
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (r, r), r)
        _TRAIL_SURFS[key] = s
    return _TRAIL_SURFS[key]


def _make_ball(score, mode):
    schedule   = BALL_SCHEDULE[mode]
    base_speed = schedule[0][1]
    for threshold, spd in schedule:
        if score >= threshold:
            base_speed = spd
    heavy  = random.random() < HEAVY_CHANCE
    homing = (mode == "hardcore" and
            score >= HOMING_ACTIVATE_SCORE and
            random.random() < HOMING_CHANCE)
    b = Ball(base_speed, homing=homing, heavy=heavy)
    b.set_position_random_edge()
    return b


def _should_add_ball(balls, score, mode):
    if score > BALL_MAX_SCORE[mode]:
        return False
    schedule = BALL_SCHEDULE[mode]
    for i, (threshold, _) in enumerate(schedule):
        if score >= threshold and len(balls) <= i:
            return True
    if len(balls) >= len(schedule):
        expected = len(schedule) + (score - schedule[-1][0]) // PERIODIC_BALL_INTERVAL
        expected = min(expected, len(schedule) + 8)
        if len(balls) < expected:
            return True
    return False


class GameSession:
    def __init__(self, mode, display, clock):
        self.mode         = mode
        self.display      = display
        self.clock        = clock
        self.score        = 0
        self.effects      = EffectsManager()
        self.balls        = []
        self.target       = Target()
        self.powerups     = []
        self.walls        = []
        self.active_pu    = {}
        self.shield       = False
        self.lives        = 1 if mode == "hardcore" else 0
        self.dead         = False
        self.zone_rect    = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self._pu_timer    = 5 * FPS
        self._wall_timer  = WALL_SPAWN_INTERVAL
        self._shrink_timer = SHRINK_INTERVAL
        # trail: list of (x, y) deques
        self._trail       = []
        self.balls.append(_make_ball(0, mode))
        self.target.respawn(self.zone_rect if mode == "shrink" else None)
        # reusable surfaces
        self._zone_overlay = None
        self._zone_overlay_rect = None

    @property
    def slowmo_active(self):
        return PU_SLOWMO in self.active_pu

    @property
    def ghost_active(self):
        return PU_GHOST in self.active_pu

    def _apply_slowmo(self, on):
        for b in self.balls:
            b.slowmo = on

    def collect_powerup(self, kind):
        self.active_pu[kind] = PU_DURATION[kind]
        self.effects.trigger_powerup(kind)
        if kind == PU_SHIELD:
            self.shield = True
        if kind == PU_SLOWMO:
            self._apply_slowmo(True)

    def update_powerups(self):
        expired = [k for k, v in self.active_pu.items() if v <= 1]
        for k in expired:
            del self.active_pu[k]
            if k == PU_SHIELD:
                self.shield = False
            if k == PU_SLOWMO:
                self._apply_slowmo(False)
        for k in self.active_pu:
            self.active_pu[k] -= 1

    def handle_death(self):
        if self.shield:
            self.shield = False
            self.active_pu.pop(PU_SHIELD, None)
            return
        if self.lives > 0:
            self.lives -= 1
            self.effects.trigger_death()
            return
        self.dead = True
        self.effects.trigger_death()

    def update(self):
        self.effects.update()
        if self.dead:
            return
        ppos = pygame.mouse.get_pos()
        zone = self.zone_rect if self.mode == "shrink" else None

        # update trail
        self._trail.append(ppos)
        if len(self._trail) > TRAIL_LEN:
            self._trail.pop(0)

        # update balls
        for b in self.balls:
            b.update_speed(self.score, self.mode)
            b.move(ppos, zone)
            if not self.ghost_active and b.collides_with_player(*ppos, P_RADIUS):
                self.handle_death()
                if self.dead:
                    return

        # target
        if self.target.player_overlap(*ppos, P_RADIUS):
            mult = 2 if (PU_MULTI30 in self.active_pu or PU_MULTI90 in self.active_pu) else 1
            self.score += 1 * mult
            self.target.respawn(zone)
            if _should_add_ball(self.balls, self.score, self.mode):
                self.balls.append(_make_ball(self.score, self.mode))

        # powerup spawning (classic + shrink only)
        if self.mode != "hardcore":
            self._pu_timer -= 1
            if self._pu_timer <= 0:
                self._pu_timer = PU_SPAWN_INTERVAL
                if random.random() < PU_CHANCE:
                    self.powerups.append(PowerUp(zone))

        # powerup collection
        for pu in self.powerups:
            if pu.alive and pu.player_overlap(*ppos, P_RADIUS):
                self.collect_powerup(pu.kind)
                pu.alive = False
        self.powerups = [p for p in self.powerups if p.alive]
        self.update_powerups()

        # walls (hardcore)
        if self.mode == "hardcore":
            self._wall_timer -= 1
            if self._wall_timer <= 0:
                self._wall_timer = WALL_SPAWN_INTERVAL
                if random.random() < WALL_CHANCE:
                    self.walls.append(Wall(zone))
            for w in self.walls:
                w.update()
                if w.blocks_player(*ppos, P_RADIUS):
                    self.handle_death()
                    if self.dead:
                        return
            self.walls = [w for w in self.walls if w.alive]

        # shrink zone
        if self.mode == "shrink":
            self._shrink_timer -= 1
            if self._shrink_timer <= 0:
                self._shrink_timer = SHRINK_INTERVAL
                self._do_shrink()

    def _do_shrink(self):
        zr    = self.zone_rect
        new_w = zr.width  - SHRINK_STEP * 2
        new_h = zr.height - SHRINK_STEP * 2
        if new_w < SHRINK_MIN_SIZE or new_h < SHRINK_MIN_SIZE:
            return
        self.zone_rect = pygame.Rect(zr.x + SHRINK_STEP, zr.y + SHRINK_STEP, new_w, new_h)
        self._zone_overlay = None  # invalidate cached overlay
        self.effects.trigger_shrink_alert()
        if not self.zone_rect.collidepoint(self.target.x, self.target.y):
            self.target.respawn(self.zone_rect)

    def _draw_zone_overlay(self, surface):
        # cache the dark-border overlay; only regenerate on zone change
        if self._zone_overlay is None:
            self._zone_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            self._zone_overlay.fill((0, 0, 0, 0))
            for r in [
                pygame.Rect(0, 0, self.zone_rect.left, HEIGHT),
                pygame.Rect(self.zone_rect.right, 0, WIDTH - self.zone_rect.right, HEIGHT),
                pygame.Rect(0, 0, WIDTH, self.zone_rect.top),
                pygame.Rect(0, self.zone_rect.bottom, WIDTH, HEIGHT - self.zone_rect.bottom),
            ]:
                self._zone_overlay.fill((0, 0, 0, 110), r)
        surface.blit(self._zone_overlay, (0, 0))
        pygame.draw.rect(surface, (80, 80, 140), self.zone_rect, 2)

    def draw(self):
        ox, oy   = self.effects.get_offset()
        game_surf = pygame.Surface((WIDTH, HEIGHT))
        game_surf.fill(BG)

        if self.mode == "shrink":
            self._draw_zone_overlay(game_surf)

        for w in self.walls:
            w.draw(game_surf)
        for b in self.balls:
            b.draw(game_surf)
        for pu in self.powerups:
            pu.draw(game_surf)
        self.target.draw(game_surf)

        # draw trail then player
        self._draw_trail(game_surf)
        ppos = pygame.mouse.get_pos()
        if self.ghost_active:
            frames_left = self.active_pu.get(PU_GHOST, 0)
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.008))
            # outer halo
            halo_r = int(P_RADIUS * 2.5 + pulse * 6)
            halo_s = pygame.Surface((halo_r*2, halo_r*2), pygame.SRCALPHA)
            pygame.draw.circle(halo_s, (200, 200, 255, int(50 + pulse * 60)),
                               (halo_r, halo_r), halo_r)
            game_surf.blit(halo_s, (ppos[0] - halo_r, ppos[1] - halo_r))
            # translucent player body
            ghost_s = pygame.Surface((P_RADIUS*2+2, P_RADIUS*2+2), pygame.SRCALPHA)
            alpha = int(80 + pulse * 80)
            pygame.draw.circle(ghost_s, (220, 220, 255, alpha),
                            (P_RADIUS+1, P_RADIUS+1), P_RADIUS)
            pygame.draw.circle(ghost_s, (255, 255, 255, alpha),
                            (P_RADIUS+1, P_RADIUS+1), P_RADIUS, 1)
            game_surf.blit(ghost_s, (ppos[0] - P_RADIUS - 1, ppos[1] - P_RADIUS - 1))
        else:
            # normal player glow + body
            pg_s = pygame.Surface((P_RADIUS*4, P_RADIUS*4), pygame.SRCALPHA)
            pygame.draw.circle(pg_s, (255, 255, 255, 40), (P_RADIUS*2, P_RADIUS*2), P_RADIUS*2)
            game_surf.blit(pg_s, (ppos[0] - P_RADIUS*2, ppos[1] - P_RADIUS*2))
            pygame.draw.circle(game_surf, P_COLOR, ppos, P_RADIUS)
            pygame.draw.circle(game_surf, WHITE,   ppos, P_RADIUS, 1)

        lives_arg = self.lives if self.mode == "hardcore" else None
        draw_hud(game_surf, self.score, self.mode, self.active_pu, lives_arg, self.shield)
        self.effects.draw_overlays(game_surf)
        self.display.blit(game_surf, (ox, oy))

    def _draw_trail(self, surface):
        pts = self._trail
        n   = len(pts)
        if n < 2:
            return
        # build interpolated point list for smooth curve
        smooth = []
        for i in range(n - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            smooth.append((x0, y0))
            smooth.append(((x0 + x1) / 2, (y0 + y1) / 2))  # midpoint
        smooth.append(pts[-1])
        total = len(smooth)
        for i, pos in enumerate(smooth):
            frac  = (i + 1) / total          # 0..1, newest = 1
            r     = max(1, int(P_RADIUS * 0.9 * frac))
            alpha = int(150 * frac ** 2)      # quadratic fade, near-zero at tail
            # color shifts from blue-white at head to purple at tail
            r_c = int(160 + 95 * frac)
            g_c = int(100 * frac)
            b_c = 255
            s = _get_trail_surf(r, alpha, (r_c, g_c, b_c))
            surface.blit(s, (int(pos[0]) - r, int(pos[1]) - r))


def run_session(mode, display, clock) -> int:
    pygame.mouse.set_visible(False)
    session = GameSession(mode, display, clock)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                raise SystemExit
        session.update()
        session.draw()
        pygame.display.update()
        clock.tick(FPS)
        if session.dead and session.effects.shake_frames == 0 and session.effects.red_flash == 0:
            break
    pygame.mouse.set_visible(True)
    submit_score(mode, session.score)
    return session.score
