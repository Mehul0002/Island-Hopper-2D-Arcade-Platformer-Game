"""
player.py – Player character with physics, animation, and state machine.
"""

import pygame
from settings import *
from draw_utils import make_player_surf
from particles import ParticleSystem


class Player(pygame.sprite.Sprite):
    """
    Controllable player with:
    - Horizontal movement + jump
    - Gravity / fall
    - Ladder climbing
    - Frame-based animation
    - State machine: idle, run, jump, fall, climb, dead
    """

    ANIM_FPS = 8   # animation frames per second

    def __init__(self, x: float, y: float, particles: ParticleSystem):
        super().__init__()

        self.particles = particles

        # Dimensions
        self.w = 36
        self.h = 52

        # Pre-render animation frames
        self._frames: dict[str, list[pygame.Surface]] = {}
        self._prerender_frames()

        # State
        self.state     = "idle"
        self.facing    = 1       # 1 = right, -1 = left
        self.frame_idx = 0
        self._anim_timer = 0

        # Physics
        self.pos   = pygame.math.Vector2(x, y)
        self.vel   = pygame.math.Vector2(0, 0)
        self.on_ground   = False
        self.on_ladder   = False
        self.was_on_ground = False

        # Inventory / status
        self.coins      = 0
        self.has_key    = False
        self.level_done = False
        self.dead       = False

        # Collision rect
        self.rect = pygame.Rect(int(self.pos.x), int(self.pos.y), self.w, self.h)

        # Coyote time + jump buffer
        self._coyote   = 0
        self._jmp_buf  = 0
        self.COYOTE    = 8    # frames
        self.JMP_BUF   = 6   # frames

    # ──────────────────────────────────────────────────────────────────
    # Frame pre-rendering
    # ──────────────────────────────────────────────────────────────────

    def _prerender_frames(self) -> None:
        states = ["idle", "run", "jump", "fall", "climb"]
        for s in states:
            n = 4 if s in ("run", "climb") else 1
            frames_r = [make_player_surf(self.w, self.h, 1,  i, s) for i in range(n)]
            frames_l = [pygame.transform.flip(f, True, False) for f in frames_r]
            self._frames[f"{s}_1"]  = frames_r
            self._frames[f"{s}_-1"] = frames_l

    def _get_frame(self) -> pygame.Surface:
        key = f"{self.state}_{self.facing}"
        frames = self._frames.get(key, self._frames["idle_1"])
        return frames[self.frame_idx % len(frames)]

    # ──────────────────────────────────────────────────────────────────
    # Update
    # ──────────────────────────────────────────────────────────────────

    def update(self, keys: pygame.key.ScancodeWrapper,
               platforms: pygame.sprite.Group,
               ladders: list[pygame.Rect],
               dt_ms: int) -> None:

        if self.dead:
            return

        self._handle_input(keys)
        self._apply_physics(platforms, ladders)
        self._animate(dt_ms)
        self._check_fall_death()

    # ──────────────────────────────────────────────────────────────────
    # Input
    # ──────────────────────────────────────────────────────────────────

    def _handle_input(self, keys) -> None:
        # Horizontal
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.facing = -1
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
            self.facing = 1
            moving = True
        else:
            self.vel.x *= 0.72   # friction

        # Jump buffer
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self._jmp_buf = self.JMP_BUF
        else:
            if self._jmp_buf > 0:
                self._jmp_buf -= 1

        # Variable jump height: release key to cut jump short
        if not (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]):
            if self.vel.y < -4:
                self.vel.y *= 0.88

        # State pre-set (physics will finalise)
        if not self.on_ladder:
            if not self.on_ground:
                self.state = "fall" if self.vel.y > 0 else "jump"
            elif moving:
                self.state = "run"
            else:
                self.state = "idle"

    # ──────────────────────────────────────────────────────────────────
    # Physics
    # ──────────────────────────────────────────────────────────────────

    def _apply_physics(self, platforms: pygame.sprite.Group,
                       ladders: list[pygame.Rect]) -> None:

        keys = pygame.key.get_pressed()

        # --- Ladder check ---
        on_lad = False
        for lr in ladders:
            if self.rect.colliderect(lr):
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    on_lad = True
                    self.vel.y = -LADDER_SPEED
                    self.state = "climb"
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    on_lad = True
                    self.vel.y = LADDER_SPEED
                    self.state = "climb"
                break

        if on_lad:
            self.on_ladder = True
            self.vel.x *= 0.5
            self.vel.y = max(-LADDER_SPEED, min(LADDER_SPEED, self.vel.y))
        else:
            self.on_ladder = False

        # --- Gravity ---
        if not self.on_ladder:
            self.vel.y += GRAVITY
            self.vel.y = min(self.vel.y, MAX_FALL_SPEED)

        # --- Coyote time ---
        self.was_on_ground = self.on_ground
        if self.on_ground:
            self._coyote = self.COYOTE
        elif self._coyote > 0:
            self._coyote -= 1

        # --- Jump ---
        can_jump = self.on_ground or self._coyote > 0
        if self._jmp_buf > 0 and can_jump and not self.on_ladder:
            self.vel.y = PLAYER_JUMP
            self.on_ground = False
            self._coyote  = 0
            self._jmp_buf = 0
            self.state = "jump"

        # --- Move X ---
        self.pos.x += self.vel.x
        self.rect.x = int(self.pos.x)
        self._resolve_x(platforms)

        # --- Move Y ---
        self.pos.y += self.vel.y
        self.rect.y = int(self.pos.y)
        self.on_ground = False
        self._resolve_y(platforms)

        # Dust on landing
        if not self.was_on_ground and self.on_ground:
            self.particles.emit_dust(self.rect.centerx, self.rect.bottom, 6)

        # World left boundary
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x = 0
            self.rect.x = 0

    def _resolve_x(self, platforms: pygame.sprite.Group) -> None:
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel.x < 0:
                    self.rect.left  = plat.rect.right
                self.pos.x = float(self.rect.x)
                self.vel.x = 0

    def _resolve_y(self, platforms: pygame.sprite.Group) -> None:
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0:
                    self.rect.bottom = plat.rect.top
                    self.on_ground   = True
                    self.vel.y       = 0
                elif self.vel.y < 0:
                    self.rect.top   = plat.rect.bottom
                    self.vel.y      = 0
                self.pos.y = float(self.rect.y)

    # ──────────────────────────────────────────────────────────────────
    # Animation
    # ──────────────────────────────────────────────────────────────────

    def _animate(self, dt_ms: int) -> None:
        self._anim_timer += dt_ms
        frame_ms = 1000 // self.ANIM_FPS
        if self._anim_timer >= frame_ms:
            self._anim_timer -= frame_ms
            self.frame_idx += 1

    # ──────────────────────────────────────────────────────────────────
    # Misc
    # ──────────────────────────────────────────────────────────────────

    def _check_fall_death(self) -> None:
        if self.pos.y > WORLD_H + 200:
            self.dead = True

    def collect_coin(self) -> None:
        self.coins += 1
        self.particles.emit_coins(self.rect.centerx, self.rect.centery, 14)

    def collect_key(self) -> None:
        self.has_key = True
        self.particles.emit_sparkle(self.rect.centerx, self.rect.centery,
                                    color=(255, 220, 50), count=16)

    def collect_chest(self) -> None:
        self.level_done = True
        self.particles.emit_sparkle(self.rect.centerx, self.rect.centery,
                                    color=(255, 215, 0), count=24)

    def reset(self, x: float, y: float) -> None:
        self.pos.x  = x
        self.pos.y  = y
        self.vel     = pygame.math.Vector2(0, 0)
        self.on_ground   = False
        self.on_ladder   = False
        self.dead        = False
        self.coins       = 0
        self.has_key     = False
        self.level_done  = False
        self.frame_idx   = 0
        self._coyote     = 0
        self._jmp_buf    = 0
        self.rect.topleft = (int(x), int(y))

    # ──────────────────────────────────────────────────────────────────
    # Draw
    # ──────────────────────────────────────────────────────────────────

    def draw(self, surf: pygame.Surface, cam_ox: float, cam_oy: float) -> None:
        frame = self._get_frame()
        sx = self.rect.x - int(cam_ox)
        sy = self.rect.y - int(cam_oy)
        surf.blit(frame, (sx, sy))

        # Shadow
        shad = pygame.Surface((self.w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 0, 0, 60), (0, 0, self.w, 8))
        surf.blit(shad, (sx, sy + self.h + 1))
