# -*- coding: utf-8 -*-
"""
ui.py - All HUD, menus, and overlay rendering.

Includes:
  - HUD (coins, key indicator, score)
  - Main menu
  - Pause menu
  - Win screen
  - Death / game-over overlay
  - Control hints
"""

import pygame
import math
from settings import *
from draw_utils import make_coin_surf, make_key_surf, make_chest_surf


# -----------------------------------------------------------------------
# Font cache
# -----------------------------------------------------------------------

_font_cache: dict = {}


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        try:
            _font_cache[key] = pygame.font.SysFont("segoeui", size, bold=bold)
        except Exception:
            _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]


# -----------------------------------------------------------------------
# Drawing helpers
# -----------------------------------------------------------------------

def draw_text_shadow(surf, text, font, color, pos,
                     shadow_color=(0, 0, 0), shadow_offset=2):
    shd = font.render(text, True, shadow_color)
    surf.blit(shd, (pos[0] + shadow_offset, pos[1] + shadow_offset))
    img = font.render(text, True, color)
    surf.blit(img, pos)
    return img.get_rect(topleft=pos)


def draw_rounded_box(surf, rect, color=(20, 20, 40, 200),
                     border_color=None, radius=12):
    box = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(box, color, (0, 0, rect.width, rect.height),
                     border_radius=radius)
    surf.blit(box, rect.topleft)
    if border_color:
        pygame.draw.rect(surf, border_color, rect, 3, border_radius=radius)


def draw_button(surf, text, rect, hover=False, font_size=28):
    bg = (255, 230, 80) if hover else (50, 40, 20)
    tc = (30, 20, 0)    if hover else UI_TEXT
    draw_rounded_box(surf, rect, color=(*bg, 230),
                     border_color=UI_BORDER, radius=10)
    font = get_font(font_size, bold=True)
    txt  = font.render(text, True, tc)
    tx   = rect.centerx - txt.get_width()  // 2
    ty   = rect.centery - txt.get_height() // 2
    surf.blit(txt, (tx, ty))


# -----------------------------------------------------------------------
# HUD icon singletons
# -----------------------------------------------------------------------

_COIN_HUD = None
_KEY_HUD  = None


def _get_coin_hud():
    global _COIN_HUD
    if _COIN_HUD is None:
        _COIN_HUD = make_coin_surf(12)
    return _COIN_HUD


def _get_key_hud():
    global _KEY_HUD
    if _KEY_HUD is None:
        _KEY_HUD = make_key_surf(28)
    return _KEY_HUD


# -----------------------------------------------------------------------
# HUD
# -----------------------------------------------------------------------

def draw_hud(surf, coins, total_coins, has_key, paused,
             level_done, timer_s):
    """Top HUD bar - coins, key, timer, controls hint."""
    # Left panel
    panel = pygame.Rect(8, 8, 300, 52)
    draw_rounded_box(surf, panel, color=(10, 10, 30, 180),
                     border_color=(255, 215, 0), radius=10)

    # Coin icon + count
    coin_img = _get_coin_hud()
    surf.blit(coin_img, (18, 18))
    font = get_font(22, bold=True)
    draw_text_shadow(surf, "{:02d} / {:02d}".format(coins, total_coins),
                     font, COIN_YELLOW, (44, 22))

    # Key indicator
    key_img = _get_key_hud()
    kx = 170
    if has_key:
        surf.blit(key_img, (kx, 14))
        draw_text_shadow(surf, "KEY", font, KEY_GOLD, (kx + 34, 22))
    else:
        grey = key_img.copy()
        grey.fill((80, 80, 80, 180), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(grey, (kx, 14))

    # Right timer panel
    panel2 = pygame.Rect(SCREEN_WIDTH - 130, 8, 122, 52)
    draw_rounded_box(surf, panel2, color=(10, 10, 30, 180),
                     border_color=(255, 215, 0), radius=10)
    m = int(timer_s) // 60
    s = int(timer_s) % 60
    draw_text_shadow(surf, "Time {:02d}:{:02d}".format(m, s),
                     get_font(20, bold=True), WHITE,
                     (SCREEN_WIDTH - 126, 22))

    # Controls hint (bottom left)
    hint_font = get_font(15)
    hints = "WASD/Arrows: Move  |  Space/Up: Jump  |  P: Pause  |  R: Restart"
    draw_text_shadow(surf, hints, hint_font, (200, 200, 200),
                     (10, SCREEN_HEIGHT - 24), shadow_offset=1)


# -----------------------------------------------------------------------
# Main Menu
# -----------------------------------------------------------------------

class MainMenu:
    """Animated main menu screen."""

    def __init__(self):
        self._time = 0.0
        self._star_positions = [
            (int(SCREEN_WIDTH * 0.05 * i),
             int(SCREEN_HEIGHT * 0.1 * (i % 9) + 20))
            for i in range(1, 14)
        ]

    def update(self, dt_ms):
        self._time += dt_ms * 0.001

    def draw(self, surf, mouse_pos):
        """Draw the main menu and return button rects dict."""
        from draw_utils import draw_sky_gradient
        draw_sky_gradient(surf, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Sparkle stars
        for i, (sx, sy) in enumerate(self._star_positions):
            r     = int(3 + 2 * math.sin(self._time * 2 + i))
            alpha = int(180 + 75 * math.sin(self._time * 1.5 + i))
            tmp   = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (*COIN_YELLOW, alpha), (r, r), r)
            surf.blit(tmp, (sx - r, sy - r))

        # Title card
        title_card = pygame.Rect(SCREEN_WIDTH // 2 - 340, 90, 680, 130)
        draw_rounded_box(surf, title_card,
                         color=(10, 5, 40, 210), border_color=COIN_YELLOW,
                         radius=20)

        # Pulsing title
        t_font = get_font(int(66 * (1 + 0.04 * math.sin(self._time * 2.5))),
                          bold=True)
        title  = t_font.render("ISLAND  HOPPER", True, COIN_YELLOW)
        surf.blit(title,
                  (SCREEN_WIDTH // 2 - title.get_width() // 2, 104))

        sub_font = get_font(24)
        sub = sub_font.render("A Cartoon Arcade Platformer",
                              True, (200, 240, 255))
        surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 192))

        # Buttons
        bw, bh = 260, 56
        cx = SCREEN_WIDTH // 2 - bw // 2
        play_rect = pygame.Rect(cx, 280, bw, bh)
        quit_rect = pygame.Rect(cx, 360, bw, bh)

        draw_button(surf, "PLAY GAME", play_rect,
                    hover=play_rect.collidepoint(mouse_pos))
        draw_button(surf, "QUIT", quit_rect,
                    hover=quit_rect.collidepoint(mouse_pos))

        # Instructions
        ctrl_font = get_font(18)
        lines = [
            "Arrow Keys / WASD : Move & Jump",
            "Up / W on Ladder  : Climb",
            "P : Pause    R : Restart    ESC : Main Menu",
            "Collect coins, grab the Key, then open the Treasure Chest!",
        ]
        y0 = 450
        for line in lines:
            img = ctrl_font.render(line, True, (190, 220, 255))
            surf.blit(img,
                      (SCREEN_WIDTH // 2 - img.get_width() // 2, y0))
            y0 += 28

        return {"play": play_rect, "quit": quit_rect}


# -----------------------------------------------------------------------
# Pause Menu
# -----------------------------------------------------------------------

class PauseMenu:
    """Semi-transparent pause overlay."""

    def draw(self, surf, mouse_pos):
        # Dim overlay
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 30, 160))
        surf.blit(dim, (0, 0))

        # Panel
        pw, ph = 400, 340
        px = SCREEN_WIDTH  // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        panel = pygame.Rect(px, py, pw, ph)
        draw_rounded_box(surf, panel, color=(10, 10, 40, 230),
                         border_color=COIN_YELLOW, radius=16)

        # Title
        t_font = get_font(48, bold=True)
        title  = t_font.render("PAUSED", True, COIN_YELLOW)
        surf.blit(title,
                  (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 30))

        # Buttons
        bw, bh = 240, 52
        bx = SCREEN_WIDTH // 2 - bw // 2
        resume_rect  = pygame.Rect(bx, py + 110, bw, bh)
        restart_rect = pygame.Rect(bx, py + 178, bw, bh)
        menu_rect    = pygame.Rect(bx, py + 246, bw, bh)

        draw_button(surf, "RESUME",    resume_rect,
                    hover=resume_rect.collidepoint(mouse_pos))
        draw_button(surf, "RESTART",   restart_rect,
                    hover=restart_rect.collidepoint(mouse_pos))
        draw_button(surf, "MAIN MENU", menu_rect,
                    hover=menu_rect.collidepoint(mouse_pos))

        return {"resume": resume_rect, "restart": restart_rect,
                "menu": menu_rect}


# -----------------------------------------------------------------------
# Win Screen
# -----------------------------------------------------------------------

class WinScreen:
    """Victory overlay with star rating."""

    def __init__(self):
        self._time = 0.0
        self._chest_surf = make_chest_surf(80, 60, open_=True)

    def update(self, dt_ms):
        self._time += dt_ms * 0.001

    def draw(self, surf, coins, total, elapsed_s, mouse_pos):
        # Dim
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        surf.blit(dim, (0, 0))

        # Panel
        pw, ph = 540, 460
        px = SCREEN_WIDTH  // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        panel = pygame.Rect(px, py, pw, ph)
        draw_rounded_box(surf, panel, color=(10, 50, 10, 230),
                         border_color=COIN_YELLOW, radius=20)

        # Bobbing chest
        cy_off = int(6 * math.sin(self._time * 3))
        surf.blit(self._chest_surf,
                  (SCREEN_WIDTH // 2 - 40, py + 18 + cy_off))

        # Title
        t_font = get_font(56, bold=True)
        title  = t_font.render("YOU WIN!", True, COIN_YELLOW)
        surf.blit(title,
                  (SCREEN_WIDTH // 2 - title.get_width() // 2, py + 90))

        # Stats
        sf  = get_font(26)
        m   = int(elapsed_s) // 60
        s   = int(elapsed_s) % 60
        pct = int(coins / max(total, 1) * 100)
        for i, line in enumerate([
            "Coins: {} / {}  ({}%)".format(coins, total, pct),
            "Time:  {:02d}:{:02d}".format(m, s),
        ]):
            img = sf.render(line, True, WHITE)
            surf.blit(img,
                      (SCREEN_WIDTH // 2 - img.get_width() // 2,
                       py + 170 + i * 38))

        # Star rating (ASCII stars)
        stars     = 1 + (1 if pct >= 50 else 0) + (1 if pct >= 90 else 0)
        star_font = get_font(46)
        star_str  = "* " * stars + ". " * (3 - stars)
        star_img  = star_font.render(star_str.strip(), True, COIN_YELLOW)
        surf.blit(star_img,
                  (SCREEN_WIDTH // 2 - star_img.get_width() // 2,
                   py + 256))

        # Star label
        lbl_font = get_font(20)
        lbl      = lbl_font.render("({} / 3 stars)".format(stars),
                                   True, (200, 220, 180))
        surf.blit(lbl,
                  (SCREEN_WIDTH // 2 - lbl.get_width() // 2, py + 308))

        # Buttons
        bw, bh = 220, 52
        bx = SCREEN_WIDTH // 2 - bw // 2
        restart_rect = pygame.Rect(bx, py + 350, bw, bh)
        menu_rect    = pygame.Rect(bx, py + 416, bw, bh)

        draw_button(surf, "PLAY AGAIN", restart_rect,
                    hover=restart_rect.collidepoint(mouse_pos))
        draw_button(surf, "MAIN MENU",  menu_rect,
                    hover=menu_rect.collidepoint(mouse_pos))

        return {"restart": restart_rect, "menu": menu_rect}


# -----------------------------------------------------------------------
# Death Screen
# -----------------------------------------------------------------------

class DeathScreen:

    def __init__(self):
        self._time = 0.0

    def update(self, dt_ms):
        self._time += dt_ms * 0.001

    def draw(self, surf, mouse_pos):
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((60, 0, 0, 160))
        surf.blit(dim, (0, 0))

        pw, ph = 420, 300
        px = SCREEN_WIDTH  // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        panel = pygame.Rect(px, py, pw, ph)
        draw_rounded_box(surf, panel, color=(40, 0, 0, 230),
                         border_color=(200, 50, 50), radius=16)

        t_font = get_font(52, bold=True)
        shake  = int(3 * math.sin(self._time * 20))
        title  = t_font.render("YOU FELL!", True, (255, 80, 80))
        surf.blit(title,
                  (SCREEN_WIDTH // 2 - title.get_width() // 2 + shake,
                   py + 40))

        sf  = get_font(22)
        msg = sf.render("Fell into the void...", True, (255, 180, 180))
        surf.blit(msg,
                  (SCREEN_WIDTH // 2 - msg.get_width() // 2, py + 110))

        bw, bh = 220, 52
        bx = SCREEN_WIDTH // 2 - bw // 2
        retry_rect = pygame.Rect(bx, py + 170, bw, bh)
        menu_rect  = pygame.Rect(bx, py + 236, bw, bh)

        draw_button(surf, "TRY AGAIN", retry_rect,
                    hover=retry_rect.collidepoint(mouse_pos))
        draw_button(surf, "MAIN MENU", menu_rect,
                    hover=menu_rect.collidepoint(mouse_pos))

        return {"retry": retry_rect, "menu": menu_rect}
