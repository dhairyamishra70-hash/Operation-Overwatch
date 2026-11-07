import pygame
import math
import random


# 1. GAME WINDOW

WIDTH , HEIGHT = 900,600
FPS = 60
HUD_HEIGHT = 40
FOOTER_HEIGHT = 28

# Colours

GRASS = (34,90,48)
WHITE = (240,240,240)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (210, 50, 50)
GREEN = (60, 200, 90)
BLUE = (70, 130, 230)
GREY = (60, 60, 60)

# ARMORY

START_FUNDS = 150
BASE_MAX_HEALTH = 150
ARCHER_COST = 50
MAX_ARCHER_LEVEL = 5
KILLSTREAK_NEEDED = 10
VOLLEY_DAMAGE = 80
INTERMISSION_TIME = 4.0

# 2. Enemy types 

# Wave 1

ENEMY_TYPES = {
    "grunt":  {"health": 35,  "speed": 60,  "damage": 10, "reward": 10, "radius": 10, "color": (200, 70, 70)},
    "runner": {"health": 25,  "speed": 110, "damage": 8,  "reward": 12, "radius": 8,  "color": (230, 150, 40)},
}
#  3. Helper Function

def distance(x1, y1, x2, y2):
    return math.hypot(x2-x1,y2-y1)

# 4. BASE

class Base:
    def __init__(self):
        self.rect = pygame.rect(WIDTH - 90, 0 , 60 , 130)
        self.rect.centery = (HUD_HEIGHT + HEIGHT - FOOTER_HEIGHT)// 2
        self.max_health =  BASE_MAX_HEALTH
        self.health = BASE_MAX_HEALTH

    @property
    def center(self):
        return self.rect.center

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.rect(screen, (150,130,100), self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3)

        bar = pygame.Rect(self.rect.x, self.rect.y - 14, self.rect.width, 8)
        pygame.draw.rect(screen, GREY. bar)
        fill = bar.copy()
        fill.width =  int(bar.width * self.health / self.max_health)
        pygame.draw.rect(screen,  GREEN, fill)

#  Enemy 

def __init__(self, kind, wave):
    stats = ENEMY_TYPES[kind]
    scale = 1 + 0.25  * (wave - 1)
    self.kind = kind
    self.x = -20
    self.y = random.randint(HUD_HEIGHT + 30, HEIGHT - FOOTER_HEIGHT - 30 )
    self.max_health = stats["health"] * scale
    self.health = self.max_health
    self.speed = stats["Speed"]
    self.damage = stats["Damage"]
    self.reward = stats["Reward"]
    self.radius = stats["Radius"]
    self.color = stats["color"]

def update (self, dt, base):

    """Moving to the base"""
    dx = base.center[0]- self.x
    dy = base.center[1]- self.y
    dist = math.hypot(dx, dy)
    if dist > 0:
        step = self.speed * dt
        self.x += dx / dist * step
        self.y += dy / dist * step


    def reached_base(self, base):

        # Collision at base

        return base.rect.inflate(self.radius * 2,  self.radius * 2).collidepoint(self.x, self.y)

    def is_dead(self):
        return self.health <= 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, ((int(self.x), self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y),), self.radius, 2)

        #  health bar

        w = self.radius * 2
        bar = pygame.Rect