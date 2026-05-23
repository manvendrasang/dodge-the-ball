# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, unused-import, unused-argument, no-name-in-module, multiple-statements

import sys
import pygame
from constants import WIDTH, HEIGHT, FPS, BG, init_fonts, MODES
from ui import draw_main_menu, draw_game_over, draw_leaderboard
from modes import run_session

pygame.init()
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge The Ball!")
clock = pygame.time.Clock()
init_fonts()

state        = "menu"
current_mode = "classic"
last_score   = 0
lb_tab       = 0

while True:
    ev_list = []
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        ev_list.append(e)

    if state == "menu":
        menu_buttons = draw_main_menu(display)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
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
                        state = "game"

    elif state == "game":
        # run_session blocks until the death animation fully finishes
        last_score = run_session(current_mode, display, clock)
        state = "gameover"
        # flush all events queued during gameplay so they don't fire on game over screen
        pygame.event.clear()

    elif state == "gameover":
        over_buttons = draw_game_over(display, last_score, current_mode)
        for ev in ev_list:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r: state = "game"
                if ev.key == pygame.K_m: state = "menu"
                if ev.key == pygame.K_q: pygame.quit(); sys.exit()
            for btn in over_buttons:
                if btn.clicked(ev):
                    lbl = btn.label.lower()
                    if "restart" in lbl: state = "game"
                    elif "menu"   in lbl: state = "menu"
                    elif "quit"   in lbl: pygame.quit(); sys.exit()

    elif state == "leaderboard":
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
