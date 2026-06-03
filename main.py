# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import, line-too-long, invalid-name
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument, no-name-in-module, multiple-statements

import sys
import pygame
import constants as C
from constants import init_fonts, set_resolution, MODES, FPS
from ui import draw_main_menu, draw_game_over, draw_leaderboard, draw_settings
from modes import run_session
from menu_anim import MenuAnimator
from audio import get_audio
from settings import load as load_cfg, save as save_cfg

pygame.init()
info    = pygame.display.Info()
SW, SH  = info.current_w, info.current_h
cfg     = load_cfg()
_flags  = pygame.FULLSCREEN if cfg.get("fullscreen", True) else 0
display = pygame.display.set_mode((SW, SH), _flags)
pygame.display.set_caption("Dodge The Ball!")
clock   = pygame.time.Clock()
set_resolution(SW, SH)
init_fonts()

# overlay surface reused every frame for transitions
_fade_surf = pygame.Surface((SW, SH))
_fade_surf.fill((0, 0, 0))

class Transition:
    FRAMES = 18  # half-duration (fade out = 18f, fade in = 18f)

    def __init__(self):
        self._alpha      = 0
        self._state      = "idle"   # idle | out | in
        self._next_state = None
        self._callback   = None     # called at peak black (between out and in)

    @property
    def busy(self):
        return self._state != "idle"

    def go(self, next_state, callback=None):
        """Start a transition to next_state, optionally calling callback at peak."""
        if self._state != "idle":
            return  # ignore if already transitioning
        self._next_state = next_state
        self._callback   = callback
        self._state      = "out"
        self._alpha      = 0

    def update(self):
        if self._state == "out":
            self._alpha = min(255, self._alpha + 255 // self.FRAMES)
            if self._alpha >= 255:
                self._alpha = 255
                self._state = "in"
                if self._callback:
                    self._callback()
        elif self._state == "in":
            self._alpha = max(0, self._alpha - 255 // self.FRAMES)
            if self._alpha <= 0:
                self._alpha = 0
                self._state = "idle"
                self._next_state = None

    def draw(self, surface):
        if self._state == "idle":
            return
        _fade_surf.set_alpha(self._alpha)
        surface.blit(_fade_surf, (0, 0))

    def consume_next(self):
        """Return and clear the pending next_state when transition peaks."""
        s = self._next_state
        return s


state        = "menu"
current_mode = "classic"
last_score   = 0
last_stats   = {}
lb_tab       = 0
animator     = MenuAnimator()
audio        = get_audio()
_music_on    = False
trans        = Transition()

def _apply_volume():
    audio.set_volume(cfg.get("sfx_volume", 0.7))
    audio.set_music_volume(cfg.get("music_volume", 0.45))

_apply_volume()

def _toggle_fullscreen():
    global display, _fade_surf
    cfg["fullscreen"] = not cfg.get("fullscreen", True)
    save_cfg(cfg)
    flags = pygame.FULLSCREEN if cfg["fullscreen"] else 0
    display = pygame.display.set_mode((SW, SH), flags)
    _fade_surf = pygame.Surface((SW, SH))
    _fade_surf.fill((0, 0, 0))

def _go(next_state, pre_callback=None):
    """Trigger a transition. pre_callback fires at peak black if provided."""
    trans.go(next_state, callback=lambda: _apply_state_change(next_state, pre_callback))

def _apply_state_change(next_state, pre_callback=None):
    global state, _music_on
    if pre_callback:
        pre_callback()
    state = next_state
    # music housekeeping at state change
    if next_state == "game":
        audio.stop_music(); _music_on = False
    else:
        if not _music_on:
            audio.start_music(); _music_on = True


while True:
    ev_list = []
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        ev_list.append(e)

    # only process input when no transition is running
    if not trans.busy:
        if state == "menu":
            if not _music_on:
                audio.start_music(); _music_on = True
            animator.update()
            display.fill(C.BG)
            animator.draw(display)
            menu_buttons = draw_main_menu(display)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                for btn in menu_buttons:
                    if btn.clicked(ev):
                        lbl = btn.label.lower()
                        if lbl == "quit":
                            pygame.quit(); sys.exit()
                        elif lbl == "leaderboard":
                            _go("leaderboard")
                        elif lbl == "settings":
                            _go("settings")
                        elif lbl in ("classic", "shrink zone", "hardcore"):
                            current_mode = lbl.replace(" zone", "")
                            _go("game")

        elif state == "game":
            last_score, last_stats = run_session(current_mode, display, clock)
            pygame.event.clear()
            if last_score == -1:
                _go("menu")
            else:
                _go("gameover")

        elif state == "gameover":
            if not _music_on:
                audio.start_music(); _music_on = True
            over_buttons = draw_game_over(display, last_score, current_mode, last_stats)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:   _go("game")
                    if ev.key in (pygame.K_m, pygame.K_ESCAPE): _go("menu")
                for btn in over_buttons:
                    if btn.clicked(ev):
                        lbl = btn.label.lower()
                        if "restart" in lbl:  _go("game")
                        elif "menu"   in lbl: _go("menu")
                        elif "quit"   in lbl: pygame.quit(); sys.exit()

        elif state == "leaderboard":
            if not _music_on:
                audio.start_music(); _music_on = True
            lb_buttons, lb_tabs = draw_leaderboard(display, lb_tab)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    _go("menu")
                for i, tb in enumerate(lb_tabs):
                    if tb.clicked(ev): lb_tab = i
                for btn in lb_buttons:
                    if btn.clicked(ev): _go("menu")

        elif state == "settings":
            if not _music_on:
                audio.start_music(); _music_on = True
            cfg = load_cfg()
            btns = draw_settings(display, cfg)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    _go("menu")
                for btn in btns["back"]:
                    if btn.clicked(ev): _go("menu")
                for btn in btns["toggle_fs"]:
                    if btn.clicked(ev): _toggle_fullscreen()
                for btn, idx in btns["colors"]:
                    if btn.clicked(ev):
                        cfg["player_color"] = idx; save_cfg(cfg)
                for sl in btns["sliders"]:
                    if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                        if sl["rect"].collidepoint(ev.pos):
                            raw = (ev.pos[0] - sl["track_x"]) / sl["track_w"]
                            cfg[sl["key"]] = max(0.0, min(1.0, round(raw, 2)))
                            save_cfg(cfg); _apply_volume()
                    if ev.type == pygame.MOUSEMOTION and ev.buttons[0]:
                        if sl["rect"].collidepoint(ev.pos):
                            raw = (ev.pos[0] - sl["track_x"]) / sl["track_w"]
                            cfg[sl["key"]] = max(0.0, min(1.0, round(raw, 2)))
                            save_cfg(cfg); _apply_volume()
                from trails import set_active
                for btn, trail_id, locked in btns["trails"]:
                    if not locked and btn.clicked(ev):
                        set_active(trail_id)
    else:
        # during transition: keep drawing current state behind the fade
        if state == "menu":
            animator.update()
            display.fill(C.BG)
            animator.draw(display)
            draw_main_menu(display)
        elif state == "gameover":
            draw_game_over(display, last_score, current_mode, last_stats)
        elif state == "leaderboard":
            draw_leaderboard(display, lb_tab)
        elif state == "settings":
            draw_settings(display, load_cfg())

    trans.update()
    trans.draw(display)
    pygame.display.update()
    clock.tick(FPS)
