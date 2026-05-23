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
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((200, 20, 20, alpha))
            surface.blit(overlay, (0, 0))
        # powerup glow
        if self.glow_frames > 0 and self.glow_color:
            alpha = int(90 * self.glow_frames / 45)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((*self.glow_color, alpha))
            surface.blit(overlay, (0, 0))
        # shrink zone alert
        if self.alert_frames > 0:
            alpha = min(255, self.alert_frames * 5)
            lbl = C.FONT_BIG.render(self.alert_text, True, (255, 80, 80))
            lbl.set_alpha(alpha)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, HEIGHT//2 - 40))
