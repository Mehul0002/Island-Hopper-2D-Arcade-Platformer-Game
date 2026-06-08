"""
camera.py – Smooth-follow camera that clamps to world bounds.
"""

import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_W, WORLD_H


class Camera:
    """
    Translates all game objects so the player is centred on screen.
    Supports smooth lerp-follow and edge clamping.
    """

    def __init__(self):
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        # Lerp speed – lower = smoother lag, higher = snappier
        self.lerp_x = 0.10
        self.lerp_y = 0.10

    # ------------------------------------------------------------------
    def update(self, target: pygame.Rect) -> None:
        """Move camera so *target* stays centred."""
        # Desired offset so the target centre sits at screen centre
        desired_x = target.centerx - SCREEN_WIDTH  // 2
        desired_y = target.centery - SCREEN_HEIGHT // 2

        # Smooth lerp
        self.offset_x += (desired_x - self.offset_x) * self.lerp_x
        self.offset_y += (desired_y - self.offset_y) * self.lerp_y

        # Clamp to world bounds
        self.offset_x = max(0, min(self.offset_x, WORLD_W - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, WORLD_H - SCREEN_HEIGHT))

    # ------------------------------------------------------------------
    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Return a screen-space Rect for a world-space Rect."""
        return pygame.Rect(
            rect.x - int(self.offset_x),
            rect.y - int(self.offset_y),
            rect.width,
            rect.height,
        )

    def apply_point(self, x: float, y: float):
        """Convert a world-space point to screen-space."""
        return x - self.offset_x, y - self.offset_y

    # ------------------------------------------------------------------
    @property
    def world_rect(self) -> pygame.Rect:
        """The visible world rectangle (for culling)."""
        return pygame.Rect(
            int(self.offset_x), int(self.offset_y),
            SCREEN_WIDTH, SCREEN_HEIGHT
        )
