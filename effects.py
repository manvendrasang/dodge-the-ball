# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, multiple-statements

import pygame
import constants as C
from constants import *

class EffectsManager:
    def __init__(self):
        self.shake_frames    = 0
        self.shake_intensity = 0
        self.red_flash       = 0
        self.glow_color      = None
        self.glow_frames     = 0
        self.alert_text      = ""
        self.alert_frames    = 0
        self._offset         = (0, 0)

    def trigger_death(self):
        self.shake_frames    = 28
        self.shake_intensity = 14
        self.red_flash       = 40

    def trigger_powerup(self, kind):
        self.glow_color  = PU_COLOR[kind]
        self.glow_frames = 45

    def trigger_shrink_alert(self):
        self.alert_text   = "! ZONE SHRINKING !"
        self.alert_frames = 90

    def trigger_levelup(self, level):
        self.alert_text   = f"LEVEL  {level}"
        self.alert_frames = 100
        self.glow_color   = (255, 255, 255)
        self.glow_frames  = 30

    def get_offset(self):
        return self._offset

    def update(self):
        if self.shake_frames > 0:
            import random
            i = int(self.shake_intensity)
            self._offset = (random.randint(-i, i), random.randint(-i, i))
            self.shake_frames    -= 1
            self.shake_intensity  = max(0, self.shake_intensity - 0.4)
        else:
            self._offset = (0, 0)
        if self.red_flash   > 0: self.red_flash   -= 1
        if self.glow_frames > 0: self.glow_frames  -= 1
        if self.alert_frames > 0: self.alert_frames -= 1

    def draw_overlays(self, surface):
        # red death flash
        if self.red_flash > 0:
            alpha = int(160 * self.red_flash / 40)
            overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 20, 20, alpha))
            surface.blit(overlay, (0, 0))
        # powerup glow
        if self.glow_frames > 0 and self.glow_color:
            alpha = int(90 * self.glow_frames / 45)
            overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.glow_color, alpha))
            surface.blit(overlay, (0, 0))
        # shrink zone / level up alert
        if self.alert_frames > 0:
            alpha     = min(255, self.alert_frames * 4)
            is_level  = self.alert_text.startswith("LEVEL")
            col       = (80, 240, 255) if is_level else (255, 80, 80)
            font      = C.FONT_TITLE if is_level else C.FONT_BIG
            lbl = font.render(self.alert_text, True, col)
            lbl.set_alpha(alpha)
            surface.blit(lbl, (C.WIDTH//2 - lbl.get_width()//2, C.HEIGHT//2 - 50))
