# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, no-name-in-module

import pygame
import constants as C
from constants import *
from scores import get_scores, get_personal_best

# button helper
class Button:
    def __init__(self, rect, label, color=BLUE, hover_color=CYAN):
        self.rect        = pygame.Rect(rect)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color

    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        col    = self.hover_color if self.rect.collidepoint(mx, my) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        lbl = C.FONT_HUD.render(self.label, True, DARK)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


def draw_main_menu(surface) -> str | None:
    """Returns 'classic','shrink','hardcore', or None."""
    surface.fill(BG)
    title = C.FONT_TITLE.render("DODGE THE BALL", True, CYAN)
    surface.blit(title, (WIDTH//2 - title.get_width()//2, 80))
    sub = C.FONT_HUD.render("Select a game mode", True, WHITE)
    surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 195))
    bw, bh = 280, 55
    cx = WIDTH // 2 - bw // 2
    buttons = [
        Button((cx, 260, bw, bh), "Classic",       BLUE,   CYAN),
        Button((cx, 335, bw, bh), "Shrink Zone",   PURPLE, PINK),
        Button((cx, 410, bw, bh), "Hardcore",       RED,    ORANGE),
        Button((cx, 500, bw, bh), "Leaderboard",   DARK,   (60,60,80)),
        Button((cx, 570, bw, bh), "Quit",          DARK,   (80,30,30)),
    ]
    for b in buttons:
        b.draw(surface)
    pb_y = 235
    for mode in MODES:
        pb = get_personal_best(mode)
        if pb:
            txt = C.FONT_SMALL.render(f"{mode.capitalize()} best: {pb}", True, YELLOW)
            surface.blit(txt, (WIDTH - txt.get_width() - 20, pb_y))
            pb_y += 28
    return buttons


def draw_game_over(surface, score, mode) -> str | None:
    """Returns 'restart','menu', or None."""
    surface.fill(BG)
    t = C.FONT_TITLE.render("GAME OVER", True, RED)
    surface.blit(t, (WIDTH//2 - t.get_width()//2, 120))
    s = C.FONT_BIG.render(f"Score: {score}", True, WHITE)
    surface.blit(s, (WIDTH//2 - s.get_width()//2, 240))
    pb = get_personal_best(mode)
    if score >= pb:
        hi = C.FONT_HUD.render("NEW PERSONAL BEST!", True, YELLOW)
        surface.blit(hi, (WIDTH//2 - hi.get_width()//2, 310))
    bw, bh = 240, 52
    cx = WIDTH//2 - bw//2
    buttons = [
        Button((cx, 390, bw, bh), "[R] Restart", GREEN,  CYAN),
        Button((cx, 460, bw, bh), "[M] Menu",    BLUE,   CYAN),
        Button((cx, 530, bw, bh), "[Q] Quit",    DARK,   (80,30,30)),
    ]
    for b in buttons:
        b.draw(surface)
    return buttons


def draw_leaderboard(surface, active_tab_idx: int) -> tuple:
    """Returns (buttons_list, tab_buttons_list)."""
    surface.fill(BG)
    t = C.FONT_BIG.render("LEADERBOARD", True, CYAN)
    surface.blit(t, (WIDTH//2 - t.get_width()//2, 30))
    tab_labels = ["Classic", "Shrink Zone", "Hardcore"]
    tab_colors = [BLUE, PURPLE, RED]
    tab_w, tab_h = 200, 44
    tab_start = WIDTH//2 - (len(tab_labels) * tab_w + (len(tab_labels)-1)*10)//2
    tab_buttons = []
    for i, (lbl, col) in enumerate(zip(tab_labels, tab_colors)):
        tx = tab_start + i * (tab_w + 10)
        b = Button((tx, 90, tab_w, tab_h), lbl, col if i != active_tab_idx else WHITE,
                   (col[0]//2+127, col[1]//2+127, col[2]//2+127))
        b.draw(surface)
        tab_buttons.append(b)
    mode = MODES[active_tab_idx]
    entries = get_scores(mode)
    y = 160
    for rank, sc in enumerate(entries, 1):
        color = YELLOW if rank == 1 else (WHITE if rank <= 3 else (160,160,160))
        row = C.FONT_HUD.render(f"#{rank:>2}   {sc}", True, color)
        surface.blit(row, (WIDTH//2 - 80, y))
        y += 38
    if not entries:
        empty = C.FONT_HUD.render("No scores yet!", True, (100,100,120))
        surface.blit(empty, (WIDTH//2 - empty.get_width()//2, 260))
    bk = Button((WIDTH//2 - 110, HEIGHT - 70, 220, 48), "Back to Menu", DARK, (60,60,80))
    bk.draw(surface)
    return [bk], tab_buttons


def draw_hud(surface, score, mode, active_pus: dict, lives=None, shield=False):
    sc_txt = C.FONT_HUD.render(f"Score: {score}", True, WHITE)
    surface.blit(sc_txt, (14, 12))
    pb = get_personal_best(mode)
    pb_txt = C.FONT_SMALL.render(f"Best: {pb}", True, YELLOW)
    surface.blit(pb_txt, (14, 44))
    mode_txt = C.FONT_SMALL.render(mode.upper(), True, (100, 100, 140))
    surface.blit(mode_txt, (WIDTH - mode_txt.get_width() - 14, 12))
    if lives is not None:
        lv_txt = C.FONT_HUD.render(f"Lives: {'♥' * lives}", True, RED)
        surface.blit(lv_txt, (WIDTH - lv_txt.get_width() - 14, 40))
    if shield:
        sh = C.FONT_SMALL.render("SHIELD ACTIVE", True, GREEN)
        surface.blit(sh, (WIDTH//2 - sh.get_width()//2, 12))
    # active powerup timers
    px = 14
    for kind, frames_left in active_pus.items():
        secs = max(0, frames_left // FPS)
        lbl  = C.FONT_SMALL.render(f"{PU_LABEL[kind]} {secs}s", True, PU_COLOR[kind])
        surface.blit(lbl, (px, HEIGHT - 32))
        px += lbl.get_width() + 20
