# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import, line-too-long, invalid-name
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument, no-name-in-module, multiple-statements, redefined-outer-name

import sys
import math
import pygame
import constants as C
from constants import init_fonts, set_resolution, MODES, FPS
from ui import draw_main_menu, draw_mode_select, draw_game_over, draw_leaderboard, draw_settings, draw_profile
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

_fade_surf = pygame.Surface((SW, SH))
_fade_surf.fill((0, 0, 0))

# achievement popup queue
_ach_popups = []   # list of {"ach": dict, "life": int, "max_life": int}
_ACH_POP_LIFE = 4 * FPS  # 4 seconds each

def _queue_ach_popups(new_ach: list):
    for ach in new_ach:
        _ach_popups.append({"ach": ach, "life": _ACH_POP_LIFE, "max_life": _ACH_POP_LIFE})

def _draw_ach_popups(surface):
    """Draw stacked achievement popups at top-center of screen."""
    if not _ach_popups:
        return
    pop_w, pop_h = 420, 56
    for i, pop in enumerate(_ach_popups[:3]):
        frac  = pop["life"] / pop["max_life"]
        # slide in from top
        slide = max(0.0, 1.0 - frac * 8)        # 0→1 means offscreen; snaps in fast
        alpha = int(255 * min(1.0, frac * 6))    # fades out in last ~0.17s
        py_   = int(-pop_h * slide) + 12 + i * (pop_h + 6)
        px_   = C.WIDTH // 2 - pop_w // 2
        # panel
        ps = pygame.Surface((pop_w, pop_h), pygame.SRCALPHA)
        ps.fill((30, 20, 50, int(220 * min(1.0, frac * 6))))
        pygame.draw.rect(ps, (*C.PURPLE, alpha), (0, 0, pop_w, pop_h), 2, border_radius=8)
        surface.blit(ps, (px_, py_))
        # ping dot
        ping_r = 6
        ping_a = int(255 * abs(math.sin(pygame.time.get_ticks() * 0.006)))
        pd = pygame.Surface((ping_r*2, ping_r*2), pygame.SRCALPHA)
        pygame.draw.circle(pd, (*C.YELLOW, ping_a), (ping_r, ping_r), ping_r)
        surface.blit(pd, (px_ + pop_w - ping_r*2 - 8, py_ + pop_h//2 - ping_r))
        # icon + text
        ach  = pop["ach"]
        ico  = C.FONT_HUD.render(ach["icon"], True, C.YELLOW)
        nm   = C.FONT_HUD.render(ach["name"], True, C.WHITE)
        tag  = C.FONT_SMALL.render("ACHIEVEMENT UNLOCKED", True, C.PURPLE)
        ico.set_alpha(alpha); nm.set_alpha(alpha); tag.set_alpha(alpha)
        surface.blit(ico, (px_ + 12, py_ + pop_h//2 - ico.get_height()//2))
        surface.blit(tag, (px_ + 50, py_ + 6))
        surface.blit(nm,  (px_ + 50, py_ + 24))

def _tick_ach_popups():
    for p in _ach_popups:
        p["life"] -= 1
    while _ach_popups and _ach_popups[0]["life"] <= 0:
        _ach_popups.pop(0)

class Transition:
    FRAMES = 18
    def __init__(self):
        self._alpha = 0; self._state = "idle"
        self._next_state = None; self._callback = None
    @property
    def busy(self): return self._state != "idle"
    def go(self, next_state, callback=None):
        if self._state != "idle": return
        self._next_state = next_state; self._callback = callback
        self._state = "out"; self._alpha = 0
    def update(self):
        if self._state == "out":
            self._alpha = min(255, self._alpha + 255 // self.FRAMES)
            if self._alpha >= 255:
                self._alpha = 255; self._state = "in"
                if self._callback: self._callback()
        elif self._state == "in":
            self._alpha = max(0, self._alpha - 255 // self.FRAMES)
            if self._alpha <= 0: self._alpha = 0; self._state = "idle"
    def draw(self, surface):
        if self._state == "idle": return
        _fade_surf.set_alpha(self._alpha); surface.blit(_fade_surf, (0, 0))

state        = "menu"
current_mode = "classic"
last_score   = 0
last_stats   = {}
lb_tab       = 0
profile_tab  = 0
animator     = MenuAnimator()
audio        = get_audio()
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
    _fade_surf = pygame.Surface((SW, SH)); _fade_surf.fill((0, 0, 0))

def _apply_state_change(next_state, pre_callback=None):
    global state
    if pre_callback: pre_callback()
    state = next_state
    if next_state == "game":
        audio.stop_music()
    else:
        audio.start_music()

def _go(next_state, pre_callback=None):
    trans.go(next_state, callback=lambda: _apply_state_change(next_state, pre_callback))

def _draw_menu_bg():
    animator.update(); display.fill(C.BG); animator.draw(display)

audio.start_music()

while True:
    ev_list = []
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        ev_list.append(e)

    if not trans.busy:

        if state == "menu":
            _draw_menu_bg()
            menu_buttons = draw_main_menu(display)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                for btn in menu_buttons:
                    if btn.clicked(ev):
                        lbl = btn.label.lower()
                        if   lbl == "quit":        pygame.quit(); sys.exit()
                        elif lbl == "leaderboard": _go("leaderboard")
                        elif lbl == "settings":    _go("settings")
                        elif lbl == "profile":     _go("profile")
                        elif lbl == "play":        _go("mode_select")

        elif state == "mode_select":
            _draw_menu_bg()
            mode_buttons, back_btn = draw_mode_select(display)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: _go("menu")
                if back_btn.clicked(ev): _go("menu")
                for btn in mode_buttons:
                    if btn.clicked(ev):
                        current_mode = btn.label.lower().replace(" zone", "")
                        _go("game")

        elif state == "game":
            last_score, last_stats = run_session(current_mode, display, clock)
            pygame.event.clear()
            new_ach = last_stats.get("new_achievements", [])
            if new_ach:
                _queue_ach_popups(new_ach)
            _go("menu" if last_score == -1 else "gameover")

        elif state == "gameover":
            over_buttons = draw_game_over(display, last_score, current_mode, last_stats)
            _tick_ach_popups()
            _draw_ach_popups(display)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:                    _go("game")
                    if ev.key in (pygame.K_m, pygame.K_ESCAPE): _go("menu")
                for btn in over_buttons:
                    if btn.clicked(ev):
                        lbl = btn.label.lower()
                        if "restart" in lbl:  _go("game")
                        elif "menu"   in lbl: _go("menu")
                        elif "quit"   in lbl: pygame.quit(); sys.exit()

        elif state == "leaderboard":
            lb_buttons, lb_tabs = draw_leaderboard(display, lb_tab)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: _go("menu")
                for i, tb in enumerate(lb_tabs):
                    if tb.clicked(ev): lb_tab = i
                for btn in lb_buttons:
                    if btn.clicked(ev): _go("menu")

        elif state == "profile":
            tab_btns, back_btn = draw_profile(display, profile_tab)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: _go("menu")
                if back_btn.clicked(ev): _go("menu")
                for i, tb in enumerate(tab_btns):
                    if tb.clicked(ev): profile_tab = i

        elif state == "settings":
            cfg = load_cfg()
            btns = draw_settings(display, cfg)
            for ev in ev_list:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE: _go("menu")
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
                    if not locked and btn.clicked(ev): set_active(trail_id)

    else:
        if state in ("menu", "mode_select"):
            _draw_menu_bg()
            if state == "menu":  draw_main_menu(display)
            else:                draw_mode_select(display)
        elif state == "gameover":    draw_game_over(display, last_score, current_mode, last_stats)
        elif state == "leaderboard": draw_leaderboard(display, lb_tab)
        elif state == "profile":     draw_profile(display, profile_tab)
        elif state == "settings":    draw_settings(display, load_cfg())

    # always tick and draw popups on top of everything
    _tick_ach_popups()
    _draw_ach_popups(display)

    trans.update()
    trans.draw(display)
    pygame.display.update()
    clock.tick(FPS)
