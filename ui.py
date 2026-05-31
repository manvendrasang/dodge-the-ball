# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import, line-too-long
# pylint: disable=missing-class-docstring, no-member, no-name-in-module, multiple-statements, unused-variable, unused-import

import pygame
import constants as C
from constants import *
from scores import get_scores, get_personal_best
from audio import get_audio

def _combo_hud_color(combo):
    if combo <= 1:  return (200, 200, 255)
    if combo == 2:  return (80,  220, 255)
    if combo == 3:  return (80,  255, 160)
    if combo == 4:  return (255, 220, 40)
    if combo == 5:  return (255, 140, 40)
    return (255, 60, 60)  # 6+ (shrink/hardcore only)

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
        Button((cx, y0+(bh+gap)*4+10,bw,bh),"Settings",   (25,40,60),   (40,100,160),  WHITE),
        Button((cx, y0+(bh+gap)*5+10,bw,bh),"Quit",       BTN_QUIT,     BTN_QUIT_H,    RED),
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
        active = i == active_tab_idx
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


def draw_hud(surface, score, mode, active_pus, lives=None, shield=False, combo=0, combo_timer=0, level=1):
    sc_txt = C.FONT_HUD.render(f"SCORE  {score}", True, WHITE)
    surface.blit(sc_txt, (14, 12))
    pb = get_personal_best(mode)
    pb_txt = C.FONT_SMALL.render(f"BEST  {pb}", True, YELLOW)
    surface.blit(pb_txt, (14, 42))
    lv_col = LEVEL_COLORS[(level - 1) % len(LEVEL_COLORS)]
    # brighten the tint color so it's visible as text
    lv_text_col = tuple(min(255, v * 8 + 120) for v in lv_col)
    lv_txt = C.FONT_SMALL.render(f"LVL  {level}", True, lv_text_col)
    surface.blit(lv_txt, (14, 64))
    mode_col = {"classic": CYAN, "shrink": PURPLE, "hardcore": RED}.get(mode, WHITE)
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
    # combo indicator - top right below mode label
    if combo > 1:
        import math
        frac      = combo_timer / COMBO_TIMEOUT if COMBO_TIMEOUT > 0 else 0
        col       = _combo_hud_color(combo)
        combo_txt = C.FONT_HUD.render(f"{combo}x COMBO", True, col)
        cx        = C.WIDTH - combo_txt.get_width() - 14
        cy        = 62
        surface.blit(combo_txt, (cx, cy))
        # thin timeout bar beneath the text
        bar_w = combo_txt.get_width()
        bar_h = 3
        pygame.draw.rect(surface, (40, 40, 60), (cx, cy + combo_txt.get_height() + 2, bar_w, bar_h))
        pygame.draw.rect(surface, col,          (cx, cy + combo_txt.get_height() + 2, int(bar_w * frac), bar_h))
    px = 14
    for kind, frames_left in active_pus.items():
        secs = max(0, frames_left // FPS)
        lbl  = C.FONT_SMALL.render(f"{PU_LABEL[kind]}  {secs}s", True, PU_COLOR[kind])
        surface.blit(lbl, (px, C.HEIGHT - 30))
        px += lbl.get_width() + 24


def draw_pause(surface) -> list:
    """Semi-transparent pause overlay. Returns list of Buttons."""
    from trails import TRAIL_DEFS, get_unlocked, get_active
    overlay = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    # left panel: standard pause buttons
    pw, ph = 380, 360
    px_ = C.WIDTH//2 - pw - 20
    py_ = C.HEIGHT//2 - ph//2
    _panel(surface, pygame.Rect(px_, py_, pw, ph), 230)
    t = C.FONT_BIG.render("PAUSED", True, CYAN)
    surface.blit(t, (px_ + pw//2 - t.get_width()//2, py_ + 22))
    hint = C.FONT_SMALL.render("ESC / P  to resume", True, DIM)
    surface.blit(hint, (px_ + pw//2 - hint.get_width()//2, py_ + 82))
    bw, bh, gap = 280, 48, 10
    cx  = px_ + pw//2 - bw//2
    y0  = py_ + 130
    buttons = [
        Button((cx, y0,            bw, bh), "Resume",  (20,80,30),  GREEN,        WHITE),
        Button((cx, y0+bh+gap,     bw, bh), "Restart", (20,60,120), BLUE,         WHITE),
        Button((cx, y0+(bh+gap)*2, bw, bh), "Menu",    (30,34,70),  BTN_LEADER_H, CYAN),
        Button((cx, y0+(bh+gap)*3, bw, bh), "Quit",    BTN_QUIT,    BTN_QUIT_H,   RED),
    ]
    for b in buttons:
        b.draw(surface)
    # right panel: trail selector
    tp_w, tp_h = 320, ph
    tp_x = C.WIDTH//2 + 20
    tp_y = py_
    _panel(surface, pygame.Rect(tp_x, tp_y, tp_w, tp_h), 230)
    tl = C.FONT_HUD.render("TRAIL STYLE", True, CYAN)
    surface.blit(tl, (tp_x + tp_w//2 - tl.get_width()//2, tp_y + 18))
    unlocked = set(get_unlocked())
    active   = get_active()
    trail_btns = []
    ty = tp_y + 58
    tbw, tbh = 260, 38
    tbx = tp_x + tp_w//2 - tbw//2
    for td in TRAIL_DEFS:
        locked = td["id"] not in unlocked
        if locked:
            col  = (30, 30, 45)
            hcol = (30, 30, 45)
            lbl  = f"{td['name']}  (unlock @ {td['unlock']})"
            tcol = DIM
        else:
            is_active = td["id"] == active
            col  = (20, 80, 30) if is_active else (28, 30, 55)
            hcol = GREEN if is_active else (60, 80, 160)
            lbl  = td["name"] + (" ✓" if is_active else "")
            tcol = WHITE
        b = Button((tbx, ty, tbw, tbh), lbl, col, hcol, tcol)
        if not locked:
            b.draw(surface)
        else:
            # draw locked state without hover effect
            pygame.draw.rect(surface, col, pygame.Rect(tbx, ty, tbw, tbh), border_radius=6)
            pygame.draw.rect(surface, (35, 35, 55), pygame.Rect(tbx, ty, tbw, tbh), 1, border_radius=6)
            lock_lbl = C.FONT_SMALL.render(lbl, True, DIM)
            surface.blit(lock_lbl, (tbx + tbw//2 - lock_lbl.get_width()//2,
                                    ty + tbh//2 - lock_lbl.get_height()//2))
        trail_btns.append((b, td["id"], locked))
        ty += tbh + 8
    return buttons, trail_btns


def draw_settings(surface, cfg: dict) -> dict:
    """
    Draw the settings screen.
    Returns dict of named button lists for the caller to handle:
      { "back": [...], "toggle_fs": [...], "colors": [...], "vol_sfx": [...], "vol_music": [...], "trails": [...] }
    """
    from settings import PLAYER_COLORS
    from trails import TRAIL_DEFS, get_unlocked, get_active
    surface.fill(C.BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (18, 20, 34), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (18, 20, 34), (0, y), (0+C.WIDTH, y))

    title = C.FONT_BIG.render("SETTINGS", True, CYAN)
    surface.blit(title, (C.WIDTH//2 - title.get_width()//2, 28))

    result = {"back": [], "toggle_fs": [], "colors": [], "trails": [],
              "vol_sfx_up": [], "vol_sfx_dn": [], "vol_music_up": [], "vol_music_dn": []}

    col_x  = C.WIDTH//2 - 540
    trail_x = C.WIDTH//2 + 60
    mid_x  = C.WIDTH//2 - 200
    sec_y  = 100

    # FULLSCREEN toggle
    _panel(surface, pygame.Rect(mid_x, sec_y, 400, 68))
    fs_lbl = C.FONT_HUD.render("FULLSCREEN", True, WHITE)
    surface.blit(fs_lbl, (mid_x + 20, sec_y + 10))
    fs_state = "ON" if cfg.get("fullscreen", True) else "OFF"
    fs_col   = GREEN if cfg.get("fullscreen") else RED
    fs_btn   = Button((mid_x + 260, sec_y + 10, 110, 40), fs_state, fs_col,
                      tuple(min(255, v+60) for v in fs_col))
    fs_btn.draw(surface)
    result["toggle_fs"].append(fs_btn)

    # PLAYER COLOR picker
    sec_y2 = sec_y + 100
    _panel(surface, pygame.Rect(col_x, sec_y2, 480, 180))
    lbl = C.FONT_HUD.render("PLAYER COLOR", True, WHITE)
    surface.blit(lbl, (col_x + 20, sec_y2 + 12))
    active_idx = cfg.get("player_color", 0)
    swatch_x = col_x + 20
    swatch_y = sec_y2 + 48
    for i, pc in enumerate(PLAYER_COLORS):
        col   = pc["color"]
        sw    = 42
        gap   = 14
        bx    = swatch_x + i * (sw + gap)
        by    = swatch_y
        # two rows of 4
        if i >= 4:
            bx = swatch_x + (i-4) * (sw + gap)
            by = swatch_y + sw + 10
        selected = i == active_idx
        # glow for selected
        if selected:
            gs = pygame.Surface((sw+12, sw+12), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*col, 80), (0, 0, sw+12, sw+12), border_radius=8)
            surface.blit(gs, (bx-6, by-6))
        pygame.draw.rect(surface, col,   (bx, by, sw, sw), border_radius=6)
        pygame.draw.rect(surface, WHITE if selected else DIM, (bx, by, sw, sw), 2, border_radius=6)
        b = Button((bx, by, sw, sw), "", col, tuple(min(255,v+60) for v in col))
        result["colors"].append((b, i))

    # draw all color swatches as clickable (no text)
    name_txt = C.FONT_SMALL.render(PLAYER_COLORS[active_idx]["name"], True, YELLOW)
    surface.blit(name_txt, (col_x + 20, sec_y2 + 148))

    # VOLUME controls
    sec_y3 = sec_y2 + 200
    _panel(surface, pygame.Rect(col_x, sec_y3, 480, 130))
    vol_lbl = C.FONT_HUD.render("VOLUME", True, WHITE)
    surface.blit(vol_lbl, (col_x + 20, sec_y3 + 10))
    # SFX row
    sfx_v = cfg.get("sfx_volume", 0.7)
    sfx_txt = C.FONT_SMALL.render(f"SFX   {int(sfx_v*100):>3}%", True, WHITE)
    surface.blit(sfx_txt, (col_x + 20, sec_y3 + 48))
    dn1 = Button((col_x + 240, sec_y3 + 44, 36, 30), "◀", (30,30,60), BLUE)
    up1 = Button((col_x + 284, sec_y3 + 44, 36, 30), "▶", (30,30,60), BLUE)
    dn1.draw(surface); up1.draw(surface)
    result["vol_sfx_dn"].append(dn1); result["vol_sfx_up"].append(up1)
    # music row
    mu_v = cfg.get("music_volume", 0.45)
    mu_txt = C.FONT_SMALL.render(f"MUSIC {int(mu_v*100):>3}%", True, WHITE)
    surface.blit(mu_txt, (col_x + 20, sec_y3 + 86))
    dn2 = Button((col_x + 240, sec_y3 + 82, 36, 30), "◀", (30,30,60), BLUE)
    up2 = Button((col_x + 284, sec_y3 + 82, 36, 30), "▶", (30,30,60), BLUE)
    dn2.draw(surface); up2.draw(surface)
    result["vol_music_dn"].append(dn2); result["vol_music_up"].append(up2)

    # TRAIL STYLE picker
    _panel(surface, pygame.Rect(trail_x, sec_y2, 340, 310))
    trl = C.FONT_HUD.render("TRAIL STYLE", True, WHITE)
    surface.blit(trl, (trail_x + 20, sec_y2 + 12))
    unlocked = set(get_unlocked())
    active_trail = get_active()
    ty = sec_y2 + 50
    for td in TRAIL_DEFS:
        locked = td["id"] not in unlocked
        is_act = td["id"] == active_trail
        if locked:
            bg   = (22, 22, 38); hov = (22, 22, 38); tc = DIM
            txt  = f"{td['name']}  @ {td['unlock']}"
        else:
            bg   = (20,80,30) if is_act else (28,30,55)
            hov  = GREEN if is_act else (60,80,160)
            tc   = WHITE
            txt  = td["name"] + (" ✓" if is_act else "")
        b = Button((trail_x+20, ty, 300, 38), txt, bg, hov, tc)
        if not locked:
            b.draw(surface)
        else:
            pygame.draw.rect(surface, bg, (trail_x+20, ty, 300, 38), border_radius=6)
            pygame.draw.rect(surface, (35,35,55), (trail_x+20, ty, 300, 38), 1, border_radius=6)
            ll = C.FONT_SMALL.render(txt, True, DIM)
            surface.blit(ll, (trail_x+20+150-ll.get_width()//2, ty+10))
        result["trails"].append((b, td["id"], locked))
        ty += 46

    # BACK button
    bk = Button((C.WIDTH//2 - 120, C.HEIGHT - 68, 240, 48), "Back to Menu", (30,34,70), BTN_LEADER_H, CYAN)
    bk.draw(surface)
    result["back"].append(bk)

    # player preview dot
    preview_col = PLAYER_COLORS[active_idx]["color"]
    px_ = mid_x + 360
    py_ = sec_y + 14
    gs2 = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(gs2, (*preview_col, 50), (20,20), 20)
    surface.blit(gs2, (px_-20, py_-20))
    pygame.draw.circle(surface, preview_col, (px_, py_+20), 12)
    pygame.draw.circle(surface, WHITE,       (px_, py_+20), 12, 2)

    return result
