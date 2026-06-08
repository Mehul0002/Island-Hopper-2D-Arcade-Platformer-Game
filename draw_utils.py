"""
draw_utils.py – Procedural sprite/surface drawing helpers.

All game graphics are drawn here with pygame.draw calls so the game
requires zero external image assets.
"""

import math
import pygame
from settings import *


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _aa_circle(surf, color, center, radius):
    pygame.draw.circle(surf, color, center, radius)


def lighten(color, amount=30):
    return tuple(min(255, c + amount) for c in color)


def darken(color, amount=30):
    return tuple(max(0, c - amount) for c in color)


# ──────────────────────────────────────────────────────────────────────────────
# Background
# ──────────────────────────────────────────────────────────────────────────────

def draw_sky_gradient(surf: pygame.Surface, w: int, h: int) -> None:
    """Vertical gradient sky."""
    top = SKY_TOP
    bot = SKY_BOT
    for y in range(h):
        t = y / h
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))


def draw_mountains(surf: pygame.Surface, cam_ox: float, w: int, h: int) -> None:
    """Parallax mountain silhouettes."""
    # Far mountains (slow parallax)
    pts_far = []
    num = 8
    for i in range(num + 1):
        bx = (i / num) * (w + 200) - 100 + cam_ox * 0.05
        bx = bx % (w + 200) - 100
        peak = h * 0.62 - math.sin(i * 1.3 + 1) * 90 - math.sin(i * 0.7) * 50
        pts_far.append((bx, peak))
    pts_far = [(0, h)] + pts_far + [(w, h)]
    pygame.draw.polygon(surf, MTN_BLUE, pts_far)
    pygame.draw.polygon(surf, darken(MTN_BLUE, 15), pts_far, 2)

    # Near mountains (faster parallax)
    pts_near = []
    num2 = 6
    for i in range(num2 + 1):
        bx = (i / num2) * (w + 300) - 150 + cam_ox * 0.12
        bx = bx % (w + 300) - 150
        peak = h * 0.75 - math.sin(i * 1.7 + 0.5) * 70 - math.sin(i * 0.9) * 40
        pts_near.append((bx, peak))
    pts_near = [(0, h)] + pts_near + [(w, h)]
    pygame.draw.polygon(surf, MTN_DARK, pts_near)


def make_cloud_surf(w: int, h: int) -> pygame.Surface:
    """Return a surface containing a fluffy cartoon cloud."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    r = h // 2
    # Main body
    pygame.draw.ellipse(surf, CLOUD_WHITE, (cx - r, cy - r // 2, r * 2, r))
    # Bumps
    for dx, dy, dr in [(-r // 2, 0, r // 2 + 4), (r // 2, 0, r // 2 + 4),
                        (0, -r // 2, r // 2 + 6)]:
        pygame.draw.circle(surf, CLOUD_WHITE, (cx + dx, cy + dy), dr)
    return surf


# ──────────────────────────────────────────────────────────────────────────────
# Terrain tiles
# ──────────────────────────────────────────────────────────────────────────────

def make_grass_tile(size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Dirt fill
    surf.fill(DIRT_BROWN)
    # Dirt detail stones
    for sx, sy in [(8, 18), (24, 26), (38, 14)]:
        pygame.draw.ellipse(surf, STONE_GRAY, (sx, sy, 10, 7))
        pygame.draw.ellipse(surf, STONE_DARK, (sx, sy, 10, 7), 1)
    # Grass top strip
    pygame.draw.rect(surf, GRASS_GREEN, (0, 0, size, size // 5))
    pygame.draw.rect(surf, GRASS_DARK,  (0, 0, size, 3))
    # Grass tufts
    for gx in range(4, size, 8):
        pygame.draw.line(surf, GRASS_DARK,
                         (gx, size // 5), (gx - 2, size // 5 - 5), 2)
        pygame.draw.line(surf, GRASS_DARK,
                         (gx + 2, size // 5), (gx + 4, size // 5 - 5), 2)
    return surf


def make_dirt_tile(size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill(DIRT_BROWN)
    for sx, sy in [(6, 10), (22, 28), (36, 16), (14, 38)]:
        pygame.draw.ellipse(surf, STONE_GRAY, (sx, sy, 12, 8))
        pygame.draw.ellipse(surf, STONE_DARK, (sx, sy, 12, 8), 1)
    return surf


def make_stone_tile(size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill(STONE_GRAY)
    for sx, sy in [(4, 4), (24, 10), (8, 30), (34, 28)]:
        pygame.draw.rect(surf, STONE_DARK, (sx, sy, 14, 10), 1)
    return surf


def make_island_surface(w_tiles: int, tile_size: int) -> pygame.Surface:
    """
    A floating island: rounded dirt body with grass top.
    Width in tiles, height = 2 tiles with a rounded bottom.
    """
    pw = w_tiles * tile_size
    ph = tile_size * 2
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)

    # Dirt body (rounded rect)
    body = pygame.Rect(0, tile_size // 3, pw, ph - tile_size // 3)
    pygame.draw.rect(surf, DIRT_BROWN, body, border_radius=tile_size // 2)
    pygame.draw.rect(surf, DIRT_DARK, body, 3, border_radius=tile_size // 2)

    # Stone details
    for sx in range(8, pw - 8, 20):
        sy = tile_size // 2 + 14
        pygame.draw.ellipse(surf, STONE_GRAY, (sx, sy, 14, 9))

    # Grass top
    grass_h = tile_size // 3
    grass_rect = pygame.Rect(0, 0, pw, grass_h + 6)
    pygame.draw.rect(surf, GRASS_GREEN, grass_rect, border_radius=6)
    pygame.draw.rect(surf, GRASS_DARK,  (0, 0, pw, 4), border_radius=4)
    # Tufts
    for gx in range(6, pw - 6, 10):
        pygame.draw.line(surf, GRASS_DARK,
                         (gx, grass_h), (gx - 2, grass_h - 6), 2)
        pygame.draw.line(surf, GRASS_DARK,
                         (gx + 2, grass_h), (gx + 4, grass_h - 6), 2)
    return surf


# ──────────────────────────────────────────────────────────────────────────────
# Interactive objects
# ──────────────────────────────────────────────────────────────────────────────

def make_coin_surf(radius: int) -> pygame.Surface:
    d = radius * 2 + 4
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    cx, cy = d // 2, d // 2
    pygame.draw.circle(surf, COIN_DARK,   (cx, cy), radius)
    pygame.draw.circle(surf, COIN_YELLOW, (cx, cy), radius - 2)
    pygame.draw.circle(surf, lighten(COIN_YELLOW, 60), (cx - 3, cy - 3), radius // 3)
    return surf


def make_key_surf(size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    r = size // 4
    # Ring
    pygame.draw.circle(surf, darken(KEY_GOLD, 20), (cx, cy - r), r + 2)
    pygame.draw.circle(surf, KEY_GOLD,             (cx, cy - r), r)
    pygame.draw.circle(surf, lighten(KEY_GOLD, 60),(cx - 2, cy - r - 2), r // 2)
    # Shaft
    pygame.draw.rect(surf, KEY_GOLD,             (cx - 3, cy, 6, size // 2 + 2))
    pygame.draw.rect(surf, darken(KEY_GOLD, 20), (cx - 3, cy, 6, size // 2 + 2), 1)
    # Teeth
    for dy in [size // 2 + 4, size // 2 + 10]:
        pygame.draw.rect(surf, KEY_GOLD, (cx + 3, dy, 5, 4))
    return surf


def make_chest_surf(w: int, h: int, open_: bool = False) -> pygame.Surface:
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Body
    pygame.draw.rect(surf, CHEST_BROWN, (0, h // 3, w, h * 2 // 3), border_radius=4)
    pygame.draw.rect(surf, darken(CHEST_BROWN, 30), (0, h // 3, w, h * 2 // 3), 2, border_radius=4)
    # Lid
    lid_h = h // 3 + 4
    lid_rect = (0, 0, w, lid_h)
    if not open_:
        pygame.draw.rect(surf, darken(CHEST_BROWN, 10), lid_rect, border_radius=4)
        pygame.draw.rect(surf, darken(CHEST_BROWN, 40), lid_rect, 2, border_radius=4)
    else:
        # Open lid tilted back
        pygame.draw.rect(surf, darken(CHEST_BROWN, 10), (0, -lid_h + 4, w, lid_h),
                         border_radius=4)
        # Coins spilling
        for gx, gy in [(w // 2, -4), (w // 4, 2), (3 * w // 4, 0)]:
            pygame.draw.circle(surf, COIN_YELLOW, (gx, gy), 5)
    # Metal bands
    pygame.draw.rect(surf, CHEST_GOLD, (0, h // 3 + 2, w, 5))
    pygame.draw.rect(surf, CHEST_GOLD, (w // 2 - 3, 0, 6, h))
    # Lock
    pygame.draw.rect(surf, CHEST_GOLD, (w // 2 - 5, h // 2 - 2, 10, 8), border_radius=2)
    return surf


def make_crate_surf(size: int) -> pygame.Surface:
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, WOOD_LIGHT, (0, 0, size, size), border_radius=4)
    pygame.draw.rect(surf, WOOD_DARK,  (0, 0, size, size), 3, border_radius=4)
    # Wood planks
    pygame.draw.line(surf, WOOD_DARK, (0, size // 3),     (size, size // 3),     2)
    pygame.draw.line(surf, WOOD_DARK, (0, 2 * size // 3), (size, 2 * size // 3), 2)
    pygame.draw.line(surf, WOOD_DARK, (size // 3, 0),     (size // 3, size),     2)
    pygame.draw.line(surf, WOOD_DARK, (2 * size // 3, 0), (2 * size // 3, size), 2)
    # Diagonal cross
    pygame.draw.line(surf, darken(WOOD_LIGHT, 20), (4, 4), (size - 4, size - 4), 2)
    pygame.draw.line(surf, darken(WOOD_LIGHT, 20), (size - 4, 4), (4, size - 4), 2)
    return surf


def make_ladder_surf(width: int, height: int) -> pygame.Surface:
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rail_w = 5
    rung_h = 16
    # Rails
    pygame.draw.rect(surf, WOOD_DARK, (0,           0, rail_w, height))
    pygame.draw.rect(surf, WOOD_DARK, (width - rail_w, 0, rail_w, height))
    # Rungs
    y = 4
    while y < height:
        pygame.draw.rect(surf, WOOD_LIGHT, (rail_w, y, width - rail_w * 2, 4))
        y += rung_h
    return surf


def make_flag_surf(pole_h: int) -> pygame.Surface:
    w = 40
    surf = pygame.Surface((w, pole_h + 20), pygame.SRCALPHA)
    # Pole
    pygame.draw.rect(surf, WOOD_DARK, (w // 2 - 2, 10, 4, pole_h))
    # Flag
    pts = [(w // 2 + 2, 10), (w // 2 + 2 + 20, 20), (w // 2 + 2, 30)]
    pygame.draw.polygon(surf, FLAG_RED, pts)
    pygame.draw.polygon(surf, darken(FLAG_RED, 30), pts, 2)
    return surf


def make_cave_surf(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Hill
    pts = [(0, h), (0, h * 0.4),
           (w * 0.5, 0),
           (w, h * 0.4), (w, h)]
    pygame.draw.polygon(surf, STONE_GRAY, pts)
    pygame.draw.polygon(surf, STONE_DARK, pts, 3)
    # Dark arch entrance
    arch_w, arch_h = w // 2, h // 2
    arch_x = w // 2 - arch_w // 2
    arch_y = h - arch_h - 2
    pygame.draw.ellipse(surf, CAVE_DARK, (arch_x, arch_y, arch_w, arch_h))
    pygame.draw.ellipse(surf, CAVE_MID,  (arch_x, arch_y, arch_w, arch_h), 3)
    # Grass fringe
    pygame.draw.rect(surf, GRASS_GREEN, (0, h - 10, w, 10))
    return surf


def make_rope_surf(length: int, angle_deg: float = 0) -> pygame.Surface:
    """Straight rope segment."""
    rad = math.radians(angle_deg)
    dx = int(abs(math.cos(rad) * length))
    dy = int(abs(math.sin(rad) * length))
    surf = pygame.Surface((max(dx, 6), max(dy, 6)), pygame.SRCALPHA)
    end = (dx - 1, dy - 1)
    pygame.draw.line(surf, ROPE_COLOR, (0, 0), end, 4)
    pygame.draw.line(surf, lighten(ROPE_COLOR, 30), (0, 0), end, 1)
    return surf


def make_player_surf(w: int, h: int, facing: int = 1,
                     frame: int = 0, state: str = "idle") -> pygame.Surface:
    """
    Draws a cartoon character.
    facing: 1 = right, -1 = left
    state: 'idle', 'run', 'jump', 'fall', 'climb'
    """
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # ── body proportions
    head_r  = w // 3
    body_h  = h * 2 // 5
    leg_h   = h // 4
    arm_h   = body_h * 2 // 3

    head_cy = head_r + 2
    body_y  = head_cy + head_r
    body_x  = cx - w // 4
    body_w  = w // 2

    # ── leg animation
    run_offsets = [(0, 0), (4, -4), (0, 0), (-4, -4)]
    if state == "run":
        lo, ro = run_offsets[frame % 4][0], -run_offsets[frame % 4][0]
    elif state in ("jump", "fall"):
        lo, ro = -8, 8
    elif state == "climb":
        lo, ro = run_offsets[frame % 4][0], -run_offsets[frame % 4][0]
    else:
        lo = ro = 0

    # Legs
    leg_w = 8
    lx = cx - leg_w - 2
    rx = cx + 2
    pygame.draw.rect(surf, (60, 40, 20),
                     (lx + lo, body_y + body_h - 4, leg_w, leg_h + 4), border_radius=3)
    pygame.draw.rect(surf, (60, 40, 20),
                     (rx + ro, body_y + body_h - 4, leg_w, leg_h + 4), border_radius=3)
    # Boots
    boot_col = (80, 55, 25)
    pygame.draw.rect(surf, boot_col,
                     (lx + lo - 2, body_y + body_h + leg_h - 2, leg_w + 4, 6), border_radius=2)
    pygame.draw.rect(surf, boot_col,
                     (rx + ro - 2, body_y + body_h + leg_h - 2, leg_w + 4, 6), border_radius=2)

    # Body / shirt
    shirt_col = (220, 80, 50)   # red shirt
    pygame.draw.rect(surf, shirt_col,
                     (body_x, body_y, body_w, body_h), border_radius=5)
    pygame.draw.rect(surf, darken(shirt_col, 40),
                     (body_x, body_y, body_w, body_h), 2, border_radius=5)

    # Arms
    arm_col = (240, 195, 140)
    if state == "climb":
        # One arm up
        arm_y = body_y + (0 if frame % 2 == 0 else arm_h // 2)
        pygame.draw.rect(surf, arm_col,
                         (body_x - 6, arm_y, 6, arm_h), border_radius=3)
        pygame.draw.rect(surf, arm_col,
                         (body_x + body_w, body_y + arm_h // 2, 6, arm_h), border_radius=3)
    else:
        pygame.draw.rect(surf, arm_col,
                         (body_x - 6, body_y + 4, 6, arm_h), border_radius=3)
        pygame.draw.rect(surf, arm_col,
                         (body_x + body_w, body_y + 4, 6, arm_h), border_radius=3)

    # Head
    skin = (240, 195, 140)
    pygame.draw.circle(surf, skin, (cx, head_cy), head_r)
    pygame.draw.circle(surf, darken(skin, 20), (cx, head_cy), head_r, 2)

    # Hair
    hair_col = (80, 50, 20)
    pygame.draw.ellipse(surf, hair_col,
                        (cx - head_r, head_cy - head_r, head_r * 2, head_r))

    # Eyes
    eye_x_off = 5 * facing
    eye_y = head_cy - 2
    white_r = 4
    pupil_r = 2
    pygame.draw.circle(surf, WHITE, (cx + eye_x_off, eye_y), white_r)
    pygame.draw.circle(surf, (30, 30, 150), (cx + eye_x_off + facing, eye_y), pupil_r)

    # Mouth – smile or 'O' on jump
    if state in ("jump", "fall"):
        pygame.draw.circle(surf, (160, 60, 40), (cx + eye_x_off, head_cy + 6), 3)
    else:
        pygame.draw.arc(surf, (160, 60, 40),
                        (cx + eye_x_off - 5, head_cy + 3, 10, 6),
                        math.pi, 0, 2)

    # Scarf / collar
    pygame.draw.rect(surf, (250, 200, 50),
                     (body_x, body_y, body_w, 6), border_radius=3)

    return surf


def make_mushroom_surf(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    # Stalk
    stalk_w = w // 3
    pygame.draw.rect(surf, (220, 210, 190),
                     (cx - stalk_w // 2, h // 2, stalk_w, h // 2), border_radius=3)
    # Cap
    cap_col = (210, 50, 50)
    pygame.draw.ellipse(surf, cap_col, (0, 0, w, h * 2 // 3))
    # White dots
    for dx, dy in [(-w // 5, h // 6), (w // 5, h // 8), (0, h // 3)]:
        pygame.draw.circle(surf, WHITE, (cx + dx, dy), w // 8)
    return surf
