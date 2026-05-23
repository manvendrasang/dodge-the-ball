# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument

import random
import math
import pygame
from constants import *
from entities import Ball, Target, PowerUp, Wall
from effects import EffectsManager
from scores import submit_score
from ui import draw_hud


def _make_ball(score, mode):
    schedule = BALL_SCHEDULE[mode]
    # pick base speed from last threshold reached
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


def _should_add_ball(balls, score, mode, schedule_used):
    max_score = BALL_MAX_SCORE[mode]
    if score > max_score:
        return False
    schedule = BALL_SCHEDULE[mode]
    # check fixed schedule
    for i, (threshold, _) in enumerate(schedule):
        if score >= threshold and len(balls) <= i:
            return True
    # periodic after schedule exhausted
    if len(balls) >= len(schedule):
        expected = len(schedule) + (score - schedule[-1][0]) // PERIODIC_BALL_INTERVAL
        expected = min(expected, len(schedule) + 8)
        if len(balls) < expected:
            return True
    return False


class GameSession:
    """Shared state and logic for one play session."""
    def __init__(self, mode: str, display, clock):
        self.mode      = mode
        self.display   = display
        self.clock     = clock
        self.score     = 0
        self.effects   = EffectsManager()
        self.balls     = []
        self.target    = Target()
        self.powerups  = []
        self.walls     = []
        self.active_pu = {}  # kind -> frames_remaining
        self.shield    = False
        self.lives     = 1 if mode == "hardcore" else 0  # extra life in HC
        self.dead      = False
        self.zone_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self._pu_timer = 5 * FPS  # first powerup appears after ~5s
        self._wall_timer = WALL_SPAWN_INTERVAL
        self._shrink_timer = SHRINK_INTERVAL
        self._schedule_used = False
        # spawn first ball
        self.balls.append(_make_ball(0, mode))
        self.target.respawn(self.zone_rect if mode == "shrink" else None)

    @property
    def slowmo_active(self):
        return PU_SLOWMO in self.active_pu

    def _apply_slowmo(self, on: bool):
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
        expired = []
        for kind in list(self.active_pu):
            self.active_pu[kind] -= 1
            if self.active_pu[kind] <= 0:
                expired.append(kind)
        for kind in expired:
            del self.active_pu[kind]
            if kind == PU_SHIELD:
                self.shield = False
            if kind == PU_SLOWMO:
                self._apply_slowmo(False)

    def handle_death(self):
        if self.shield:
            self.shield = False
            if PU_SHIELD in self.active_pu:
                del self.active_pu[PU_SHIELD]
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

        # update balls
        for b in self.balls:
            b.update_speed(self.score, self.mode)
            b.move(ppos, zone)
            if b.collides_with_player(*ppos, P_RADIUS):
                self.handle_death()
                if self.dead:
                    return

        # check target
        if self.target.player_overlap(*ppos, P_RADIUS):
            mult = 2 if (PU_MULTI30 in self.active_pu or PU_MULTI90 in self.active_pu) else 1
            self.score += 1 * mult
            self.target.respawn(zone)
            if _should_add_ball(self.balls, self.score, self.mode, self._schedule_used):
                self.balls.append(_make_ball(self.score, self.mode))

        # powerup spawning
        if self.mode != "hardcore":
            self._pu_timer -= 1
            if self._pu_timer <= 0:
                self._pu_timer = PU_SPAWN_INTERVAL
                if random.random() < PU_CHANCE:
                    self.powerups.append(PowerUp(zone))

        # powerup collection
        for pu in self.powerups[:]:
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
        zr = self.zone_rect
        new_w = zr.width  - SHRINK_STEP * 2
        new_h = zr.height - SHRINK_STEP * 2
        if new_w < SHRINK_MIN_SIZE or new_h < SHRINK_MIN_SIZE:
            return
        self.zone_rect = pygame.Rect(
            zr.x + SHRINK_STEP, zr.y + SHRINK_STEP, new_w, new_h)
        self.effects.trigger_shrink_alert()
        # push target inside new zone
        if not self.zone_rect.collidepoint(self.target.x, self.target.y):
            self.target.respawn(self.zone_rect)

    def draw(self):
        ox, oy = self.effects.get_offset()
        game_surf = pygame.Surface((WIDTH, HEIGHT))
        game_surf.fill(BG)

        # shrink zone boundary
        if self.mode == "shrink":
            pygame.draw.rect(game_surf, (70, 70, 100), self.zone_rect, 3)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for edge_rect in [
                pygame.Rect(0, 0, self.zone_rect.left, HEIGHT),
                pygame.Rect(self.zone_rect.right, 0, WIDTH - self.zone_rect.right, HEIGHT),
                pygame.Rect(0, 0, WIDTH, self.zone_rect.top),
                pygame.Rect(0, self.zone_rect.bottom, WIDTH, HEIGHT - self.zone_rect.bottom),
            ]:
                overlay.fill((0, 0, 0, 80), edge_rect)
            game_surf.blit(overlay, (0, 0))

        for w in self.walls:
            w.draw(game_surf)
        for b in self.balls:
            b.draw(game_surf)
        for pu in self.powerups:
            pu.draw(game_surf)
        self.target.draw(game_surf)
        ppos = pygame.mouse.get_pos()
        pygame.draw.circle(game_surf, P_COLOR, ppos, P_RADIUS)

        lives_arg = self.lives if self.mode == "hardcore" else None
        draw_hud(game_surf, self.score, self.mode, self.active_pu, lives_arg, self.shield)
        self.effects.draw_overlays(game_surf)
        self.display.blit(game_surf, (ox, oy))


def run_session(mode: str, display, clock) -> int:
    """Run one game session; returns final score."""
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
        # stay in loop until dead AND full shake+flash animation has played out
        if session.dead and session.effects.shake_frames == 0 and session.effects.red_flash == 0:
            break
    pygame.mouse.set_visible(True)
    submit_score(mode, session.score)
    return session.score
