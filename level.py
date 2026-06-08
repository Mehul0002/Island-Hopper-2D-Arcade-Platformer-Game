"""
level.py – Level data, tile map, collectibles, and all world objects.

Level layout mirrors the reference image:
  • Wide ground section with hill / cave on the right
  • Tall wooden crane/tower in the centre-left area
  • Multiple floating grass islands at various heights
  • Ropes connecting platforms
  • Ladders on the tower and some islands
  • Coins scattered across the world
  • Key on a mid-right island
  • Treasure chest on the upper-right island (goal)
  • Checkpoint flag near the cave
  • Wooden crates stacked on ground and platforms
"""

import math
import pygame
from settings import *
from draw_utils import (
    make_grass_tile, make_dirt_tile, make_island_surface,
    make_coin_surf, make_key_surf, make_chest_surf,
    make_crate_surf, make_ladder_surf, make_flag_surf,
    make_cave_surf, make_mushroom_surf,
)


# ──────────────────────────────────────────────────────────────────────────────
# Sprite base classes
# ──────────────────────────────────────────────────────────────────────────────

class Tile(pygame.sprite.Sprite):
    """Static solid tile."""

    def __init__(self, x: int, y: int, surf: pygame.Surface):
        super().__init__()
        self.image = surf
        self.rect  = surf.get_rect(topleft=(x, y))


class Island(pygame.sprite.Sprite):
    """Floating grass island – solid on top."""

    def __init__(self, x: int, y: int, w_tiles: int):
        super().__init__()
        self.image = make_island_surface(w_tiles, TILE_SIZE)
        self.rect  = self.image.get_rect(topleft=(x, y))
        # Collision: only the top portion of the island counts
        grass_h = TILE_SIZE // 3
        self.collision_rect = pygame.Rect(x, y, w_tiles * TILE_SIZE, grass_h + 6)

    def draw_shadow(self, surf: pygame.Surface, cam_ox: float, cam_oy: float):
        sx = self.rect.x - int(cam_ox)
        sy = self.rect.y - int(cam_oy)
        shad = pygame.Surface((self.rect.width, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 0, 0, 45),
                            (0, 0, self.rect.width, 14))
        surf.blit(shad, (sx, sy + self.rect.height + 4))


class Rope(pygame.sprite.Sprite):
    """Visual-only decorative rope between two world points."""

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        super().__init__()
        self.p1 = (x1, y1)
        self.p2 = (x2, y2)

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        # Catenary-style rope drawn as multiple line segments
        sx1 = self.p1[0] - int(cam_ox)
        sy1 = self.p1[1] - int(cam_oy)
        sx2 = self.p2[0] - int(cam_ox)
        sy2 = self.p2[1] - int(cam_oy)
        segs = 20
        sag  = 40   # maximum sag at centre
        pts  = []
        for i in range(segs + 1):
            t  = i / segs
            x  = sx1 + (sx2 - sx1) * t
            y  = sy1 + (sy2 - sy1) * t + sag * math.sin(t * math.pi)
            pts.append((x, y))
        if len(pts) > 1:
            pygame.draw.lines(surf, ROPE_COLOR, False, pts, 3)
            pygame.draw.lines(surf, (200, 165, 100), False, pts, 1)


class Coin(pygame.sprite.Sprite):
    """Collectible coin with idle bob animation."""

    _SURF = None
    _RAD  = 14

    def __init__(self, x: int, y: int):
        super().__init__()
        if Coin._SURF is None:
            Coin._SURF = make_coin_surf(Coin._RAD)
        self.base_y    = float(y)
        self._timer    = 0
        self._bob_amp  = 5
        self._bob_spd  = 0.04
        self.image     = Coin._SURF
        self.rect      = self.image.get_rect(center=(x, y))
        self.collected = False

    def update(self, dt_ms: int) -> None:
        self._timer += dt_ms * 0.001
        self.rect.centery = int(self.base_y + math.sin(self._timer * 3) * self._bob_amp)

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        sx = self.rect.x - int(cam_ox)
        sy = self.rect.y - int(cam_oy)
        # Spin by scaling x
        scale = abs(math.cos(self._timer * 3))
        w = max(2, int(self._SURF.get_width() * scale))
        h = self._SURF.get_height()
        scaled = pygame.transform.scale(self._SURF, (w, h))
        surf.blit(scaled, (sx + (self._SURF.get_width() - w) // 2, sy))


class Key(pygame.sprite.Sprite):
    """Collectible key."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image     = make_key_surf(32)
        self.rect      = self.image.get_rect(center=(x, y))
        self.base_y    = float(y)
        self._timer    = 0
        self.collected = False

    def update(self, dt_ms: int) -> None:
        self._timer += dt_ms * 0.001
        self.rect.centery = int(self.base_y + math.sin(self._timer * 2.5) * 6)


class Chest(pygame.sprite.Sprite):
    """Treasure chest – goal item (requires key)."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self._surf_closed = make_chest_surf(52, 40, open_=False)
        self._surf_open   = make_chest_surf(52, 40, open_=True)
        self.image        = self._surf_closed
        self.rect         = self.image.get_rect(bottomleft=(x, y))
        self.opened       = False
        self._open_timer  = 0
        self._anim_done   = False

    def open(self) -> None:
        if not self.opened:
            self.opened = True
            self.image  = self._surf_open

    def update(self, dt_ms: int) -> None:
        if self.opened and not self._anim_done:
            self._open_timer += dt_ms
            if self._open_timer > 500:
                self._anim_done = True


class Flag(pygame.sprite.Sprite):
    """Checkpoint flag."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self._pole_h   = 64
        self.image     = make_flag_surf(self._pole_h)
        self.rect      = self.image.get_rect(midbottom=(x, y))
        self.reached   = False
        self._wave     = 0.0

    def update(self, dt_ms: int) -> None:
        self._wave += dt_ms * 0.003


class Crate(pygame.sprite.Sprite):
    """Solid wooden crate obstacle."""

    def __init__(self, x: int, y: int, size: int = TILE_SIZE):
        super().__init__()
        self.image = make_crate_surf(size)
        self.rect  = self.image.get_rect(topleft=(x, y))


class Mushroom(pygame.sprite.Sprite):
    """Purely decorative mushroom."""

    def __init__(self, x: int, y: int, size: int = 28):
        super().__init__()
        self.image = make_mushroom_surf(size, size + 8)
        self.rect  = self.image.get_rect(midbottom=(x, y))


# ──────────────────────────────────────────────────────────────────────────────
# Cloud  (animated background element)
# ──────────────────────────────────────────────────────────────────────────────

class Cloud:
    """Drifting animated cloud."""

    def __init__(self, x: float, y: float, w: int, h: int, speed: float):
        from draw_utils import make_cloud_surf
        self.surf  = make_cloud_surf(w, h)
        self.x     = x
        self.y     = y
        self.speed = speed
        self.alpha = 210
        self.surf.set_alpha(self.alpha)

    def update(self) -> None:
        self.x += self.speed
        if self.x > WORLD_W + 200:
            self.x = -self.surf.get_width() - 50

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        # Parallax factor
        px = self.x - cam_ox * 0.25
        py = self.y - cam_oy * 0.05
        surf.blit(self.surf, (int(px), int(py)))


# ──────────────────────────────────────────────────────────────────────────────
# Level 1 data
# ──────────────────────────────────────────────────────────────────────────────

def _build_ground_tiles():
    """Wide ground platform from x=0 to x≈2200."""
    tiles = []
    T = TILE_SIZE
    grass_surf = make_grass_tile(T)
    dirt_surf  = make_dirt_tile(T)

    ground_y = WORLD_H - 4 * T   # y of the ground surface row

    # Ground rows: 1 grass + 3 dirt rows wide
    for col in range(50):   # 50 tiles wide
        x = col * T
        tiles.append(Tile(x, ground_y,       grass_surf))
        tiles.append(Tile(x, ground_y + T,   dirt_surf))
        tiles.append(Tile(x, ground_y + 2*T, dirt_surf))
        tiles.append(Tile(x, ground_y + 3*T, dirt_surf))

    # Raised section ground (under crane, cols 14-26)
    raise_y = ground_y - T
    for col in range(14, 27):
        x = col * T
        tiles.append(Tile(x, raise_y,     grass_surf))
        tiles.append(Tile(x, raise_y + T, dirt_surf))

    return tiles, ground_y


def build_level_1():
    """
    Construct and return all level objects for level 1.
    Returns a dict with all sprite groups and lists.
    """
    T = TILE_SIZE

    tiles, ground_y = _build_ground_tiles()
    tile_group = pygame.sprite.Group(*tiles)

    # ── Islands (floating)
    islands = [
        # (x, y, width_in_tiles)
        Island(  80,  ground_y - 260, 4),   # left low island
        Island( 280,  ground_y - 420, 5),   # left mid island  (star/gem)
        Island( 600,  ground_y - 540, 6),   # upper-left island (mushrooms, sign)
        Island( 950,  ground_y - 380, 5),   # centre-left island (coins, sign)
        Island(1300,  ground_y - 310, 4),   # centre island
        Island(1560,  ground_y - 480, 5),   # upper-centre island
        Island(1950,  ground_y - 350, 4),   # right-of-centre island (flag)
        Island(2150,  ground_y - 500, 3),   # upper right-centre island
        Island(2380,  ground_y - 280, 5),   # right island (key, fence)
        Island(2650,  ground_y - 450, 4),   # far right mid island (treasure + palm)
        Island(2900,  ground_y - 600, 3),   # topmost right island
    ]
    island_group = pygame.sprite.Group(*islands)

    # For collision use collision_rect
    platform_rects = [isl.collision_rect for isl in islands]

    # Solid tile sprites for collision (wrap ground tiles + crate bodies)
    all_solid = pygame.sprite.Group(*tiles)

    # ── Crates  (act as solid)
    crates = [
        Crate(1720, ground_y - T,          T),
        Crate(1720, ground_y - 2*T,        T),
        Crate(1768, ground_y - T,          T),
        Crate(1320, ground_y - T - 12, 36),
        Crate(1350, ground_y - T - 45, 36),
        # On raised section near cave
        Crate(2060, ground_y - T,          T),
        Crate(2060, ground_y - 2*T,        T),
        Crate(2108, ground_y - T,          T),
    ]
    crate_group = pygame.sprite.Group(*crates)
    all_solid.add(*crates)

    # ── Ladders (list of Rects + rendered surfaces)
    ladder_defs = [
        # (world_x, world_y, width, height)
        (820,  ground_y - 260, 36, 260),    # tower left rail
        (950,  ground_y - 300, 36, 300),    # tower right rail
        (890,  ground_y - 500, 36, 220),    # tower upper section
        (2380, ground_y - 280, 36, 280),    # right island access
        (2650, ground_y - 450, 36, 450),    # far right access
        (2150, ground_y - 500, 36, 220),    # upper right-centre
    ]
    ladders_rects   = []
    ladders_surfs   = []   # (surf, rect)
    for lx, ly, lw, lh in ladder_defs:
        s = make_ladder_surf(lw, lh)
        r = pygame.Rect(lx, ly, lw, lh)
        ladders_rects.append(r)
        ladders_surfs.append((s, r))

    # ── Ropes (decorative catenary lines)
    ropes = [
        Rope(240, ground_y - 380, 600, ground_y - 480),
        Rope(600, ground_y - 480, 1000, ground_y - 340),
        Rope(1000, ground_y - 340, 1300, ground_y - 260),
        Rope(1560, ground_y - 430, 1950, ground_y - 310),
        Rope(1950, ground_y - 310, 2380, ground_y - 240),
        Rope(2380, ground_y - 240, 2650, ground_y - 410),
        Rope(2650, ground_y - 400, 2900, ground_y - 560),
        # Crane cross ropes
        Rope(800, ground_y - 520, 1000, ground_y - 320),
        Rope(820, ground_y - 480, 1000, ground_y - 200),
    ]

    # ── Coins
    coin_positions = [
        # Ground level trail
        (200, ground_y - 60), (248, ground_y - 60), (296, ground_y - 60),
        # Left island
        (130, ground_y - 320), (178, ground_y - 320),
        # Mid-left island
        (340, ground_y - 480), (388, ground_y - 480), (436, ground_y - 480),
        # Upper-left island
        (640, ground_y - 600), (688, ground_y - 600),
        # Centre island arc
        (980, ground_y - 440), (1020, ground_y - 480),
        (1060, ground_y - 510), (1100, ground_y - 480), (1140, ground_y - 440),
        # Crate-area
        (1370, ground_y - 120), (1410, ground_y - 120),
        # Upper-centre island
        (1600, ground_y - 550), (1648, ground_y - 550), (1696, ground_y - 550),
        # Crane arc coins
        (870, ground_y - 350), (900, ground_y - 300), (930, ground_y - 260),
        # Right section
        (2000, ground_y - 400), (2050, ground_y - 400),
        (2200, ground_y - 560), (2248, ground_y - 560),
        (2400, ground_y - 340), (2448, ground_y - 340), (2496, ground_y - 340),
        # Far right island coins
        (2700, ground_y - 510), (2748, ground_y - 510),
        (2940, ground_y - 660), (2988, ground_y - 660),
    ]
    coins = [Coin(x, y) for x, y in coin_positions]
    coin_group = pygame.sprite.Group(*coins)

    # ── Key
    key_obj  = Key(2490, ground_y - 340)

    # ── Chest (on topmost right island)
    chest_obj = Chest(2950, ground_y - 600 - TILE_SIZE * 2 // 3 + 4)

    # ── Checkpoint flag
    flag_obj = Flag(2100, ground_y)

    # ── Cave / exit
    cave_surf = make_cave_surf(120, 100)
    cave_rect = cave_surf.get_rect(midbottom=(2200, ground_y))
    cave_data = (cave_surf, cave_rect)

    # ── Mushrooms (decorative)
    mushrooms = [
        Mushroom( 650, ground_y - 4*T//3 + T//3 + 2, 28),
        Mushroom( 670, ground_y - 4*T//3 + T//3 + 2, 20),
        Mushroom(1640, ground_y - 480 - TILE_SIZE*2//3 + TILE_SIZE//3, 28),
        Mushroom(1660, ground_y - 480 - TILE_SIZE*2//3 + TILE_SIZE//3, 20),
    ]

    # ── Clouds
    import random
    random.seed(42)
    clouds = []
    for _ in range(18):
        cx   = random.randint(-200, WORLD_W)
        cy   = random.randint(30, SCREEN_HEIGHT // 2)
        cw   = random.randint(100, 220)
        ch   = random.randint(50, 90)
        spd  = random.uniform(0.15, 0.55)
        clouds.append(Cloud(cx, cy, cw, ch, spd))

    # ── Player spawn
    spawn = (80, ground_y - 4 * T - 60)

    return {
        "tile_group":    tile_group,
        "all_solid":     all_solid,
        "islands":       islands,
        "island_group":  island_group,
        "platform_rects": platform_rects,
        "crates":        crates,
        "crate_group":   crate_group,
        "ladders_rects": ladders_rects,
        "ladders_surfs": ladders_surfs,
        "ropes":         ropes,
        "coins":         coins,
        "coin_group":    coin_group,
        "key":           key_obj,
        "chest":         chest_obj,
        "flag":          flag_obj,
        "cave":          cave_data,
        "mushrooms":     mushrooms,
        "clouds":        clouds,
        "spawn":         spawn,
        "ground_y":      ground_y,
        "total_coins":   len(coins),
    }
