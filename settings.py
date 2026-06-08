"""
settings.py - Global constants and configuration for Island Hopper platformer.
"""

# --- Screen ---
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "Island Hopper – Arcade Platformer"

# --- Physics ---
GRAVITY          = 0.55
MAX_FALL_SPEED   = 18
PLAYER_SPEED     = 4.5
PLAYER_JUMP      = -13.5
LADDER_SPEED     = 3.5

# --- Tile / World ---
TILE_SIZE  = 48            # pixels per tile
WORLD_W    = 5000          # total world width  (pixels)
WORLD_H    = 1800          # total world height (pixels)

# --- Colors  (R, G, B) ---
SKY_TOP      = (102, 191, 255)
SKY_BOT      = (178, 228, 255)
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
TRANSPARENT  = (0,   0,   0, 0)

GRASS_GREEN  = (86,  175, 46)
GRASS_DARK   = (62,  130, 27)
DIRT_BROWN   = (139, 90,  43)
DIRT_DARK    = (101, 63,  27)
STONE_GRAY   = (140, 140, 135)
STONE_DARK   = (100, 100, 95)

WOOD_LIGHT   = (205, 155, 75)
WOOD_DARK    = (160, 110, 45)
ROPE_COLOR   = (160, 120, 60)

COIN_YELLOW  = (255, 215, 0)
COIN_DARK    = (218, 165, 32)
KEY_GOLD     = (255, 200, 50)
CHEST_BROWN  = (120, 70,  20)
CHEST_GOLD   = (255, 180, 0)
FLAG_RED     = (220, 50,  50)
FLAG_WHITE   = (240, 240, 240)

CAVE_DARK    = (40,  30,  20)
CAVE_MID     = (70,  55,  35)

CLOUD_WHITE  = (240, 248, 255)
MTN_BLUE     = (170, 195, 220)
MTN_DARK     = (130, 155, 180)

UI_BG        = (20,  20,  40, 210)
UI_BORDER    = (255, 215,  0)
UI_TEXT      = (255, 240, 180)
UI_SHADOW    = (0,   0,   0)

PARTICLE_COLORS = [
    (255, 215, 0),
    (255, 180, 0),
    (255, 240, 100),
    (255, 255, 150),
]

# --- Z-Layers (draw order) ---
LAYER_BG       = 0
LAYER_DECO     = 1
LAYER_PLATFORM = 2
LAYER_ROPE     = 3
LAYER_LADDER   = 4
LAYER_ITEMS    = 5
LAYER_PLAYER   = 6
LAYER_PARTICLE = 7
LAYER_UI       = 8
