# Island Hopper – Arcade Platformer

A complete 2D side-scrolling arcade platformer built entirely in Python with Pygame.
Inspired by classic cartoon platformer level designs with floating islands, wooden
structures, ropes, coins, keys, and a treasure chest goal.

## Requirements

- Python 3.10 or later (tested on 3.13)
- pygame-ce (Community Edition) >= 2.4.0

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| A / Left Arrow | Move left |
| D / Right Arrow | Move right |
| W / Up Arrow / Space | Jump |
| W / Up Arrow | Climb ladder (when touching) |
| S / Down Arrow | Descend ladder |
| P | Pause / Resume |
| R | Restart level |
| ESC | Back to main menu |

## Objective

1. Collect gold coins scattered across the world
2. Find and grab the **golden Key** on one of the floating islands
3. Use the key to open the **Treasure Chest** on the highest island
4. Opening the chest wins the level!

A **star rating** (1–3 stars) is awarded based on the percentage of coins collected.

## Project Structure

```
IslandHopper/
├── main.py        – Game loop, state machine, rendering pipeline
├── player.py      – Player physics, animation, state machine
├── level.py       – Level 1 data: platforms, islands, coins, etc.
├── camera.py      – Smooth-follow camera with clamping
├── ui.py          – HUD, main menu, pause, win, death screens
├── particles.py   – Particle system (coin sparkles, dust, etc.)
├── draw_utils.py  – All procedural graphics (no external images)
├── settings.py    – Global constants and configuration
└── requirements.txt
```

## Adding New Levels

To add a second level, create a `build_level_2()` function in `level.py`
following the same pattern as `build_level_1()`, then update `main.py` to
select the active level based on the current level index.

## Features

- Smooth camera with lerp following and edge clamping
- Coyote time + jump buffering for responsive controls
- Particle effects on coin collection and checkpoint
- Animated spinning coins with bob effect
- Parallax mountain background
- Animated drifting clouds
- Mini-map HUD element
- Star rating on victory screen
- Procedural graphics — no external image assets required
