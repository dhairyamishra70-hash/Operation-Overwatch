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

# Enemy types 

# Wave 1

ENEMY_TYPES = {
    "grunt":  {"health": 35,  "speed": 60,  "damage": 10, "reward": 10, "radius": 10, "color": (200, 70, 70)},
    "runner": {"health": 25,  "speed": 110, "damage": 8,  "reward": 12, "radius": 8,  "color": (230, 150, 40)},
}