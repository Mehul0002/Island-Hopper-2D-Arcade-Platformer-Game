# -*- coding: utf-8 -*-
"""
main.py - Island Hopper entry point and main game loop.

Run:
    python main.py

Controls:
    A / Left  : Move left
    D / Right : Move right
    W / Up / Space : Jump  (also start climbing ladder)
    S / Down  : Descend ladder
    P         : Pause / Resume
    R         : Restart level
    ESC       : Back to main menu
"""

import sys
import math
import pygame

from settings import *
from camera   import Camera
from player   import Player
from level    import build_level_1
from particles import ParticleSystem
from ui       import (MainMenu, PauseMenu, WinScreen, DeathScreen,
                      draw_hud, get_font, draw_text_shadow)
from draw_utils import draw_sky_gradient, draw_mountains


# ======================================================================
# Game States
# ======================================================================

STATE_MENU  = "menu"
STATE_PLAY  = "play"
STATE_PAUSE = "pause"
STATE_WIN   = "win"
STATE_DEAD  = "dead"


# ======================================================================
# Background renderer
# ======================================================================

class Background:
    """Draws sky gradient, parallax mountains, and animated clouds."""

    def __init__(self):
        self._sky_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        draw_sky_gradient(self._sky_surf, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw(self, surf, cam_ox, cam_oy, clouds):
        surf.blit(self._sky_surf, (0, 0))
        draw_mountains(surf, cam_ox, SCREEN_WIDTH, SCREEN_HEIGHT)
        for cloud in clouds:
            cloud.draw(surf, cam_ox, cam_oy)


# ======================================================================
# Main Game class
# ======================================================================

class Game:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock  = pygame.time.Clock()

        # UI screens
        self.main_menu    = MainMenu()
        self.pause_menu   = PauseMenu()
        self.win_screen   = WinScreen()
        self.death_screen = DeathScreen()

        self.state = STATE_MENU

        # Particle system (shared by player)
        self.particles = ParticleSystem()

        # Level data (loaded on play)
        self.level_data: dict = {}

        # Player (created on first load)
        self.player: Player = None

        # Camera
        self.camera = Camera()

        # Background
        self.bg = Background()

        # Game timer
        self.elapsed_ms = 0
        self._anim_t    = 0.0   # continuous time for animations

    # ------------------------------------------------------------------
    # Level loading / reset
    # ------------------------------------------------------------------

    def _load_level(self):
        """Build / rebuild the level and reset the player."""
        self.level_data = build_level_1()
        spawn = self.level_data["spawn"]

        if self.player is None:
            self.player = Player(spawn[0], spawn[1], self.particles)
        else:
            self.player.reset(spawn[0], spawn[1])

        self.particles.clear()
        self.elapsed_ms = 0

        # Reset all collectibles
        for coin in self.level_data["coins"]:
            coin.collected = False
        self.level_data["key"].collected   = False
        self.level_data["chest"].opened    = False
        self.level_data["flag"].reached    = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while True:
            dt_ms = self.clock.tick(FPS)
            dt_ms = min(dt_ms, 50)  # clamp to avoid spiral of death

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self._handle_event(event)

            self._update(dt_ms)
            self._draw()
            pygame.display.flip()

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _handle_event(self, event):
        if self.state == STATE_PLAY:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.state = STATE_PAUSE
                elif event.key == pygame.K_r:
                    self._load_level()
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU

        elif self.state == STATE_PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self.state = STATE_PLAY
                elif event.key == pygame.K_r:
                    self._load_level()
                    self.state = STATE_PLAY

        elif self.state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._load_level()
                    self.state = STATE_PLAY

        elif self.state == STATE_WIN:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._load_level()
                    self.state = STATE_PLAY
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU

        elif self.state == STATE_DEAD:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._load_level()
                    self.state = STATE_PLAY
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU

        # Mouse clicks on any screen
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        """Dispatch mouse clicks to the appropriate menu."""
        # We redraw to a temp surface to obtain button rects
        tmp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.state == STATE_MENU:
            btns = self.main_menu.draw(tmp, pos)
            if btns["play"].collidepoint(pos):
                self._load_level()
                self.state = STATE_PLAY
            elif btns["quit"].collidepoint(pos):
                pygame.quit()
                sys.exit()

        elif self.state == STATE_PAUSE:
            btns = self.pause_menu.draw(tmp, pos)
            if btns["resume"].collidepoint(pos):
                self.state = STATE_PLAY
            elif btns["restart"].collidepoint(pos):
                self._load_level()
                self.state = STATE_PLAY
            elif btns["menu"].collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_WIN:
            btns = self.win_screen.draw(
                tmp,
                self.player.coins,
                self.level_data["total_coins"],
                self.elapsed_ms / 1000,
                pos,
            )
            if btns["restart"].collidepoint(pos):
                self._load_level()
                self.state = STATE_PLAY
            elif btns["menu"].collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_DEAD:
            btns = self.death_screen.draw(tmp, pos)
            if btns["retry"].collidepoint(pos):
                self._load_level()
                self.state = STATE_PLAY
            elif btns["menu"].collidepoint(pos):
                self.state = STATE_MENU

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt_ms):
        self._anim_t += dt_ms * 0.001

        if self.state == STATE_MENU:
            self.main_menu.update(dt_ms)

        elif self.state == STATE_WIN:
            self.win_screen.update(dt_ms)

        elif self.state == STATE_DEAD:
            self.death_screen.update(dt_ms)

        elif self.state == STATE_PLAY and self.level_data:
            self.elapsed_ms += dt_ms
            ld   = self.level_data
            keys = pygame.key.get_pressed()

            # --- Build combined collision group for this frame ---
            # We need: ground tiles, crates, AND island top surfaces.
            # Island top-surface sprites are created on-the-fly each frame
            # (cheap since there are only ~11 islands).
            class _ColSprite(pygame.sprite.Sprite):
                """Minimal sprite that only wraps a Rect for collision."""
                def __init__(self, r):
                    super().__init__()
                    self.rect = r

            island_col = pygame.sprite.Group(
                *[_ColSprite(r) for r in ld["platform_rects"]]
            )
            combined_solid = pygame.sprite.Group(
                *ld["all_solid"].sprites(),
                *island_col.sprites(),
            )

            # Update player
            self.player.update(keys, combined_solid,
                               ld["ladders_rects"], dt_ms)

            # Camera follow
            self.camera.update(self.player.rect)

            # Coin collection
            for coin in ld["coins"]:
                if not coin.collected:
                    coin.update(dt_ms)
                    if self.player.rect.colliderect(coin.rect):
                        coin.collected = True
                        self.player.collect_coin()

            # Key collection
            key = ld["key"]
            if not key.collected:
                key.update(dt_ms)
                if self.player.rect.colliderect(key.rect):
                    key.collected = True
                    self.player.collect_key()

            # Chest interaction (requires key)
            chest = ld["chest"]
            chest.update(dt_ms)
            if not chest.opened and self.player.has_key:
                if self.player.rect.colliderect(chest.rect):
                    chest.open()
                    self.player.collect_chest()

            # Checkpoint flag
            flag = ld["flag"]
            flag.update(dt_ms)
            if not flag.reached and self.player.rect.colliderect(flag.rect):
                flag.reached = True
                self.particles.emit_sparkle(
                    flag.rect.centerx, flag.rect.top,
                    color=FLAG_RED, count=20)

            # Clouds drift
            for cloud in ld["clouds"]:
                cloud.update()

            # Particles
            self.particles.update()

            # State transitions
            if self.player.level_done:
                self.state = STATE_WIN
            elif self.player.dead:
                self.state = STATE_DEAD

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        surf  = self.screen
        mouse = pygame.mouse.get_pos()

        if self.state == STATE_MENU:
            self.main_menu.draw(surf, mouse)
            return

        # Always draw world for play / pause / win / dead
        if self.level_data:
            self._draw_world(surf)

        if self.state == STATE_PAUSE:
            self.pause_menu.draw(surf, mouse)
        elif self.state == STATE_WIN:
            self.win_screen.draw(
                surf,
                self.player.coins,
                self.level_data["total_coins"],
                self.elapsed_ms / 1000,
                mouse,
            )
        elif self.state == STATE_DEAD:
            self.death_screen.draw(surf, mouse)

    def _draw_world(self, surf):
        cam    = self.camera
        ld     = self.level_data
        cam_ox = cam.offset_x
        cam_oy = cam.offset_y
        vis    = cam.world_rect
        scr_r  = surf.get_rect()

        # 1. Sky background + clouds
        self.bg.draw(surf, cam_ox, cam_oy, ld["clouds"])

        # 2. Island shadows
        for isl in ld["islands"]:
            if vis.colliderect(isl.rect):
                isl.draw_shadow(surf, cam_ox, cam_oy)

        # 3. Ground tiles
        for tile in ld["tile_group"]:
            sr = cam.apply(tile.rect)
            if scr_r.colliderect(sr):
                surf.blit(tile.image, sr)

        # 4. Ropes (behind platforms)
        for rope in ld["ropes"]:
            rope.draw(surf, cam_ox, cam_oy)

        # 5. Ladders
        for lsurf, lrect in ld["ladders_surfs"]:
            sr = cam.apply(lrect)
            if scr_r.colliderect(sr):
                surf.blit(lsurf, sr)

        # 6. Islands
        for isl in ld["islands"]:
            sr = cam.apply(isl.rect)
            if scr_r.colliderect(sr):
                surf.blit(isl.image, sr)

        # 7. Crates
        for crate in ld["crates"]:
            sr = cam.apply(crate.rect)
            if scr_r.colliderect(sr):
                surf.blit(crate.image, sr)

        # 8. Decorative mushrooms
        for mush in ld["mushrooms"]:
            sr = cam.apply(mush.rect)
            if scr_r.colliderect(sr):
                surf.blit(mush.image, sr)

        # 9. Cave
        cave_surf, cave_rect = ld["cave"]
        sr = cam.apply(cave_rect)
        if scr_r.colliderect(sr):
            surf.blit(cave_surf, sr)

        # 10. Checkpoint flag
        flag = ld["flag"]
        sr   = cam.apply(flag.rect)
        if scr_r.colliderect(sr):
            surf.blit(flag.image, sr)
            if flag.reached:
                glow = pygame.Surface(flag.image.get_size(), pygame.SRCALPHA)
                a    = int(60 + 50 * math.sin(flag._wave * 6))
                glow.fill((255, 255, 80, a))
                surf.blit(glow, sr, special_flags=pygame.BLEND_RGBA_ADD)

        # 11. Coins
        for coin in ld["coins"]:
            if not coin.collected:
                coin.draw(surf, cam_ox, cam_oy)

        # 12. Key
        key = ld["key"]
        if not key.collected:
            sr = cam.apply(key.rect)
            if scr_r.colliderect(sr):
                surf.blit(key.image, sr)

        # 13. Chest
        chest = ld["chest"]
        sr    = cam.apply(chest.rect)
        if scr_r.colliderect(sr):
            surf.blit(chest.image, sr)
            # Show prompt when player has key and is near chest
            if not chest.opened and self.player.has_key:
                if abs(chest.rect.centerx - self.player.rect.centerx) < 200:
                    pf = get_font(18, bold=True)
                    pulse = int(200 + 55 * math.sin(self._anim_t * 4))
                    prm   = pf.render("Press UP to Open!", True,
                                      (pulse, pulse, 50))
                    surf.blit(prm, (sr.centerx - prm.get_width() // 2,
                                    sr.top - 30))

        # 14. Particles
        self.particles.draw(surf, cam_ox, cam_oy)

        # 15. Player
        self.player.draw(surf, cam_ox, cam_oy)

        # 16. HUD overlay
        draw_hud(
            surf,
            self.player.coins,
            ld["total_coins"],
            self.player.has_key,
            self.state == STATE_PAUSE,
            self.player.level_done,
            self.elapsed_ms / 1000,
        )

        # 17. Mini-map
        self._draw_minimap(surf)

    def _draw_minimap(self, surf):
        """Small mini-map showing player position relative to the world."""
        mw, mh = 160, 40
        mx = SCREEN_WIDTH  - mw - 10
        my = SCREEN_HEIGHT - mh - 32

        mm = pygame.Surface((mw, mh), pygame.SRCALPHA)
        mm.fill((10, 10, 30, 170))
        pygame.draw.rect(mm, COIN_YELLOW, (0, 0, mw, mh), 2, border_radius=4)

        # Islands on mini-map (green lines)
        for isl in self.level_data["islands"]:
            ix  = int(isl.rect.x / WORLD_W * mw)
            iy  = int(isl.rect.y / WORLD_H * mh)
            iw2 = max(3, int(isl.rect.width / WORLD_W * mw))
            pygame.draw.rect(mm, GRASS_GREEN, (ix, iy, iw2, 2))

        # Ground line
        gy = int(self.level_data["ground_y"] / WORLD_H * mh)
        pygame.draw.line(mm, DIRT_BROWN, (0, gy), (mw, gy), 2)

        # Player dot
        px_r = self.player.pos.x / WORLD_W
        py_r = self.player.pos.y / WORLD_H
        dx   = int(px_r * mw)
        dy   = int(py_r * mh)
        pygame.draw.circle(mm, (255, 80, 80), (dx, dy), 3)

        surf.blit(mm, (mx, my))

        lbl = get_font(13).render("MAP", True, (180, 180, 220))
        surf.blit(lbl, (mx + 4, my - 16))


# ======================================================================
# Entry point
# ======================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
