# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import
# pylint: disable=missing-class-docstring, no-member, no-name-in-module, multiple-statements, unused-variable

import pygame
import constants as C
from constants import *
from scores import get_scores, get_personal_best
from audio import get_audio

class Button:
    def __init__(self, rect, label, color, hover_color, text_color=None):
        self.rect        = pygame.Rect(rect)
        self.label       = label
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color or WHITE

    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        col = self.hover_color if hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=6)
        border_col = self.hover_color if not hovered else WHITE
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=6)
        lbl = C.FONT_HUD.render(self.label, True, self.text_color)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))

    def clicked(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos)):
            get_audio().play("click")
            return True
        return False


def _panel(surface, rect, alpha=180):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.fill((20, 22, 40, alpha))
    surface.blit(s, rect.topleft)
    pygame.draw.rect(surface, DIM, rect, 1, border_radius=8)


def draw_main_menu(surface):
    # background + grid drawn by MenuAnimator in main.py before this call
    # title
    title = C.FONT_TITLE.render("DODGE THE BALL", True, CYAN)
    # glow behind title
    glow = C.FONT_TITLE.render("DODGE THE BALL", True, (0, 80, 100))
    for off in [(-2,2),(2,2),(-2,-2),(2,-2)]:
        surface.blit(glow, (C.WIDTH//2 - title.get_width()//2 + off[0], 72 + off[1]))
    surface.blit(title, (C.WIDTH//2 - title.get_width()//2, 72))
    sub = C.FONT_HUD.render("SELECT GAME MODE", True, DIM)
    surface.blit(sub, (C.WIDTH//2 - sub.get_width()//2, 178))
    bw, bh, gap = 300, 52, 14
    cx = C.WIDTH//2 - bw//2
    y0 = 220
    buttons = [
        Button((cx, y0,           bw, bh), "Classic",     (20,60,120),  (40,130,255),  WHITE),
        Button((cx, y0+bh+gap,    bw, bh), "Shrink Zone", (60,20,100),  (160,40,255),  WHITE),
        Button((cx, y0+(bh+gap)*2,bw, bh), "Hardcore",    (100,20,20),  (255,40,40),   WHITE),
        Button((cx, y0+(bh+gap)*3+10,bw,bh),"Leaderboard",(30,34,70),   BTN_LEADER_H,  CYAN),
        Button((cx, y0+(bh+gap)*4+10,bw,bh),"Quit",       BTN_QUIT,     BTN_QUIT_H,    RED),
    ]
    for b in buttons:
        b.draw(surface)
    # personal bests panel
    pb_x = C.WIDTH - 230
    _panel(surface, pygame.Rect(pb_x - 10, 218, 220, 100))
    pb_title = C.FONT_SMALL.render("PERSONAL BESTS", True, DIM)
    surface.blit(pb_title, (pb_x, 224))
    for i, mode in enumerate(MODES):
        pb = get_personal_best(mode)
        col = YELLOW if pb else DIM
        txt = C.FONT_SMALL.render(f"{mode.upper():<10} {pb}", True, col)
        surface.blit(txt, (pb_x, 244 + i*24))
    return buttons


def draw_game_over(surface, score, mode):
    surface.fill(BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (20, 22, 36), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (20, 22, 36), (0, y), (C.WIDTH, y))
    # panel
    pw, ph = 500, 360
    _panel(surface, pygame.Rect(C.WIDTH//2 - pw//2, 100, pw, ph), 210)
    t = C.FONT_TITLE.render("GAME OVER", True, RED)
    glow = C.FONT_TITLE.render("GAME OVER", True, (80, 10, 10))
    for off in [(-2,2),(2,2),(-2,-2),(2,-2)]:
        surface.blit(glow, (C.WIDTH//2 - t.get_width()//2 + off[0], 118 + off[1]))
    surface.blit(t, (C.WIDTH//2 - t.get_width()//2, 118))
    s = C.FONT_BIG.render(f"Score: {score}", True, WHITE)
    surface.blit(s, (C.WIDTH//2 - s.get_width()//2, 232))
    pb = get_personal_best(mode)
    if score >= pb and score > 0:
        hi = C.FONT_HUD.render("★  NEW PERSONAL BEST  ★", True, YELLOW)
        surface.blit(hi, (C.WIDTH//2 - hi.get_width()//2, 295))
    bw, bh, gap = 260, 50, 12
    cx = C.WIDTH//2 - bw//2
    buttons = [
        Button((cx, 370, bw, bh), "[R]  Restart", (20,80,30),  GREEN,  WHITE),
        Button((cx, 370+bh+gap, bw, bh), "[M]  Menu",    (20,50,100), BLUE,   WHITE),
        Button((cx, 370+(bh+gap)*2, bw, bh), "[Q]  Quit",    BTN_QUIT,    BTN_QUIT_H, RED),
    ]
    for b in buttons:
        b.draw(surface)
    return buttons


def draw_leaderboard(surface, active_tab_idx):
    surface.fill(BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (20, 22, 36), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (20, 22, 36), (0, y), (C.WIDTH, y))
    t = C.FONT_BIG.render("LEADERBOARD", True, CYAN)
    surface.blit(t, (C.WIDTH//2 - t.get_width()//2, 24))
    tab_labels = ["Classic", "Shrink Zone", "Hardcore"]
    tab_fg     = [CYAN, PURPLE, RED]
    tab_bg     = [(20,60,120), (50,20,90), (90,20,20)]
    tab_w, tab_h = 210, 44
    tab_start = C.WIDTH//2 - (len(tab_labels)*(tab_w+10)-10)//2
    tab_buttons = []
    for i, (lbl, fg, bg) in enumerate(zip(tab_labels, tab_fg, tab_bg)):
        tx = tab_start + i*(tab_w+10)
        active = (i == active_tab_idx)
        b = Button((tx, 86, tab_w, tab_h), lbl,
                   fg if active else bg,
                   fg,
                   DARK if active else WHITE)
        b.draw(surface)
        tab_buttons.append(b)
    mode    = MODES[active_tab_idx]
    entries = get_scores(mode)
    # entries are now (score, timestamp) tuples or plain ints for backward compat
    _panel(surface, pygame.Rect(C.WIDTH//2 - 320, 148, 640, C.HEIGHT - 220))
    y = 164
    for rank, entry in enumerate(entries, 1):
        if isinstance(entry, (list, tuple)):
            sc, ts = entry[0], entry[1]
        else:
            sc, ts = entry, ""
        if rank == 1:   col = YELLOW
        elif rank <= 3: col = (200, 200, 255)
        else:           col = DIM
        medals = {1:"🥇", 2:"🥈", 3:"🥉"}
        medal = medals.get(rank, "") if rank <= 3 else ""
        rank_txt = C.FONT_HUD.render(f"#{rank:>2}", True, col)
        sc_txt   = C.FONT_HUD.render(str(sc), True, WHITE)
        ts_txt   = C.FONT_SMALL.render(ts, True, (80, 84, 110))
        surface.blit(rank_txt, (C.WIDTH//2 - 280, y))
        surface.blit(sc_txt,   (C.WIDTH//2 - 200, y))
        surface.blit(ts_txt,   (C.WIDTH//2 + 20,  y + 4))
        pygame.draw.line(surface, (28, 30, 50),
                         (C.WIDTH//2 - 300, y + 34), (C.WIDTH//2 + 300, y + 34))
        y += 38
    if not entries:
        empty = C.FONT_HUD.render("No scores recorded yet", True, DIM)
        surface.blit(empty, (C.WIDTH//2 - empty.get_width()//2, 280))
    bk = Button((C.WIDTH//2 - 120, C.HEIGHT - 62, 240, 46),
                "Back to Menu", (30,34,70), BTN_LEADER_H, CYAN)
    bk.draw(surface)
    return [bk], tab_buttons


def draw_hud(surface, score, mode, active_pus, lives=None, shield=False):
    sc_txt = C.FONT_HUD.render(f"SCORE  {score}", True, WHITE)
    surface.blit(sc_txt, (14, 12))
    pb = get_personal_best(mode)
    pb_txt = C.FONT_SMALL.render(f"BEST  {pb}", True, YELLOW)
    surface.blit(pb_txt, (14, 42))
    mode_col = {
        "classic": CYAN, "shrink": PURPLE, "hardcore": RED
    }.get(mode, WHITE)
    mode_txt = C.FONT_SMALL.render(mode.upper(), True, mode_col)
    surface.blit(mode_txt, (C.WIDTH - mode_txt.get_width() - 14, 12))
    if lives is not None:
        lv_txt = C.FONT_HUD.render(f"{'♥' * (lives+1)}", True, RED)
        surface.blit(lv_txt, (C.WIDTH - lv_txt.get_width() - 14, 38))
    if shield:
        sh = C.FONT_SMALL.render("◈  SHIELD ACTIVE", True, GREEN)
        surface.blit(sh, (C.WIDTH//2 - sh.get_width()//2, 12))
    if PU_GHOST in active_pus:
        gh = C.FONT_SMALL.render("◌  GHOST ACTIVE", True, (200, 200, 255))
        offset = 32 if shield else 12
        surface.blit(gh, (C.WIDTH//2 - gh.get_width()//2, offset))
    px = 14
    for kind, frames_left in active_pus.items():
        secs = max(0, frames_left // FPS)
        lbl  = C.FONT_SMALL.render(f"{PU_LABEL[kind]}  {secs}s", True, PU_COLOR[kind])
        surface.blit(lbl, (px, C.HEIGHT - 30))
        px += lbl.get_width() + 24


def draw_pause(surface) -> list:
    """Semi-transparent pause overlay. Returns list of Buttons."""
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    # panel
    pw, ph = 420, 340
    px_, py_ = C.WIDTH//2 - pw//2, C.HEIGHT//2 - ph//2
    _panel(surface, pygame.Rect(px_, py_, pw, ph), 230)
    t = C.FONT_BIG.render("PAUSED", True, CYAN)
    surface.blit(t, (C.WIDTH//2 - t.get_width()//2, py_ + 28))
    hint = C.FONT_SMALL.render("ESC / P  to resume", True, DIM)
    surface.blit(hint, (C.WIDTH//2 - hint.get_width()//2, py_ + 88))
    bw, bh, gap = 280, 48, 10
    cx = C.WIDTH//2 - bw//2
    y0 = py_ + 138
    buttons = [
        Button((cx, y0,             bw, bh), "Resume",   (20,80,30),  GREEN,      WHITE),
        Button((cx, y0+bh+gap,      bw, bh), "Restart",  (20,60,120), BLUE,       WHITE),
        Button((cx, y0+(bh+gap)*2,  bw, bh), "Menu",     (30,34,70),  BTN_LEADER_H, CYAN),
        Button((cx, y0+(bh+gap)*3,  bw, bh), "Quit",     BTN_QUIT,    BTN_QUIT_H, RED),
    ]
    for b in buttons:
        b.draw(surface)
    return buttons
