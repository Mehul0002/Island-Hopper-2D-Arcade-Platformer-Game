"""
particles.py – Particle system for coin collection, sparkles, and dust.
"""

import random
import math
import pygame
from settings import PARTICLE_COLORS, COIN_YELLOW


class Particle:
    """Single particle emitted when collecting items."""

    __slots__ = ("x", "y", "vx", "vy", "color", "lifetime", "max_life",
                 "radius", "gravity")

    def __init__(self, x: float, y: float, color=None, speed: float = 3.5,
                 lifetime: int = 40, radius: int = 4, gravity: float = 0.15):
        angle = random.uniform(0, math.pi * 2)
        spd   = random.uniform(speed * 0.4, speed)
        self.x        = x
        self.y        = y
        self.vx       = math.cos(angle) * spd
        self.vy       = math.sin(angle) * spd - speed * 0.5
        self.color    = color or random.choice(PARTICLE_COLORS)
        self.lifetime = lifetime
        self.max_life = lifetime
        self.radius   = radius
        self.gravity  = gravity

    def update(self) -> bool:
        """Return False when dead."""
        self.x  += self.vx
        self.y  += self.vy
        self.vy += self.gravity
        self.vx *= 0.97
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        alpha = int(255 * self.lifetime / self.max_life)
        r = max(1, int(self.radius * self.lifetime / self.max_life))
        sx = int(self.x - cam_ox)
        sy = int(self.y - cam_oy)
        # Draw with alpha manually
        tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*self.color, alpha), (r, r), r)
        surf.blit(tmp, (sx - r, sy - r))


class DustParticle(Particle):
    """Grey dust emitted when landing."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, color=(200, 190, 170), speed=2,
                         lifetime=25, radius=6, gravity=0.05)
        self.vy = -random.uniform(0.5, 2)


class ParticleSystem:
    """Manages and draws all active particles."""

    def __init__(self):
        self._particles: list[Particle] = []

    def emit_coins(self, x: float, y: float, count: int = 12) -> None:
        for _ in range(count):
            self._particles.append(Particle(x, y, color=COIN_YELLOW,
                                            speed=4, lifetime=45, radius=5))

    def emit_sparkle(self, x: float, y: float,
                     color=None, count: int = 8) -> None:
        for _ in range(count):
            self._particles.append(Particle(x, y, color=color,
                                            speed=3, lifetime=35, radius=3))

    def emit_dust(self, x: float, y: float, count: int = 5) -> None:
        for _ in range(count):
            self._particles.append(DustParticle(x, y))

    def update(self) -> None:
        self._particles = [p for p in self._particles if p.update()]

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        for p in self._particles:
            p.draw(surf, cam_ox, cam_oy)

    def clear(self) -> None:
        self._particles.clear()
