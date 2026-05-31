# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import, line-too-long
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

state        = "menu"
current_mode = "classic"
last_score   = 0
lb_tab       = 0
animator     = MenuAnimator()
audio        = get_audio()
_music_on    = False

def _apply_volume():
    audio.set_volume(cfg.get("sfx_volume", 0.7))
    audio.set_music_volume(cfg.get("music_volume", 0.45))

_apply_volume()

def _toggle_fullscreen():
    global display
    cfg["fullscreen"] = not cfg.get("fullscreen", True)
    save_cfg(cfg)
    flags = pygame.FULLSCREEN if cfg["fullscreen"] else 0
    display = pygame.display.set_mode((SW, SH), flags)

VOL_STEP = 0.05

while True:
    ev_list = []
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        ev_list.append(e)

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
                        lb_tab = 0; state = "leaderboard"
                    elif lbl == "settings":
                        state = "settings"
                    elif lbl in ("classic", "shrink zone", "hardcore"):
                        current_mode = lbl.replace(" zone", "")
                        audio.stop_music(); _music_on = False
                        state = "game"

    elif state == "game":
        last_score = run_session(current_mode, display, clock)
        pygame.event.clear()
        state = "menu" if last_score == -1 else "gameover"

    elif state == "gameover":
        if not _music_on:
            audio.start_music(); _music_on = True
        over_buttons = draw_game_over(display, last_score, current_mode)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    audio.stop_music(); _music_on = False; state = "game"
                if ev.key in (pygame.K_m, pygame.K_ESCAPE): state = "menu"
            for btn in over_buttons:
                if btn.clicked(ev):
                    lbl = btn.label.lower()
                    if "restart" in lbl:
                        audio.stop_music(); _music_on = False; state = "game"
                    elif "menu" in lbl: state = "menu"
                    elif "quit" in lbl: pygame.quit(); sys.exit()

    elif state == "leaderboard":
        if not _music_on:
            audio.start_music(); _music_on = True
        lb_buttons, lb_tabs = draw_leaderboard(display, lb_tab)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                state = "menu"
            for i, tb in enumerate(lb_tabs):
                if tb.clicked(ev): lb_tab = i
            for btn in lb_buttons:
                if btn.clicked(ev): state = "menu"

    elif state == "settings":
        if not _music_on:
            audio.start_music(); _music_on = True
        cfg = load_cfg()  # reload so changes reflect immediately
        btns = draw_settings(display, cfg)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                state = "menu"
            # back
            for btn in btns["back"]:
                if btn.clicked(ev): state = "menu"
            # fullscreen toggle
            for btn in btns["toggle_fs"]:
                if btn.clicked(ev): _toggle_fullscreen()
            # player color swatches
            for btn, idx in btns["colors"]:
                if btn.clicked(ev):
                    cfg["player_color"] = idx
                    save_cfg(cfg)
            # volume up/down
            for btn in btns["vol_sfx_up"]:
                if btn.clicked(ev):
                    cfg["sfx_volume"] = min(1.0, round(cfg.get("sfx_volume",0.7) + VOL_STEP, 2))
                    save_cfg(cfg); _apply_volume()
            for btn in btns["vol_sfx_dn"]:
                if btn.clicked(ev):
                    cfg["sfx_volume"] = max(0.0, round(cfg.get("sfx_volume",0.7) - VOL_STEP, 2))
                    save_cfg(cfg); _apply_volume()
            for btn in btns["vol_music_up"]:
                if btn.clicked(ev):
                    cfg["music_volume"] = min(1.0, round(cfg.get("music_volume",0.45) + VOL_STEP, 2))
                    save_cfg(cfg); _apply_volume()
            for btn in btns["vol_music_dn"]:
                if btn.clicked(ev):
                    cfg["music_volume"] = max(0.0, round(cfg.get("music_volume",0.45) - VOL_STEP, 2))
                    save_cfg(cfg); _apply_volume()
            # trail selection
            from trails import set_active, get_color_fn
            for btn, trail_id, locked in btns["trails"]:
                if not locked and btn.clicked(ev):
                    set_active(trail_id)

    pygame.display.update()
    clock.tick(FPS)
