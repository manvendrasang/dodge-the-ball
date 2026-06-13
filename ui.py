# pylint: disable=missing-module-docstring, missing-function-docstring, global-statement, unused-wildcard-import, line-too-long, superfluous-parens, import-outside-toplevel
# pylint: disable=missing-class-docstring, no-member, no-name-in-module, multiple-statements, unused-variable, unused-import, redefined-outer-name, wildcard-import
# pylint: disable=reimported

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
    # background + grid drawn by MenuAnimator before this call
    title = C.FONT_TITLE.render("DODGE THE BALL", True, CYAN)
    glow  = C.FONT_TITLE.render("DODGE THE BALL", True, (0, 80, 100))
    tx = C.WIDTH//2 - title.get_width()//2
    for off in [(-2,2),(2,2),(-2,-2),(2,-2)]:
        surface.blit(glow, (tx + off[0], 60 + off[1]))
    surface.blit(title, (tx, 60))
    bw, bh, gap = 300, 56, 14
    cx = C.WIDTH//2 - bw//2
    # vertically center button group in remaining space below title
    total_h = bh * 4 + gap * 3 + 20
    y0 = max(180, C.HEIGHT//2 - total_h//2 + 30)
    buttons = [
        Button((cx, y0,              bw, bh), "Play",        (20,90,40),  (40,210,90),  WHITE),
        Button((cx, y0+bh+gap,       bw, bh), "Profile",     (50,20,80),  (120,40,200), WHITE),
        Button((cx, y0+(bh+gap)*2,   bw, bh), "Leaderboard", (30,34,70),  BTN_LEADER_H, CYAN),
        Button((cx, y0+(bh+gap)*3,   bw, bh), "Settings",    (25,40,60),  (40,100,160), WHITE),
        Button((cx, y0+(bh+gap)*4+14,bw, bh), "Quit",        BTN_QUIT,    BTN_QUIT_H,   RED),
    ]
    for b in buttons: b.draw(surface)
    # personal bests — right side, vertically aligned with button group
    pb_w = 220
    pb_x = C.WIDTH - pb_w - 40
    pb_h = 30 + len(MODES) * 28
    _panel(surface, pygame.Rect(pb_x - 10, y0, pb_w + 20, pb_h + 16))
    pb_title = C.FONT_SMALL.render("PERSONAL BESTS", True, DIM)
    surface.blit(pb_title, (pb_x, y0 + 8))
    for i, mode in enumerate(MODES):
        pb  = get_personal_best(mode)
        col = YELLOW if pb else DIM
        txt = C.FONT_SMALL.render(f"{mode.upper():<10} {pb}", True, col)
        surface.blit(txt, (pb_x, y0 + 30 + i * 28))
    return buttons


def draw_mode_select(surface):
    title = C.FONT_TITLE.render("DODGE THE BALL", True, CYAN)
    glow  = C.FONT_TITLE.render("DODGE THE BALL", True, (0, 80, 100))
    tx = C.WIDTH//2 - title.get_width()//2
    for off in [(-2,2),(2,2),(-2,-2),(2,-2)]:
        surface.blit(glow, (tx + off[0], 60 + off[1]))
    surface.blit(title, (tx, 60))
    sub = C.FONT_HUD.render("SELECT GAME MODE", True, DIM)
    surface.blit(sub, (C.WIDTH//2 - sub.get_width()//2, 158))
    bw, bh, gap = 320, 62, 16
    cx = C.WIDTH//2 - bw//2
    total_h = bh * 3 + gap * 2
    y0 = max(200, C.HEIGHT//2 - total_h//2 + 10)
    descs = {
        "Classic":     "Dodge balls · collect squares",
        "Shrink Zone": "Zone shrinks over time · powerups",
        "Hardcore":    "Walls · homing balls · no mercy",
    }
    mode_data = [
        ("Classic",     (20,60,120),  (40,130,255)),
        ("Shrink Zone", (60,20,100),  (160,40,255)),
        ("Hardcore",    (100,20,20),  (255,40,40)),
    ]
    buttons = []
    for i, (lbl, bg, hov) in enumerate(mode_data):
        by = y0 + i * (bh + gap)
        b  = Button((cx, by, bw, bh), lbl, bg, hov, WHITE)
        b.draw(surface)
        buttons.append(b)
        # description panel right of button
        desc_x = cx + bw + 24
        desc_w = C.WIDTH - desc_x - 40
        _panel(surface, pygame.Rect(desc_x, by, desc_w, bh))
        d_lbl = C.FONT_SMALL.render(descs[lbl], True, (160, 162, 190))
        surface.blit(d_lbl, (desc_x + 16, by + bh//2 - d_lbl.get_height()//2))
    # back button centered below mode buttons
    back_y = y0 + total_h + 24
    back = Button((C.WIDTH//2 - 100, back_y, 200, 46), "← Back", (30,34,70), BTN_LEADER_H, CYAN)
    back.draw(surface)
    return buttons, back


def draw_game_over(surface, score, mode, stats=None):
    if stats is None:
        stats = {}
    surface.fill(BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (20, 22, 36), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (20, 22, 36), (0, y), (C.WIDTH, y))
    # title
    t = C.FONT_TITLE.render("GAME OVER", True, RED)
    glow = C.FONT_TITLE.render("GAME OVER", True, (80, 10, 10))
    for off in [(-2,2),(2,2),(-2,-2),(2,-2)]:
        surface.blit(glow, (C.WIDTH//2 - t.get_width()//2 + off[0], 60 + off[1]))
    surface.blit(t, (C.WIDTH//2 - t.get_width()//2, 60))
    sc = C.FONT_BIG.render(f"Score: {score}", True, WHITE)
    surface.blit(sc, (C.WIDTH//2 - sc.get_width()//2, 168))
    pb = get_personal_best(mode)
    if score >= pb and score > 0:
        hi = C.FONT_HUD.render("★  NEW PERSONAL BEST  ★", True, YELLOW)
        surface.blit(hi, (C.WIDTH//2 - hi.get_width()//2, 228))
    # stats panel
    if stats:
        t_s  = stats.get("time_s", 0)
        mins = t_s // 60; secs = t_s % 60
        mode_col = {"classic": CYAN, "shrink": PURPLE, "hardcore": RED}.get(mode, WHITE)
        # build mode-specific rows
        rows = [
            ("TIME SURVIVED",   f"{mins}:{secs:02d}",         WHITE),
            ("BALLS DODGED",    str(stats.get("balls_dodged", 0)), CYAN),
            ("LEVEL REACHED",   str(stats.get("level", 1)),    YELLOW),
            ("PEAK COMBO",      f"{stats.get('peak_combo',0)}x", _combo_hud_color(stats.get("peak_combo",0))),
        ]
        if mode == "shrink":
            rows.append(("ZONE SHRINKS",  str(stats.get("shrinks", 0)),  PURPLE))
        if mode == "shrink" or mode == "hardcore":
            rows.append(("POWERUPS",      str(stats.get("powerups", 0)), GREEN))
        if mode == "hardcore":
            rows.append(("WALLS SURVIVED", str(stats.get("walls", 0)),  ORANGE))
        # draw panel
        pw    = 520
        ph    = 30 + len(rows) * 38
        px_   = C.WIDTH//2 - pw//2
        py_   = 268
        _panel(surface, pygame.Rect(px_, py_, pw, ph), 200)
        mode_lbl = C.FONT_SMALL.render(mode.upper() + " STATS", True, mode_col)
        surface.blit(mode_lbl, (px_ + 18, py_ + 8))
        for i, (label, value, col) in enumerate(rows):
            ry = py_ + 32 + i * 38
            lbl_s = C.FONT_HUD.render(label, True, DIM)
            val_s = C.FONT_HUD.render(value, True, col)
            surface.blit(lbl_s, (px_ + 18, ry))
            surface.blit(val_s, (px_ + pw - val_s.get_width() - 18, ry))
            if i < len(rows) - 1:
                pygame.draw.line(surface, (35, 37, 60),
                                (px_+18, ry+32), (px_+pw-18, ry+32))
    # buttons — anchored to actual panel bottom
    if stats:
        panel_bottom = py_ + ph + 18
    else:
        panel_bottom = 340

    # newly unlocked achievements — compact single-line banner
    new_ach = stats.get("new_achievements", []) if stats else []
    if new_ach:
        ach_pw = 520
        ach_ph = 44
        ach_px = C.WIDTH//2 - ach_pw//2
        ach_py = panel_bottom
        _panel(surface, pygame.Rect(ach_px, ach_py, ach_pw, ach_ph), 220)
        # show up to 3 icons, then "+N more"
        icons_shown = new_ach[:3]
        icon_strs   = " ".join(a["icon"] for a in icons_shown)
        if len(new_ach) == 1:
            txt = f"{icon_strs}  ACHIEVEMENT UNLOCKED: {new_ach[0]['name']}"
        else:
            extra = len(new_ach) - len(icons_shown)
            suffix = f"  +{extra} more" if extra > 0 else ""
            txt = f"{icon_strs}  {len(new_ach)} ACHIEVEMENTS UNLOCKED{suffix}"
        lbl = C.FONT_HUD.render(txt, True, YELLOW)
        surface.blit(lbl, (C.WIDTH//2 - lbl.get_width()//2, ach_py + ach_ph//2 - lbl.get_height()//2))
        panel_bottom = ach_py + ach_ph + 14

    bw, bh, gap = 240, 46, 10
    cx  = C.WIDTH//2 - bw//2
    buttons = [
        Button((cx, panel_bottom,            bw, bh), "[R]  Restart", (20,80,30),  GREEN,      WHITE),
        Button((cx, panel_bottom+bh+gap,     bw, bh), "[M]  Menu",    (20,50,100), BLUE,       WHITE),
        Button((cx, panel_bottom+(bh+gap)*2, bw, bh), "[Q]  Quit",    BTN_QUIT,    BTN_QUIT_H, RED),
    ]
    for b in buttons:
        b.draw(surface)
    return buttons


def draw_leaderboard(surface, active_tab_idx, period="all"):
    """period: 'all' or 'today'. Returns (back_buttons, mode_tabs, period_tabs)."""
    from scores import get_daily_scores
    surface.fill(BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (20, 22, 36), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (20, 22, 36), (0, y), (C.WIDTH, y))
    t = C.FONT_BIG.render("LEADERBOARD", True, CYAN)
    surface.blit(t, (C.WIDTH//2 - t.get_width()//2, 18))

    # period toggle (All-Time / Today)
    per_w, per_h = 160, 38
    per_start = C.WIDTH//2 - per_w
    period_tabs = []
    for i, (lbl, key) in enumerate([("All-Time", "all"), ("Today", "today")]):
        px_ = per_start + i * per_w
        active = (period == key)
        b = Button((px_, 64, per_w, per_h), lbl,
                (50,50,80) if active else (26,28,46),
                (90,90,140), WHITE if active else DIM)
        b.draw(surface)
        period_tabs.append(b)

    tab_labels = ["Classic", "Shrink Zone", "Hardcore"]
    tab_fg     = [CYAN, PURPLE, RED]
    tab_bg     = [(20,60,120), (50,20,90), (90,20,20)]
    tab_w, tab_h = 210, 44
    tab_start = C.WIDTH//2 - (len(tab_labels)*(tab_w+10)-10)//2
    tab_buttons = []
    for i, (lbl, fg, bg) in enumerate(zip(tab_labels, tab_fg, tab_bg)):
        tx = tab_start + i*(tab_w+10)
        active = (i == active_tab_idx)
        b = Button((tx, 116, tab_w, tab_h), lbl,
                fg if active else bg,
                fg,
                DARK if active else WHITE)
        b.draw(surface)
        tab_buttons.append(b)
    mode = MODES[active_tab_idx]
    if period == "today":
        entries = get_daily_scores(mode)
    else:
        entries = get_scores(mode)
    _panel(surface, pygame.Rect(C.WIDTH//2 - 320, 176, 640, C.HEIGHT - 250))
    y = 192
    for rank, entry in enumerate(entries, 1):
        if isinstance(entry, (list, tuple)):
            sc, ts = entry[0], entry[1]
        else:
            sc, ts = entry, ""
        if rank == 1:   col = YELLOW
        elif rank <= 3: col = (200, 200, 255)
        else:           col = DIM
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
        msg = "No scores recorded today" if period == "today" else "No scores recorded yet"
        empty = C.FONT_HUD.render(msg, True, DIM)
        surface.blit(empty, (C.WIDTH//2 - empty.get_width()//2, 240))
    bk = Button((C.WIDTH//2 - 120, C.HEIGHT - 62, 240, 46),
                "Back to Menu", (30,34,70), BTN_LEADER_H, CYAN)
    bk.draw(surface)
    return [bk], tab_buttons, period_tabs


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
        sh = C.FONT_SMALL.render("◈  SHIELD BASH ACTIVE", True, GREEN)
        surface.blit(sh, (C.WIDTH//2 - sh.get_width()//2, 12))
    if PU_GHOST in active_pus:
        gh = C.FONT_SMALL.render("◌  GHOST ACTIVE", True, (200, 200, 255))
        offset = 32 if shield else 12
        surface.blit(gh, (C.WIDTH//2 - gh.get_width()//2, offset))
    if PU_MAGNET in active_pus:
        mg = C.FONT_SMALL.render("◈  MAGNET ACTIVE", True, PINK)
        top = [shield, PU_GHOST in active_pus].count(True)
        surface.blit(mg, (C.WIDTH//2 - mg.get_width()//2, 12 + top * 22))
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
            is_active = (td["id"] == active)
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
    from settings import PLAYER_COLORS
    from trails import TRAIL_DEFS, get_unlocked, get_active
    surface.fill(C.BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (18, 20, 34), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (18, 20, 34), (0, y), (C.WIDTH, y))

    title = C.FONT_BIG.render("SETTINGS", True, CYAN)
    surface.blit(title, (C.WIDTH//2 - title.get_width()//2, 22))

    result = {"back": [], "toggle_fs": [], "colors": [], "trails": [], "sliders": []}

    # layout: two columns centered on screen
    total_w = 1020
    left_x  = C.WIDTH//2 - total_w//2
    right_x = left_x + 520
    col_w_l = 480
    col_w_r = 480
    y = 100

    # FULLSCREEN toggle — spans both columns, centered
    fs_w = 440
    fs_x = C.WIDTH//2 - fs_w//2
    _panel(surface, pygame.Rect(fs_x, y, fs_w, 60))
    fs_lbl = C.FONT_HUD.render("FULLSCREEN", True, WHITE)
    surface.blit(fs_lbl, (fs_x + 20, y + 16))
    fs_state = "ON" if cfg.get("fullscreen", True) else "OFF"
    fs_col   = GREEN if cfg.get("fullscreen") else RED
    fs_btn   = Button((fs_x + fs_w - 130, y + 10, 110, 40), fs_state, fs_col,
                    tuple(min(255, v+60) for v in fs_col))
    fs_btn.draw(surface)
    result["toggle_fs"].append(fs_btn)

    y += 82

    # PLAYER COLOR — left column
    pc_h = 200
    _panel(surface, pygame.Rect(left_x, y, col_w_l, pc_h))
    lbl = C.FONT_HUD.render("PLAYER COLOR", True, WHITE)
    surface.blit(lbl, (left_x + 20, y + 14))
    active_idx = cfg.get("player_color", 0)
    sw, sw_gap = 42, 12
    row_start_x = left_x + 20
    swatch_y = y + 52
    for i, pc in enumerate(PLAYER_COLORS):
        col    = pc["color"]
        bx     = row_start_x + (i % 4) * (sw + sw_gap)
        by     = swatch_y + (i // 4) * (sw + 10)
        selected = (i == active_idx)
        if selected:
            gs = pygame.Surface((sw+12, sw+12), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*col, 80), (0,0,sw+12,sw+12), border_radius=8)
            surface.blit(gs, (bx-6, by-6))
        pygame.draw.rect(surface, col, (bx, by, sw, sw), border_radius=6)
        pygame.draw.rect(surface, WHITE if selected else DIM, (bx, by, sw, sw), 2, border_radius=6)
        b = Button((bx, by, sw, sw), "", col, tuple(min(255,v+60) for v in col))
        result["colors"].append((b, i))
    # selected color name + preview dot on same row
    name_txt = C.FONT_SMALL.render(PLAYER_COLORS[active_idx]["name"], True, YELLOW)
    name_y   = y + pc_h - 32
    surface.blit(name_txt, (left_x + 20, name_y))
    prev_col = PLAYER_COLORS[active_idx]["color"]
    pygame.draw.circle(surface, prev_col, (left_x + col_w_l - 30, name_y + 10), 12)
    pygame.draw.circle(surface, WHITE,    (left_x + col_w_l - 30, name_y + 10), 12, 2)

    # VOLUME sliders — left column below color
    vol_y = y + pc_h + 18
    _panel(surface, pygame.Rect(left_x, vol_y, col_w_l, 130))
    vol_lbl = C.FONT_HUD.render("VOLUME", True, WHITE)
    surface.blit(vol_lbl, (left_x + 20, vol_y + 12))
    sliders = []
    for i, (label, val, key) in enumerate([("SFX",   cfg.get("sfx_volume",   0.7),  "sfx_volume"),
                                            ("MUSIC", cfg.get("music_volume", 0.45), "music_volume")]):
        row_y   = vol_y + 50 + i * 46
        lbl_s   = C.FONT_SMALL.render(f"{label}  {int(val*100):>3}%", True, WHITE)
        surface.blit(lbl_s, (left_x + 20, row_y))
        track_x = left_x + 140
        track_y = row_y + 8
        track_w = col_w_l - 160
        track_h = 6
        thumb_r = 9
        pygame.draw.rect(surface, (40,42,65), (track_x, track_y, track_w, track_h), border_radius=3)
        filled_w = int(track_w * val)
        pygame.draw.rect(surface, CYAN, (track_x, track_y, max(0,filled_w), track_h), border_radius=3)
        thumb_x = track_x + filled_w
        pygame.draw.circle(surface, WHITE, (thumb_x, track_y + track_h//2), thumb_r)
        pygame.draw.circle(surface, CYAN,  (thumb_x, track_y + track_h//2), thumb_r - 2)
        sliders.append({"key": key, "track_x": track_x, "track_y": track_y,
                        "track_w": track_w, "track_h": track_h, "thumb_r": thumb_r,
                        "rect": pygame.Rect(track_x - thumb_r, track_y - thumb_r,
                                            track_w + thumb_r*2, track_h + thumb_r*2)})
    result["sliders"] = sliders

    # TRAIL STYLE — right column
    trail_h = pc_h + 18 + 130
    _panel(surface, pygame.Rect(right_x, y, col_w_r, trail_h))
    trl = C.FONT_HUD.render("TRAIL STYLE", True, WHITE)
    surface.blit(trl, (right_x + 20, y + 14))
    unlocked     = set(get_unlocked())
    active_trail = get_active()
    ty = y + 54
    tbw, tbh = col_w_r - 40, 38
    tbx = right_x + 20
    for td in TRAIL_DEFS:
        locked = td["id"] not in unlocked
        is_act = (td["id"] == active_trail)
        if locked:
            bg = (22,22,38); hov = (22,22,38); tc = DIM
            txt = f"{td['name']}  @ {td['unlock']}"
        else:
            bg  = (20,80,30) if is_act else (28,30,55)
            hov = GREEN if is_act else (60,80,160)
            tc  = WHITE
            txt = td["name"] + (" ✓" if is_act else "")
        b = Button((tbx, ty, tbw, tbh), txt, bg, hov, tc)
        if not locked:
            b.draw(surface)
        else:
            pygame.draw.rect(surface, bg, (tbx, ty, tbw, tbh), border_radius=6)
            pygame.draw.rect(surface, (35,35,55), (tbx, ty, tbw, tbh), 1, border_radius=6)
            ll = C.FONT_SMALL.render(txt, True, DIM)
            surface.blit(ll, (tbx + tbw//2 - ll.get_width()//2, ty + tbh//2 - ll.get_height()//2))
        result["trails"].append((b, td["id"], locked))
        ty += tbh + 10

    # BACK button — centered at bottom
    bk = Button((C.WIDTH//2 - 120, C.HEIGHT - 68, 240, 48), "Back to Menu", (30,34,70), BTN_LEADER_H, CYAN)
    bk.draw(surface)
    result["back"].append(bk)
    return result


def draw_profile(surface, active_tab: int) -> tuple:
    """
    Two-tab profile screen.
    active_tab: 0 = Profile, 1 = Achievements
    Returns (tab_buttons, back_button)
    """
    from trails import TRAIL_DEFS, get_unlocked as get_unlocked_trails
    from achievements import get_all_for_display, ACHIEVEMENTS
    from scores import get_scores

    surface.fill(BG)
    for x in range(0, C.WIDTH, 60):
        pygame.draw.line(surface, (18, 20, 34), (x, 0), (x, C.HEIGHT))
    for y in range(0, C.HEIGHT, 60):
        pygame.draw.line(surface, (18, 20, 34), (0, y), (C.WIDTH, y))

    title = C.FONT_BIG.render("PROFILE", True, PURPLE)
    surface.blit(title, (C.WIDTH//2 - title.get_width()//2, 20))

    # tabs
    tab_labels = ["Profile", "Achievements"]
    tab_w, tab_h = 240, 44
    tab_start = C.WIDTH//2 - (tab_w * 2 + 10)//2
    tab_buttons = []
    for i, lbl in enumerate(tab_labels):
        tx   = tab_start + i * (tab_w + 10)
        active = (i == active_tab)
        bg   = PURPLE if active else (40, 22, 60)
        hov  = (220, 100, 255)
        tc   = DARK if active else WHITE
        b    = Button((tx, 72, tab_w, tab_h), lbl, bg, hov, tc)
        b.draw(surface)
        tab_buttons.append(b)

    content_y = 130
    content_h = C.HEIGHT - content_y - 80
    pw        = C.WIDTH - 120
    px        = 60

    if active_tab == 0:
        # PROFILE TAB: high scores + unlocked trails
        # left half: scores per mode
        half_w = pw // 2 - 10
        _panel(surface, pygame.Rect(px, content_y, half_w, content_h))
        sh = C.FONT_HUD.render("HIGH SCORES", True, CYAN)
        surface.blit(sh, (px + 20, content_y + 14))
        sy = content_y + 52
        for mode in MODES:
            mode_col = {"classic": CYAN, "shrink": PURPLE, "hardcore": RED}.get(mode, WHITE)
            mh = C.FONT_HUD.render(mode.upper(), True, mode_col)
            surface.blit(mh, (px + 20, sy))
            sy += 32
            entries = get_scores(mode)
            if not entries:
                empty = C.FONT_SMALL.render("No scores yet", True, DIM)
                surface.blit(empty, (px + 36, sy))
                sy += 28
            else:
                for rank, entry in enumerate(entries[:5], 1):
                    sc = entry[0] if isinstance(entry, (list, tuple)) else entry
                    ts = entry[1] if isinstance(entry, (list, tuple)) else ""
                    rc = YELLOW if rank == 1 else (WHITE if rank <= 3 else DIM)
                    row = C.FONT_SMALL.render(f"#{rank}  {sc:<6}  {ts}", True, rc)
                    surface.blit(row, (px + 36, sy))
                    sy += 26
            sy += 12
            pygame.draw.line(surface, (35,37,60), (px+14, sy), (px+half_w-14, sy))
            sy += 14

        # right half: trail styles
        rx = px + half_w + 20
        _panel(surface, pygame.Rect(rx, content_y, half_w, content_h))
        th = C.FONT_HUD.render("TRAIL STYLES", True, CYAN)
        surface.blit(th, (rx + 20, content_y + 14))
        unlocked_trails = set(get_unlocked_trails())
        from trails import get_color_fn
        ty = content_y + 52
        for td in TRAIL_DEFS:
            locked  = td["id"] not in unlocked_trails
            row_h   = 52
            # trail color preview strip
            strip_x = rx + 20
            strip_y = ty + 16
            fn      = get_color_fn(td["id"]) if not locked else None
            for xi in range(120):
                frac = xi / 119
                if locked:
                    v   = int(40 + frac * 30)
                    col = (v, v, v)
                else:
                    col = fn(frac, 500)
                pygame.draw.line(surface, col, (strip_x + xi, strip_y), (strip_x + xi, strip_y + 10))
            # name
            name_col = WHITE if not locked else (60, 62, 80)
            nm  = C.FONT_HUD.render(td["name"], True, name_col)
            surface.blit(nm, (strip_x + 130, ty + 10))
            if locked:
                lk = C.FONT_SMALL.render(f"Unlock @ score {td['unlock']}", True, DIM)
                surface.blit(lk, (strip_x + 130, ty + 32))
            else:
                ul = C.FONT_SMALL.render("Unlocked ✓", True, GREEN)
                surface.blit(ul, (strip_x + 130, ty + 32))
            ty += row_h + 6

    else:
        # ACHIEVEMENTS TAB
        all_ach = get_all_for_display()
        unlocked_count = sum(1 for a in all_ach if a["unlocked"])
        prog = C.FONT_HUD.render(f"{unlocked_count} / {len(all_ach)} unlocked", True, YELLOW)
        surface.blit(prog, (C.WIDTH//2 - prog.get_width()//2, content_y - 2))

        # grid: 2 columns
        col_w   = pw // 2 - 10
        cols    = 2
        item_h  = 72
        margin  = 10
        for i, ach in enumerate(all_ach):
            col_idx = i % cols
            row_idx = i // cols
            ax = px + col_idx * (col_w + 20)
            ay = content_y + 26 + row_idx * (item_h + margin)
            if ay + item_h > C.HEIGHT - 80:
                break  # don't overflow screen
            locked = not ach["unlocked"]
            bg_col = (22, 18, 38) if locked else (32, 28, 55)
            pygame.draw.rect(surface, bg_col, (ax, ay, col_w, item_h), border_radius=8)
            border = (40, 40, 60) if locked else PURPLE
            pygame.draw.rect(surface, border, (ax, ay, col_w, item_h), 2, border_radius=8)
            if locked:
                # greyscale icon + locked label
                ico = C.FONT_BIG.render("🔒", True, (60, 62, 80))
                surface.blit(ico, (ax + 12, ay + item_h//2 - ico.get_height()//2))
                nm  = C.FONT_HUD.render(ach["name"], True, (70, 72, 90))
                dsc = C.FONT_SMALL.render(ach["desc"], True, (50, 52, 70))
            else:
                ico = C.FONT_BIG.render(ach["icon"], True, YELLOW)
                surface.blit(ico, (ax + 12, ay + item_h//2 - ico.get_height()//2))
                nm  = C.FONT_HUD.render(ach["name"], True, WHITE)
                dsc = C.FONT_SMALL.render(ach["desc"], True, (160, 162, 190))
            surface.blit(nm,  (ax + 58, ay + 12))
            surface.blit(dsc, (ax + 58, ay + 38))

    back = Button((C.WIDTH//2 - 120, C.HEIGHT - 62, 240, 46),
                "Back to Menu", (30,34,70), BTN_LEADER_H, CYAN)
    back.draw(surface)
    return tab_buttons, back
