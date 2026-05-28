# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument, no-name-in-module, multiple-statements

import sys
import pygame
import constants as C
from constants import init_fonts, set_resolution, MODES, FPS
from ui import draw_main_menu, draw_game_over, draw_leaderboard
from modes import run_session
from menu_anim import MenuAnimator
from audio import get_audio

pygame.init()
info   = pygame.display.Info()
SW, SH = info.current_w, info.current_h
display = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
pygame.display.set_caption("Dodge The Ball!")
clock   = pygame.time.Clock()
set_resolution(SW, SH)
init_fonts()

state        = "menu"
current_mode = "classic"
last_score   = 0
lb_tab       = 0
animator     = MenuAnimator()
audio        = get_audio()  # kicks off background synthesis thread
_music_on    = False

while True:
    ev_list = []
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        ev_list.append(e)

    if state == "menu":
        if not _music_on:
            audio.start_music()
            _music_on = True
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
                    elif lbl in ("classic", "shrink zone", "hardcore"):
                        current_mode = lbl.replace(" zone", "")
                        audio.stop_music()
                        _music_on = False
                        state = "game"

    elif state == "game":
        last_score = run_session(current_mode, display, clock)
        pygame.event.clear()
        if last_score == -1:
            state = "menu"
        else:
            state = "gameover"

    elif state == "gameover":
        if not _music_on:
            audio.start_music()
            _music_on = True
        over_buttons = draw_game_over(display, last_score, current_mode)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    audio.stop_music(); _music_on = False; state = "game"
                if ev.key == pygame.K_m: state = "menu"
                if ev.key == pygame.K_ESCAPE: state = "menu"
            for btn in over_buttons:
                if btn.clicked(ev):
                    lbl = btn.label.lower()
                    if "restart" in lbl:
                        audio.stop_music(); _music_on = False; state = "game"
                    elif "menu"  in lbl: state = "menu"
                    elif "quit"  in lbl: pygame.quit(); sys.exit()

    elif state == "leaderboard":
        if not _music_on:
            audio.start_music()
            _music_on = True
        lb_buttons, lb_tabs = draw_leaderboard(display, lb_tab)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                state = "menu"
            for i, tb in enumerate(lb_tabs):
                if tb.clicked(ev): lb_tab = i
            for btn in lb_buttons:
                if btn.clicked(ev): state = "menu"

    pygame.display.update()
    clock.tick(FPS)
