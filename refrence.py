"""
OPERATION: OVERWATCH  -  Semester 1 Python Project
A simple top-down tower-defense game made with Pygame.

Install:  pip install pygame
Run:      python overwatch.py

CONTROLS
  Left click (empty ground) ... place an archer (costs funds)
  Left click (on an archer) ... select it (shows its range)
  U ........................... upgrade the selected archer
  SPACE ....................... Divine Volley (when killstreak is full)
  N ........................... skip the countdown, start the next wave
  P ........................... pause / resume
  R ........................... restart
  ESC ......................... quit
"""

import math
import random
import sys

import pygame

# ----------------------------------------------------------------------
# 1. SETTINGS  (variables you can tweak to balance the game)
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 900, 600
FPS = 60
HUD_HEIGHT = 40          # top bar
FOOTER_HEIGHT = 28       # bottom hint bar

START_FUNDS = 150
BASE_MAX_HEALTH = 100
ARCHER_COST = 50
MAX_ARCHER_LEVEL = 5
KILLSTREAK_NEEDED = 10
VOLLEY_DAMAGE = 80
INTERMISSION_TIME = 6.0  # seconds between waves

# Colours (R, G, B)
GRASS = (34, 90, 48)
WHITE = (240, 240, 240)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (210, 50, 50)
GREEN = (60, 200, 90)
BLUE = (70, 130, 230)
GREY = (60, 60, 60)

# Dictionary of enemy types (stats are for wave 1)
ENEMY_TYPES = {
    "grunt":  {"health": 40,  "speed": 60,  "damage": 10, "reward": 10, "radius": 10, "color": (200, 70, 70)},
    "runner": {"health": 25,  "speed": 110, "damage": 8,  "reward": 12, "radius": 8,  "color": (230, 150, 40)},
    "brute":  {"health": 160, "speed": 35,  "damage": 25, "reward": 30, "radius": 15, "color": (140, 50, 160)},
}


# ----------------------------------------------------------------------
# 2. HELPER FUNCTION
# ----------------------------------------------------------------------
def distance(x1, y1, x2, y2):
    """Straight-line distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


# ----------------------------------------------------------------------
# 3. BASE  (the sector the player protects)
# ----------------------------------------------------------------------
class Base:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 90, 0, 60, 130)
        self.rect.centery = (HUD_HEIGHT + HEIGHT - FOOTER_HEIGHT) // 2
        self.max_health = BASE_MAX_HEALTH
        self.health = BASE_MAX_HEALTH

    @property
    def center(self):
        return self.rect.center

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)   # Health = Health - Damage

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.rect(screen, (150, 130, 100), self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3)
        # health bar above the base
        bar = pygame.Rect(self.rect.x, self.rect.y - 14, self.rect.width, 8)
        pygame.draw.rect(screen, GREY, bar)
        fill = bar.copy()
        fill.width = int(bar.width * self.health / self.max_health)
        pygame.draw.rect(screen, GREEN, fill)


# ----------------------------------------------------------------------
# 4. ENEMY
# ----------------------------------------------------------------------
class Enemy:
    def __init__(self, kind, wave):
        stats = ENEMY_TYPES[kind]
        scale = 1 + 0.15 * (wave - 1)               # enemies get stronger each wave
        self.kind = kind
        self.x = -20
        self.y = random.randint(HUD_HEIGHT + 30, HEIGHT - FOOTER_HEIGHT - 30)
        self.max_health = stats["health"] * scale
        self.health = self.max_health
        self.speed = stats["speed"]
        self.damage = stats["damage"]
        self.reward = stats["reward"]
        self.radius = stats["radius"]
        self.color = stats["color"]

    def update(self, dt, base):
        """Move toward the centre of the base."""
        dx = base.center[0] - self.x
        dy = base.center[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            step = self.speed * dt
            self.x += dx / dist * step
            self.y += dy / dist * step

    def reached_base(self, base):
        # Collision: enemy point vs. base rectangle (slightly enlarged)
        return base.rect.inflate(self.radius * 2, self.radius * 2).collidepoint(self.x, self.y)

    def is_dead(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        # tiny health bar
        w = self.radius * 2
        bar = pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius - 7, w, 4)
        pygame.draw.rect(screen, GREY, bar)
        bar.width = max(0, int(w * self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, bar)


# ----------------------------------------------------------------------
# 5. ARROW (projectile)
# ----------------------------------------------------------------------
class Arrow:
    SPEED = 420

    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.alive = True

    def update(self, dt):
        # If the target already died, the arrow disappears.
        if self.target.is_dead():
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        step = self.SPEED * dt
        if dist <= step + self.target.radius:       # HIT
            self.target.health -= self.damage
            self.alive = False
        else:
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 3)


# ----------------------------------------------------------------------
# 6. ARCHER
# ----------------------------------------------------------------------
class Archer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.damage = 12
        self.range = 140
        self.cooldown = 0.8        # seconds between shots
        self.timer = 0.0           # time until next shot is allowed

    @property
    def upgrade_cost(self):
        return 40 * self.level

    def upgrade(self):
        self.level += 1
        self.damage = round(self.damage * 1.3, 1)
        self.range += 12
        self.cooldown = max(0.25, self.cooldown * 0.92)

    def update(self, dt, enemies, arrows):
        self.timer -= dt
        if self.timer > 0:
            return
        # Look through enemies -> check distance -> pick the closest one in range
        target = None
        best = self.range + 1
        for enemy in enemies:
            d = distance(self.x, self.y, enemy.x, enemy.y)
            if d <= self.range and d < best:
                best = d
                target = enemy
        if target is not None:
            arrows.append(Arrow(self.x, self.y, target, self.damage))
            self.timer = self.cooldown                # start cooldown

    def draw(self, screen, font, selected=False):
        if selected:
            ring = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (255, 255, 255, 40), (self.range, self.range), self.range)
            pygame.draw.circle(ring, (255, 255, 255, 120), (self.range, self.range), self.range, 2)
            screen.blit(ring, (self.x - self.range, self.y - self.range))
        pygame.draw.circle(screen, BLUE, (self.x, self.y), 14)
        pygame.draw.circle(screen, GOLD if selected else BLACK, (self.x, self.y), 14, 2)
        label = font.render(str(self.level), True, WHITE)
        screen.blit(label, label.get_rect(center=(self.x, self.y)))


# ----------------------------------------------------------------------
# 7. GAME (ties all the systems together)
# ----------------------------------------------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Operation: Overwatch")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 56, bold=True)
        self.reset()

    # ---------- setup / restart ----------
    def reset(self):
        self.state = "playing"              # "playing", "paused", "game_over"
        self.base = Base()
        self.enemies = []
        self.archers = []
        self.arrows = []
        self.funds = START_FUNDS
        self.wave = 0
        self.kills = 0
        self.killstreak = 0
        self.wave_active = False
        self.countdown = INTERMISSION_TIME  # time until wave 1
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.selected = None
        self.message = ""
        self.message_timer = 0.0
        self.flash = 0.0

    def say(self, text):
        self.message = text
        self.message_timer = 2.0

    # ---------- wave system ----------
    def start_wave(self):
        self.wave += 1
        self.wave_active = True
        count = 4 + 2 * self.wave
        kinds = ["grunt"]
        weights = [6]
        if self.wave >= 2:
            kinds.append("runner")
            weights.append(3)
        if self.wave >= 3:
            kinds.append("brute")
            weights.append(1 + self.wave // 3)
        self.spawn_queue = random.choices(kinds, weights, k=count)
        self.spawn_timer = 0.0

    def update_waves(self, dt):
        if not self.wave_active:
            self.countdown -= dt
            if self.countdown <= 0:
                self.start_wave()
            return
        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.enemies.append(Enemy(self.spawn_queue.pop(), self.wave))
                self.spawn_timer = max(0.4, 1.3 - 0.06 * self.wave)
        elif not self.enemies:                       # wave cleared
            bonus = 20 + 5 * self.wave
            self.funds += bonus
            self.say(f"Wave {self.wave} cleared!  +{bonus} funds")
            self.wave_active = False
            self.countdown = INTERMISSION_TIME

    # ---------- economy / killstreak ----------
    def collect_dead_enemies(self):
        alive = []
        for enemy in self.enemies:
            if enemy.is_dead():
                self.funds += enemy.reward
                self.kills += 1
                self.killstreak += 1
            else:
                alive.append(enemy)
        self.enemies = alive

    def use_volley(self):
        if self.state != "playing":
            return
        if self.killstreak < KILLSTREAK_NEEDED:
            self.say(f"Killstreak {self.killstreak}/{KILLSTREAK_NEEDED} - not ready")
            return
        for enemy in self.enemies:
            enemy.health -= VOLLEY_DAMAGE
        self.collect_dead_enemies()
        self.killstreak = 0
        self.flash = 0.25
        self.say("DIVINE VOLLEY!")

    # ---------- player actions ----------
    def handle_click(self, pos):
        x, y = pos
        if y < HUD_HEIGHT or y > HEIGHT - FOOTER_HEIGHT:
            return
        # clicked an existing archer? -> select it
        for archer in self.archers:
            if distance(x, y, archer.x, archer.y) <= 16:
                self.selected = archer
                return
        # otherwise try to place a new archer
        if x > self.base.rect.left - 20:
            self.say("Too close to the base!")
        elif any(distance(x, y, a.x, a.y) < 32 for a in self.archers):
            self.say("Too close to another archer!")
        elif self.funds < ARCHER_COST:
            self.say("Not enough funds!")
        else:
            self.funds -= ARCHER_COST
            new_archer = Archer(x, y)
            self.archers.append(new_archer)
            self.selected = new_archer

    def upgrade_selected(self):
        archer = self.selected
        if archer is None:
            self.say("Select an archer first")
        elif archer.level >= MAX_ARCHER_LEVEL:
            self.say("Archer is already max level")
        elif self.funds < archer.upgrade_cost:
            self.say(f"Need {archer.upgrade_cost} funds to upgrade")
        else:
            self.funds -= archer.upgrade_cost
            archer.upgrade()

    # ---------- main update ----------
    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
        if self.flash > 0:
            self.flash -= dt
        if self.state != "playing":
            return

        self.update_waves(dt)

        # enemies move; those reaching the base damage it
        still_walking = []
        for enemy in self.enemies:
            enemy.update(dt, self.base)
            if enemy.reached_base(self.base):
                self.base.take_damage(enemy.damage)
                self.killstreak = 0              # streak is lost when one gets through
            else:
                still_walking.append(enemy)
        self.enemies = still_walking

        # archers shoot, arrows fly
        for archer in self.archers:
            archer.update(dt, self.enemies, self.arrows)
        for arrow in self.arrows:
            arrow.update(dt)
        self.arrows = [a for a in self.arrows if a.alive]

        self.collect_dead_enemies()

        if self.base.is_destroyed():
            self.state = "game_over"

    # ---------- drawing ----------
    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(WIDTH // 2, y)))

    def draw_hud(self):
        pygame.draw.rect(self.screen, (25, 25, 30), (0, 0, WIDTH, HUD_HEIGHT))
        text = (f"Wave: {self.wave} | Funds: {self.funds} | "
                f"Base HP: {self.base.health} | "
                f"Killstreak: {self.killstreak}/{KILLSTREAK_NEEDED}")
        self.screen.blit(self.font.render(text, True, WHITE), (12, 10))
        if self.killstreak >= KILLSTREAK_NEEDED:
            ready = self.font.render("SPACE: VOLLEY READY!", True, GOLD)
            self.screen.blit(ready, (WIDTH - ready.get_width() - 12, 10))

        # footer
        pygame.draw.rect(self.screen, (25, 25, 30), (0, HEIGHT - FOOTER_HEIGHT, WIDTH, FOOTER_HEIGHT))
        if self.selected:
            a = self.selected
            info = (f"Archer Lv{a.level}  dmg {a.damage}  range {a.range}  "
                    f"| U: upgrade ({a.upgrade_cost if a.level < MAX_ARCHER_LEVEL else 'MAX'})")
        else:
            info = f"Click ground: place archer ({ARCHER_COST})  |  P: pause  |  N: next wave  |  R: restart"
        self.screen.blit(self.small_font.render(info, True, WHITE), (12, HEIGHT - FOOTER_HEIGHT + 6))

        if not self.wave_active and self.state == "playing":
            self.draw_text_center(f"Wave {self.wave + 1} in {max(0, math.ceil(self.countdown))}  (N to start now)",
                                  self.font, GOLD, HUD_HEIGHT + 20)
        if self.message_timer > 0:
            self.draw_text_center(self.message, self.font, WHITE, HUD_HEIGHT + 50)

    def draw(self):
        self.screen.fill(GRASS)
        self.base.draw(self.screen)
        for archer in self.archers:
            archer.draw(self.screen, self.small_font, archer is self.selected)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for arrow in self.arrows:
            arrow.draw(self.screen)
        self.draw_hud()

        if self.flash > 0:                           # volley flash effect
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 200, int(255 * self.flash / 0.25 * 0.6)))
            self.screen.blit(overlay, (0, 0))

        if self.state == "paused":
            self.dim_screen()
            self.draw_text_center("PAUSED", self.big_font, WHITE, HEIGHT // 2)
            self.draw_text_center("Press P to resume", self.font, WHITE, HEIGHT // 2 + 50)
        elif self.state == "game_over":
            self.dim_screen()
            self.draw_text_center("SECTOR LOST", self.big_font, RED, HEIGHT // 2 - 30)
            self.draw_text_center(f"You reached wave {self.wave} with {self.kills} kills",
                                  self.font, WHITE, HEIGHT // 2 + 25)
            self.draw_text_center("Press R to restart", self.font, GOLD, HEIGHT // 2 + 60)

        pygame.display.flip()

    def dim_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

    # ---------- events + main loop ----------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_p:
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                elif self.state == "playing":
                    if event.key == pygame.K_u:
                        self.upgrade_selected()
                    elif event.key == pygame.K_SPACE:
                        self.use_volley()
                    elif event.key == pygame.K_n and not self.wave_active:
                        self.countdown = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "playing":
                    self.handle_click(event.pos)
        return True

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0       # seconds since last frame
            dt = min(dt, 0.05)                       # avoid huge jumps if the window lags
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()