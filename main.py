import pygame
import math
import random
import sys

import pygame
import sys
import math
import random

pygame.init()

# window size - we all agreed on 1280 x 720
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Operation: Overwatch")
clock = pygame.time.Clock()

# colors
bg_color = (4, 6, 10)
cream = (244, 236, 218)
silver = (214, 220, 226)


# ------------------------------------------------------------
# the eye (first page)
# ------------------------------------------------------------

def make_glyphs(font, levels, dark, bright):
    # draws every character one time at the start, because
    # drawing text again and again every frame is really slow
    result = []
    for i in range(len(levels)):
        amount = i / (len(levels) - 1)
        r = int(dark[0] + (bright[0] - dark[0]) * amount)
        g = int(dark[1] + (bright[1] - dark[1]) * amount)
        b = int(dark[2] + (bright[2] - dark[2]) * amount)
        images = []
        for c in levels[i]:
            images.append(font.render(c, True, (r, g, b)))
        result.append(images)
    return result


class Eye:
    def __init__(self):
        self.cell = 12                    # each character gets a 12x12 square
        self.cols = width // self.cell
        self.rows = height // self.cell
        self.cx = self.cols / 2           # middle of the eye
        self.cy = self.rows / 2
        self.eye_w = 40
        self.eye_h = 17

        # dark -> bright, a few characters per level so it shimmers
        levels = [" ", ".,'", ":;", "-=~", "+*", "xX", "#%", "&8", "@W"]
        font = pygame.font.SysFont("couriernew", self.cell + 2, bold=True)

        # three color sets: copper (skin), silver (white of eye), amber (iris)
        copper = make_glyphs(font, levels, (40, 22, 12), (190, 100, 45))
        silver_set = make_glyphs(font, levels, (45, 50, 58), (228, 232, 236))
        amber = make_glyphs(font, levels, (55, 26, 12), (238, 140, 52))
        self.sets = [copper, silver_set, amber]

        # every square gets its own random number
        self.noise = []
        for y in range(self.rows):
            row = []
            for x in range(self.cols):
                row.append(random.random())
            self.noise.append(row)

        self.iris_x = self.cx
        self.iris_y = self.cy

    def update(self, offset_x, offset_y, speed=0.1):
        # offset = how many squares away from the middle the iris wants to go
        want_x = self.cx + max(-14, min(14, offset_x))
        want_y = self.cy + max(-5, min(5, offset_y))

        # it glides there instead of jumping (bigger speed = faster glide)
        self.iris_x += (want_x - self.iris_x) * speed
        self.iris_y += (want_y - self.iris_y) * speed

    def look(self, x, y, t, n):
        # gives back (how bright 0-1, which color set) for one square
        dx = (x - self.cx) / self.eye_w
        dy = (y - self.cy) / self.eye_h

        # outside the eye
        if abs(dx) > 1 or abs(dy) > 1 - dx * dx:
            value = 0.28 + (n - 0.5) * 0.16
            if y < self.cy + 6:
                return value, 1           # silver on top
            return value, 0               # copper at the bottom

        # eyelid line
        if abs(dy) > 0.85 * (1 - dx * dx):
            return 0.95, 1

        dist = math.hypot(x - self.iris_x, y - self.iris_y)
        if dist < 4:
            return 0.0, 2                 # pupil
        if dist < 5.5:
            return 0.25, 2                # dark ring around the pupil
        if dist < 11:
            angle = math.atan2(y - self.iris_y, x - self.iris_x)
            return 0.55 + 0.35 * abs(math.sin(angle * 8 + t)), 2
        return 0.55 + (n - 0.5) * 0.2, 1  # white of the eye

    def draw(self, surface):
        t = pygame.time.get_ticks() / 1000

        for y in range(self.rows):
            for x in range(self.cols):
                n = self.noise[y][x]
                value, which = self.look(x, y, t, n)

                level = int(value * 8.99)
                level = max(0, min(8, level))
                if level == 0:
                    continue              # blank square, nothing to draw

                choices = self.sets[which][level]
                pick = int(n * 100 + t * 4) % len(choices)
                surface.blit(choices[pick], (x * self.cell, y * self.cell))


# ------------------------------------------------------------
# the night siege (menu background)
# ------------------------------------------------------------
# a ruined temple on a hill, a moon, stars, mist and fire embers.
# the scene is drawn small and stretched up, that's what makes it soft and blurry

scale = 3
low_w = width // scale
low_h = height // scale
temple_floor = int(low_h * 0.62)     # height of the temple floor

low_surface = pygame.Surface((low_w, low_h))


def scaled(points):
    # turns points like (0.5, 0.5) into real positions on the small surface
    result = []
    for fx, fy in points:
        result.append((fx * low_w, fy * low_h))
    return result


# the temple columns (some are broken, so they are shorter)
column_heights = [34, 34, 34, 34, 34, 22, 34, 10]
column_left = low_w * 0.62
column_gap = low_w * 0.32 / 7

# torches between the columns (x, y)
torches = []
for i in (0, 2, 4, 6):
    torches.append((int(column_left + column_gap * i + column_gap / 2 + 3), temple_floor - 9))


def make_scenery():
    # everything that never moves: sky, moon, hills, temple
    surface = pygame.Surface((low_w, low_h))

    # sky: dark blue on top, with the glow of far away fires near the bottom
    for y in range(low_h):
        a = min(y / (low_h * 0.8), 1.0)
        fire = max(0, (a - 0.55) / 0.45) ** 2
        r = 4 + 20 * a + 70 * fire
        g = 6 + 16 * a + 28 * fire
        b = 16 + 36 * a + 10 * fire
        pygame.draw.line(surface, (int(min(r, 255)), int(min(g, 255)), int(min(b, 255))),
                         (0, y), (low_w, y))

    # moon with a soft glow around it
    moon_x = int(low_w * 0.70)
    moon_y = int(low_h * 0.22)
    # lots of circles from big+dark to small+bright = a smooth glow
    for i in range(14):
        amount = i / 13
        radius = int(44 - 22 * amount)
        color = (int(16 + 58 * amount), int(22 + 64 * amount), int(46 + 82 * amount))
        pygame.draw.circle(surface, color, (moon_x, moon_y), radius)
    pygame.draw.circle(surface, (226, 231, 241), (moon_x, moon_y), 20)
    for dx, dy, r in ((-7, -4, 5), (6, 5, 4), (-2, 9, 3), (8, -8, 2)):
        pygame.draw.circle(surface, (204, 211, 226), (moon_x + dx, moon_y + dy), r)

    # far hills
    far = [(0, 1.0), (0, 0.80), (0.2, 0.72), (0.4, 0.78), (0.55, 0.70),
           (0.8, 0.72), (1.0, 0.66), (1.0, 1.0)]
    pygame.draw.polygon(surface, (14, 18, 34), scaled(far))

    # the hill the temple stands on
    hill = [(0.45, 1.0), (0.50, 0.76), (0.57, 0.66), (0.60, 0.62),
            (0.97, 0.62), (1.0, 0.66), (1.0, 1.0)]
    dark = (7, 9, 18)
    pygame.draw.polygon(surface, dark, scaled(hill))

    # temple: steps, columns, roof beam and the triangle on top
    pygame.draw.rect(surface, dark, (int(low_w * 0.59), temple_floor - 4, int(low_w * 0.39), 6))
    for i in range(8):
        x = int(column_left + column_gap * i)
        pygame.draw.rect(surface, dark, (x, temple_floor - column_heights[i], 6, column_heights[i]))
    roof_left = int(column_left - 4)
    roof_right = int(column_left + column_gap * 4 + 10)
    beam_y = temple_floor - 34 - 5
    pygame.draw.rect(surface, dark, (roof_left, beam_y, roof_right - roof_left, 5))
    pygame.draw.polygon(surface, dark, [(roof_left, beam_y),
                                        ((roof_left + roof_right) // 2, beam_y - 16),
                                        (roof_right, beam_y)])

    # torch poles
    for x, y in torches:
        pygame.draw.rect(surface, dark, (x, y, 1, 9))

    # dark ground at the very front, with spears sticking out of it
    front_color = (3, 4, 9)
    front = [(0, 1.0), (0, 0.92), (0.15, 0.89), (0.3, 0.93), (0.5, 0.90),
             (0.7, 0.94), (0.85, 0.91), (1.0, 0.93), (1.0, 1.0)]
    pygame.draw.polygon(surface, front_color, scaled(front))
    base_y = int(0.92 * low_h)
    for fx, spear_h in ((0.60, 40), (0.64, 34), (0.69, 46), (0.73, 36),
                        (0.88, 42), (0.92, 33), (0.96, 44)):
        x = int(fx * low_w)
        pygame.draw.line(surface, front_color, (x, base_y), (x, base_y - spear_h))
        pygame.draw.polygon(surface, front_color, [(x - 2, base_y - spear_h),
                                                   (x + 2, base_y - spear_h),
                                                   (x, base_y - spear_h - 7)])
    return surface


scenery = make_scenery()

# stars: [x, y, phase, big?]  (only in the sky above the temple roof)
stars = []
for i in range(120):
    stars.append([random.randint(0, low_w - 2), random.randint(1, int(low_h * 0.36)),
                  random.uniform(0, 6.28), i % 9 == 0])

# a bow and arrow made of stars, because the archers are the heroes
cx = int(low_w * 0.44)
cy = int(low_h * 0.30)
archer_stars = [(cx, cy - 30), (cx + 14, cy - 14), (cx + 18, cy), (cx + 14, cy + 14),
                (cx, cy + 30), (cx - 26, cy), (cx + 30, cy), (cx, cy)]
archer_lines = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (5, 6)]


def draw_sky_extras(surface, t):
    # twinkling stars
    for x, y, phase, big in stars:
        b = 0.5 + 0.5 * math.sin(t * 1.5 + phase)
        v = int(90 + 150 * b)
        surface.set_at((x, y), (v, v, min(255, v + 20)))
        if big:
            dim = v // 2
            surface.set_at((x - 1, y), (dim, dim, dim))
            surface.set_at((x + 1, y), (dim, dim, dim))
            surface.set_at((x, y - 1), (dim, dim, dim))
            surface.set_at((x, y + 1), (dim, dim, dim))

    # the constellation
    for a, b in archer_lines:
        pygame.draw.line(surface, (50, 66, 110), archer_stars[a], archer_stars[b])
    for i in range(len(archer_stars)):
        glow = 0.6 + 0.4 * math.sin(t * 2 + i)
        v = int(255 * glow)
        pygame.draw.circle(surface, (v, v, 255), archer_stars[i], 1)


# a shooting star every few seconds
shot = {"life": 0.0, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "next": 4.0}


def draw_shooting_star(surface, t, dt):
    if shot["life"] <= 0 and t > shot["next"]:
        shot["life"] = 0.8
        shot["x"] = random.uniform(low_w * 0.45, low_w * 0.95)
        shot["y"] = random.uniform(low_h * 0.03, low_h * 0.2)
        shot["vx"] = -140.0
        shot["vy"] = 55.0
        shot["next"] = t + random.uniform(5, 9)

    if shot["life"] > 0:
        shot["life"] -= dt
        shot["x"] += shot["vx"] * dt
        shot["y"] += shot["vy"] * dt
        fade = max(0, shot["life"] / 0.8)
        for k in range(8):
            v = int(255 * fade * (1 - k / 8))
            tail_x = shot["x"] - shot["vx"] * 0.012 * k
            tail_y = shot["y"] - shot["vy"] * 0.012 * k
            pygame.draw.circle(surface, (v, v, min(255, v + 10)), (int(tail_x), int(tail_y)), 1)


def draw_torches(surface, t):
    # little fires that flicker
    for x, y in torches:
        flick = 0.7 + 0.3 * math.sin(t * 9 + x) + 0.15 * math.sin(t * 23 + x * 2)
        pygame.draw.circle(surface, (110, 46, 18), (x, y), 5)
        pygame.draw.circle(surface, (255, 140, 40), (x, y), 2 + int(flick))
        pygame.draw.circle(surface, (255, 220, 120), (x, y), 1)


# mist: a wide strip of soft blobs that slowly drifts past
fog_w = low_w * 2
fog_h = 60


def make_fog():
    fog = pygame.Surface((fog_w, fog_h))
    fog.fill((0, 0, 0))
    for i in range(10):
        blob_x = random.randint(0, fog_w)
        rx = random.randint(40, 90)
        ry = random.randint(10, 20)
        strength = random.uniform(0.5, 1.0)

        # one blob = ellipses inside ellipses, brighter in the middle
        blob = pygame.Surface((rx * 2, ry * 2))
        for step in range(6):
            shrink = 1 - step / 6
            level = strength * (step + 1) / 6
            color = (int(22 * level), int(28 * level), int(44 * level))
            w = int(rx * 2 * shrink)
            h = int(ry * 2 * shrink)
            pygame.draw.ellipse(blob, color, (rx - w // 2, ry - h // 2, w, h))

        # add it 3 times (shifted) so the strip wraps around without a seam
        for shift in (-fog_w, 0, fog_w):
            fog.blit(blob, (blob_x - rx + shift, fog_h // 2 - ry), special_flags=pygame.BLEND_RGB_ADD)
    return fog


fog = make_fog()


def draw_fog(surface, t):
    for y, speed in ((int(low_h * 0.70), 6), (int(low_h * 0.84), -9)):
        offset = int((t * speed) % fog_w)
        surface.blit(fog, (-offset, y), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(fog, (fog_w - offset, y), special_flags=pygame.BLEND_RGB_ADD)


# fire embers floating up (drawn on the real screen so they stay sharp)
embers = []
for i in range(60):
    embers.append([random.uniform(0, width), random.uniform(0, height),
                   random.uniform(25, 70),      # how fast it floats up
                   random.uniform(0, 6.28),
                   random.uniform(0.5, 1.6)])


def draw_menu_background(t, dt):
    low_surface.blit(scenery, (0, 0))
    draw_sky_extras(low_surface, t)
    draw_shooting_star(low_surface, t, dt)
    draw_torches(low_surface, t)
    draw_fog(low_surface, t)

    # stretch the small picture to full size (this makes it blurry and soft)
    screen.blit(pygame.transform.smoothscale(low_surface, (width, height)), (0, 0))

    # extra glow: shrink it a LOT, stretch it back, and add it on top
    tiny = pygame.transform.smoothscale(low_surface, (low_w // 8, low_h // 8))
    glow = pygame.transform.smoothscale(tiny, (width, height))
    glow.fill((110, 110, 110), special_flags=pygame.BLEND_RGB_MULT)
    screen.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # embers (small and sharp, so they stand out from the blur)
    for p in embers:
        p[1] -= p[2] * dt
        p[0] += (12 + 10 * math.sin(t + p[3])) * dt
        if p[1] < 0:
            p[1] = height + 5
            p[0] = random.uniform(0, width)
        b = 0.5 + 0.5 * math.sin(t * 4 + p[3])
        color = (255, int(110 + 90 * b), int(30 + 40 * b))
        pygame.draw.circle(screen, color, (int(p[0]), int(p[1])), 1 + int(p[4] * b))


# ------------------------------------------------------------
# the dark smoky panel on the left + the menu text
# ------------------------------------------------------------

def make_panel():
    ink = (5, 7, 12)
    panel = pygame.Surface((width, height), pygame.SRCALPHA)

    # a 1 pixel tall strip that goes from solid to see-through
    strip = pygame.Surface((160, 1), pygame.SRCALPHA)
    for x in range(160):
        alpha = int(255 * (1 - x / 160) ** 1.5)
        strip.set_at((x, 0), (ink[0], ink[1], ink[2], alpha))

    # every row of pixels gets a slightly different edge, so it looks rough
    edges = []
    for y in range(height):
        edge = 430 + 28 * math.sin(y * 0.021 + 1) + 18 * math.sin(y * 0.057 + 2) \
               + 10 * math.sin(y * 0.13) + random.uniform(-8, 8)
        edge = int(edge)
        edges.append(edge)
        pygame.draw.line(panel, (ink[0], ink[1], ink[2], 255), (0, y), (edge - 160, y))
        panel.blit(strip, (edge - 160, y))

    # some random smoke blobs along the edge
    for i in range(45):
        y = random.randint(0, height - 1)
        x = edges[y] + random.randint(-10, 90)
        pygame.draw.circle(panel, (ink[0], ink[1], ink[2], 110), (x, y), random.randint(12, 36))

    # blur it: make it tiny and stretch it back
    small = pygame.transform.smoothscale(panel, (width // 4, height // 4))
    return pygame.transform.smoothscale(small, (width, height))


def spaced_text(text, font, color, spacing):
    # draws the letters one by one so there is a bit of space between them
    images = []
    total = 0
    for c in text:
        image = font.render(c, True, color)
        images.append(image)
        total += image.get_width() + spacing
    result = pygame.Surface((total, images[0].get_height()), pygame.SRCALPHA)
    x = 0
    for image in images:
        result.blit(image, (x, 0))
        x += image.get_width() + spacing
    return result


class MenuItem:
    def __init__(self, text, y, font):
        self.text = text
        self.light = spaced_text(text, font, (205, 212, 218), 3)    # normal text
        self.dark = spaced_text(text, font, (10, 14, 22), 3)        # text on the white pill
        self.rect = pygame.Rect(70, y, 300, 42)
        self.glow = 0.0                                             # 0 = normal, 1 = selected

    def draw(self, surface, selected, dt):
        # glow slides up when selected and back down when not
        if selected:
            self.glow = min(1.0, self.glow + dt * 8)
        else:
            self.glow = max(0.0, self.glow - dt * 8)

        # white pill behind the text that grows out from the left
        if self.glow > 0:
            full_w = self.light.get_width() + 40
            pill_w = int(full_w * (0.4 + 0.6 * self.glow))
            pill = pygame.Surface((pill_w, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(pill, (236, 240, 242), pill.get_rect(), border_radius=10)
            pill.set_alpha(int(255 * self.glow))
            surface.blit(pill, (self.rect.x, self.rect.y))

        # fade between the light text and the dark text
        self.light.set_alpha(int(255 * (1 - self.glow)))
        self.dark.set_alpha(int(255 * self.glow))
        text_y = self.rect.y + (self.rect.height - self.light.get_height()) // 2
        surface.blit(self.light, (self.rect.x + 20, text_y))
        surface.blit(self.dark, (self.rect.x + 20, text_y))



# ------------------------------------------------------------
# GAMEPLAY SYSTEMS
# ------------------------------------------------------------

HUD_HEIGHT = 58
FOOTER_HEIGHT = 58
GROUND_Y = height - FOOTER_HEIGHT - 35

WHITE = (240, 240, 235)
GREY = (115, 125, 135)
GREEN = (80, 190, 115)
RED = (210, 75, 75)
GOLD = (240, 185, 75)
BLUE = (90, 160, 220)
GRASS = (24, 39, 35)
SOIL = (35, 28, 25)

START_FUNDS = 150
BASE_MAX_HEALTH = 150
ARCHER_COST = 50
MAX_ARCHER_LEVEL = 5
KILLSTREAK_NEEDED = 10
VOLLEY_DAMAGE = 80
INTERMISSION_TIME = 4.0

ENEMY_TYPES = {
    "grunt": {
        "health": 35, "speed": 58, "damage": 12, "reward": 5,
        "radius": 12, "color": (190, 72, 72)
    },
    "runner": {
        "health": 28, "speed": 112, "damage": 9, "reward": 8,
        "radius": 9, "color": (225, 145, 55)
    },
    "brute": {
        "health": 105, "speed": 34, "damage": 25, "reward": 18,
        "radius": 17, "color": (125, 75, 145)
    }
}


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


class Base:
    def __init__(self):
        self.rect = pygame.Rect(width - 112, GROUND_Y - 125, 82, 125)
        self.max_health = BASE_MAX_HEALTH
        self.health = BASE_MAX_HEALTH

    @property
    def center(self):
        return self.rect.center

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, surface):
        # Fortress wall and battlements
        pygame.draw.rect(surface, (105, 104, 99), self.rect)
        pygame.draw.rect(surface, (55, 57, 59), self.rect, 3)
        for i in range(4):
            x = self.rect.x + 5 + i * 19
            pygame.draw.rect(surface, (125, 123, 115), (x, self.rect.y - 12, 13, 14))
        pygame.draw.rect(surface, (45, 39, 35),
                         (self.rect.centerx - 13, self.rect.bottom - 48, 26, 48))
        pygame.draw.rect(surface, (35, 37, 39), self.rect, 2)

        bar = pygame.Rect(self.rect.x - 4, self.rect.y - 27, self.rect.width + 8, 9)
        pygame.draw.rect(surface, (45, 45, 48), bar)
        fill = bar.copy()
        fill.width = int(bar.width * self.health / self.max_health)
        pygame.draw.rect(surface, GREEN if self.health > 45 else RED, fill)


class Enemy:
    def __init__(self, kind, wave):
        stats = ENEMY_TYPES[kind]
        scale_factor = 1 + 0.20 * (wave - 1)
        self.kind = kind
        self.x = -25
        self.y = GROUND_Y - random.randint(0, 18)
        self.max_health = stats["health"] * scale_factor
        self.health = self.max_health
        self.speed = stats["speed"] * (1 + 0.025 * (wave - 1))
        self.damage = stats["damage"] + max(0, wave - 1)
        self.reward = stats["reward"] + wave
        self.radius = stats["radius"]
        self.color = stats["color"]

    def update(self, dt, base):
        target_x = base.rect.left
        if self.x < target_x:
            self.x = min(target_x, self.x + self.speed * dt)

    def reached_base(self, base):
        return self.x >= base.rect.left - self.radius

    def is_dead(self):
        return self.health <= 0

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        # Simple side-view enemy sprite
        pygame.draw.ellipse(surface, self.color,
                            (x - self.radius, y - self.radius,
                             self.radius * 2, self.radius * 2))
        pygame.draw.circle(surface, (28, 24, 25),
                           (x + self.radius // 3, y - 3), 2)
        pygame.draw.line(surface, (35, 30, 30),
                         (x - 5, y + self.radius - 1),
                         (x - 8, y + self.radius + 7), 3)
        pygame.draw.line(surface, (35, 30, 30),
                         (x + 5, y + self.radius - 1),
                         (x + 8, y + self.radius + 7), 3)

        bar_width = self.radius * 2
        bar = pygame.Rect(x - self.radius, y - self.radius - 8, bar_width, 4)
        pygame.draw.rect(surface, (55, 55, 58), bar)
        bar.width = max(0, int(bar_width * self.health / self.max_health))
        pygame.draw.rect(surface, GREEN, bar)


class Arrow:
    SPEED = 460

    def __init__(self, x, y, target, damage):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.damage = damage
        self.alive = True

    def update(self, dt):
        if self.target.is_dead():
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.SPEED * dt + self.target.radius:
            self.target.health -= self.damage
            self.alive = False
        elif dist > 0:
            step = self.SPEED * dt
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self, surface):
        x, y = int(self.x), int(self.y)
        pygame.draw.line(surface, (225, 215, 185),
                         (x - 7, y + 3), (x + 7, y - 3), 3)
        pygame.draw.polygon(surface, WHITE,
                            [(x + 7, y - 3), (x + 1, y - 4), (x + 4, y + 2)])


class Archer:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.level = 1
        self.damage = 12
        self.range = 175
        self.cooldown = 0.85
        self.timer = 0.2

    @property
    def upgrade_cost(self):
        return 40 * self.level

    def upgrade(self):
        if self.level >= MAX_ARCHER_LEVEL:
            return
        self.level += 1
        self.damage = round(self.damage * 1.25)
        self.range += 22
        self.cooldown = max(0.30, self.cooldown * 0.90)

    def update(self, dt, enemies, arrows):
        self.timer -= dt
        if self.timer > 0:
            return

        target = None
        nearest_distance = self.range

        for enemy in enemies:
            current_distance = distance(self.x, self.y, enemy.x, enemy.y)
            if current_distance <= nearest_distance:
                nearest_distance = current_distance
                target = enemy

        if target is not None:
            arrows.append(Arrow(self.x + 10, self.y - 12, target, self.damage))
            self.timer = self.cooldown

    def draw(self, surface, font, selected=False):
        if selected:
            ring = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring, (220, 225, 235, 28),
                               (self.range, self.range), self.range)
            pygame.draw.circle(ring, (220, 225, 235, 100),
                               (self.range, self.range), self.range, 2)
            surface.blit(ring, (self.x - self.range, self.y - self.range))

        # Small archer silhouette
        pygame.draw.circle(surface, (205, 180, 145), (self.x, self.y - 22), 8)
        pygame.draw.line(surface, (105, 145, 175),
                         (self.x, self.y - 13), (self.x, self.y + 13), 7)
        pygame.draw.line(surface, (105, 145, 175),
                         (self.x, self.y - 5), (self.x + 13, self.y + 1), 4)
        pygame.draw.line(surface, (90, 65, 48),
                         (self.x + 13, self.y - 18), (self.x + 13, self.y + 8), 2)
        pygame.draw.line(surface, (210, 195, 165),
                         (self.x + 13, self.y - 18), (self.x + 13, self.y + 8), 1)
        pygame.draw.line(surface, (45, 42, 40),
                         (self.x - 5, self.y + 12), (self.x - 9, self.y + 24), 4)
        pygame.draw.line(surface, (45, 42, 40),
                         (self.x + 5, self.y + 12), (self.x + 9, self.y + 24), 4)

        pygame.draw.circle(surface, GOLD if selected else (25, 30, 35),
                           (self.x, self.y - 22), 9, 2)
        level_label = font.render(str(self.level), True, WHITE)
        surface.blit(level_label, level_label.get_rect(center=(self.x, self.y - 22)))


class Game:
    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 19, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 14)
        self.big_font = pygame.font.SysFont("georgia", 54, bold=True)
        self.reset()

    def reset(self):
        self.state = "playing"
        self.base = Base()
        self.enemies = []
        self.archers = []
        self.arrows = []
        self.funds = START_FUNDS
        self.wave = 0
        self.kills = 0
        self.killstreak = 0
        self.wave_active = False
        self.countdown = 1.5
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.selected = None
        self.message = "Deploy archers to defend the fortress"
        self.message_timer = 3.0
        self.flash = 0.0

    def say(self, message):
        self.message = message
        self.message_timer = 2.2

    def start_wave(self):
        if self.wave_active or self.state != "playing":
            return
        self.wave += 1
        self.wave_active = True
        count = 4 + 2 * self.wave
        kinds = ["grunt"]
        weights = [15]

        if self.wave >= 2:
            kinds.append("runner")
            weights.append(4)
        if self.wave >= 3:
            kinds.append("brute")
            weights.append(2 + self.wave // 3)

        self.spawn_queue = random.choices(kinds, weights=weights, k=count)
        self.spawn_timer = 0.0
        self.say(f"WAVE {self.wave} INCOMING")

    def update_waves(self, dt):
        if not self.wave_active:
            self.countdown -= dt
            if self.countdown <= 0:
                self.start_wave()
            return

        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                kind = self.spawn_queue.pop(0)
                self.enemies.append(Enemy(kind, self.wave))
                self.spawn_timer = max(0.38, 1.25 - 0.045 * self.wave)

        elif not self.enemies:
            self.wave_active = False
            bonus = 20 + 5 * self.wave
            self.funds += bonus
            self.countdown = INTERMISSION_TIME
            self.say(f"WAVE {self.wave} CLEARED  +{bonus} FUNDS")

    def collect_dead_enemies(self):
        survivors = []
        for enemy in self.enemies:
            if enemy.is_dead():
                self.funds += enemy.reward
                self.kills += 1
                self.killstreak += 1
            else:
                survivors.append(enemy)
        self.enemies = survivors

    def use_volley(self):
        if self.killstreak < KILLSTREAK_NEEDED:
            self.say(f"VOLLEY NOT READY  {self.killstreak}/{KILLSTREAK_NEEDED}")
            return

        for enemy in self.enemies:
            enemy.health -= VOLLEY_DAMAGE

        self.collect_dead_enemies()
        self.killstreak = 0
        self.flash = 0.22
        self.say("DIVINE VOLLEY RELEASED")

    def handle_click(self, pos):
        x, y = pos
        if y < HUD_HEIGHT or y > height - FOOTER_HEIGHT:
            return

        for archer in self.archers:
            if distance(x, y, archer.x, archer.y - 5) <= 22:
                self.selected = archer
                return

        if x >= self.base.rect.left - 25:
            self.say("TOO CLOSE TO THE FORTRESS")
        elif any(distance(x, y, a.x, a.y) < 38 for a in self.archers):
            self.say("ARCHERS NEED MORE SPACE")
        elif self.funds < ARCHER_COST:
            self.say("NOT ENOUGH FUNDS")
        else:
            self.funds -= ARCHER_COST
            self.selected = Archer(x, min(y, GROUND_Y - 8))
            self.archers.append(self.selected)
            self.say("ARCHER DEPLOYED")

    def upgrade_selected(self):
        archer = self.selected
        if archer is None:
            self.say("SELECT AN ARCHER FIRST")
        elif archer.level >= MAX_ARCHER_LEVEL:
            self.say("ARCHER ALREADY AT MAX LEVEL")
        elif self.funds < archer.upgrade_cost:
            self.say(f"NEED {archer.upgrade_cost} FUNDS")
        else:
            self.funds -= archer.upgrade_cost
            archer.upgrade()
            self.say(f"ARCHER UPGRADED TO LEVEL {archer.level}")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p and self.state in ("playing", "paused"):
                self.state = "paused" if self.state == "playing" else "playing"
            elif event.key == pygame.K_r:
                self.reset()
            elif event.key == pygame.K_u and self.state == "playing":
                self.upgrade_selected()
            elif event.key == pygame.K_SPACE and self.state == "playing":
                self.use_volley()
            elif event.key == pygame.K_n and self.state == "playing" and not self.wave_active:
                self.countdown = 0
                self.start_wave()

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer = max(0, self.message_timer - dt)
        if self.flash > 0:
            self.flash = max(0, self.flash - dt)

        if self.state != "playing":
            return

        self.update_waves(dt)

        survivors = []
        for enemy in self.enemies:
            enemy.update(dt, self.base)
            if enemy.reached_base(self.base):
                self.base.take_damage(enemy.damage)
                self.killstreak = 0
                self.say(f"FORTRESS HIT  -{enemy.damage} HP")
            else:
                survivors.append(enemy)
        self.enemies = survivors

        for archer in self.archers:
            archer.update(dt, self.enemies, self.arrows)

        for arrow in self.arrows:
            arrow.update(dt)
        self.arrows = [arrow for arrow in self.arrows if arrow.alive]

        self.collect_dead_enemies()

        if self.base.is_destroyed():
            self.state = "game over"
            self.say("THE FORTRESS HAS FALLEN")

    def draw_background(self, surface):
        surface.fill((12, 18, 29))

        # Distant mountains and ruined battlefield silhouettes
        pygame.draw.polygon(surface, (24, 31, 43),
                            [(0, 365), (130, 225), (260, 355), (420, 205),
                             (590, 355), (760, 245), (960, 360), (1120, 220),
                             (1280, 350), (1280, GROUND_Y), (0, GROUND_Y)])
        pygame.draw.circle(surface, (190, 166, 125), (1030, 145), 42)
        pygame.draw.circle(surface, (12, 18, 29), (1048, 132), 40)

        # Ground layers
        pygame.draw.rect(surface, (35, 43, 39),
                         (0, GROUND_Y, width, height - GROUND_Y))
        pygame.draw.line(surface, (105, 91, 66),
                         (0, GROUND_Y), (width, GROUND_Y), 3)
        for i in range(18):
            x = (i * 83 + 25) % width
            pygame.draw.line(surface, (48, 57, 48),
                             (x, GROUND_Y + 15), (x + 18, GROUND_Y + 28), 2)

        # HUD and footer
        pygame.draw.rect(surface, (8, 11, 17), (0, 0, width, HUD_HEIGHT))
        pygame.draw.line(surface, (105, 115, 125),
                         (0, HUD_HEIGHT), (width, HUD_HEIGHT), 1)
        pygame.draw.rect(surface, (8, 11, 17),
                         (0, height - FOOTER_HEIGHT, width, FOOTER_HEIGHT))
        pygame.draw.line(surface, (105, 115, 125),
                         (0, height - FOOTER_HEIGHT),
                         (width, height - FOOTER_HEIGHT), 1)

    def draw_text_center(self, surface, text, font, color, y):
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(center=(width // 2, y)))

    def draw_hud(self, surface):
        hud = (f"WAVE {self.wave}     FUNDS {self.funds}     "
               f"FORTRESS {self.base.health}/{self.base.max_health}     "
               f"KILLS {self.kills}     STREAK {self.killstreak}/{KILLSTREAK_NEEDED}")
        surface.blit(self.font.render(hud, True, cream), (18, 18))

        if self.killstreak >= KILLSTREAK_NEEDED:
            ready = self.font.render("SPACE: VOLLEY READY", True, GOLD)
            surface.blit(ready, (width - ready.get_width() - 18, 39))

        if self.selected:
            a = self.selected
            info = (f"ARCHER LV.{a.level}  DAMAGE {a.damage}  RANGE {a.range}  "
                    f"| U: UPGRADE ({a.upgrade_cost if a.level < MAX_ARCHER_LEVEL else 'MAX'})")
        else:
            info = "CLICK GROUND: DEPLOY ARCHER (50)   |   P: PAUSE   N: NEXT WAVE   R: RESTART"
        surface.blit(self.small_font.render(info, True, silver),
                     (18, height - FOOTER_HEIGHT + 20))

        if not self.wave_active and self.state == "playing":
            countdown_text = f"NEXT WAVE {max(0, math.ceil(self.countdown))}s  |  PRESS N TO START"
            self.draw_text_center(surface, countdown_text, self.font, GOLD, HUD_HEIGHT + 25)

        if self.message_timer > 0:
            self.draw_text_center(surface, self.message, self.font, WHITE, HUD_HEIGHT + 55)

    def draw(self, surface):
        self.draw_background(surface)

        # A few battlefield structures behind the units
        for x in (170, 350, 560, 760):
            pygame.draw.rect(surface, (49, 47, 43), (x, GROUND_Y - 55, 10, 55))
            pygame.draw.polygon(surface, (49, 47, 43),
                                [(x - 12, GROUND_Y - 55),
                                 (x + 5, GROUND_Y - 78),
                                 (x + 22, GROUND_Y - 55)])

        self.base.draw(surface)

        for archer in self.archers:
            archer.draw(surface, self.small_font, archer is self.selected)
        for enemy in self.enemies:
            enemy.draw(surface)
        for arrow in self.arrows:
            arrow.draw(surface)

        self.draw_hud(surface)

        if self.flash > 0:
            overlay = pygame.Surface((width, height), pygame.SRCALPHA)
            overlay.fill((255, 235, 175, int(100 * self.flash / 0.22)))
            surface.blit(overlay, (0, 0))

        if self.state == "paused":
            self.dim_screen(surface)
            self.draw_text_center(surface, "PAUSED", self.big_font, WHITE, height // 2 - 15)
            self.draw_text_center(surface, "PRESS P TO RESUME", self.font,
                                  GOLD, height // 2 + 40)

        elif self.state == "game over":
            self.dim_screen(surface)
            self.draw_text_center(surface, "SECTOR LOST", self.big_font, RED,
                                  height // 2 - 35)
            self.draw_text_center(surface,
                                  f"WAVE {self.wave}  |  KILLS {self.kills}",
                                  self.font, WHITE, height // 2 + 20)
            self.draw_text_center(surface, "PRESS R TO RESTART  |  ESC FOR MENU",
                                  self.font, GOLD, height // 2 + 65)

    def dim_screen(self, surface):
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))


# ------------------------------------------------------------
# SETUP AND MAIN APPLICATION LOOP
# ------------------------------------------------------------

eye = Eye()
panel = make_panel()

small_font = pygame.font.SysFont("segoeui,arial", 20, bold=True)
item_font = pygame.font.SysFont("segoeui,arial", 24, bold=True)
tiny_font = pygame.font.SysFont("segoeui,arial", 15, bold=True)
logo_small = pygame.font.SysFont("impact,arialblack,arial", 44)
logo_big = pygame.font.SysFont("impact,arialblack,arial", 88)
big_font = pygame.font.SysFont("georgia", 66, bold=True)

logo_1 = spaced_text("OPERATION:", logo_small, cream, 5)
logo_1_shadow = spaced_text("OPERATION:", logo_small, (0, 0, 0), 5)
logo_2 = spaced_text("OVERWATCH", logo_big, cream, 4)
logo_2_shadow = spaced_text("OVERWATCH", logo_big, (0, 0, 0), 4)
tagline = spaced_text("THE PERIMETER MUST HOLD", tiny_font, (150, 160, 170), 4)
esc_hint = spaced_text("[ESC] EXIT", tiny_font, (130, 140, 150), 2)

items = [
    MenuItem("PLAY", 340, item_font),
    MenuItem("HOW TO PLAY", 394, item_font),
    MenuItem("SETTINGS", 448, item_font),
    MenuItem("EXIT", 502, item_font),
]
selected = 0

eye_surface = pygame.Surface((width, height))
cover = pygame.Surface((width, height))
cover.fill((0, 0, 0))

state = "intro"
look_keys = [(-14, -2), (14, 2), (-12, 0), (12, -1), (0, 0)]
look_step = 0.55
look_time = 0.0
zoom_amount = 0.0
zoom_time = 3.0
max_zoom = 25
fade = 0
game = Game()

running = True
while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)
    choice = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        if state == "game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "menu"
                continue
            game.handle_event(event)
            continue

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state in ("how_to_play", "settings"):
                state = "menu"
            else:
                running = False
            continue

        if state == "intro":
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = "look"
                look_time = 0.0
            elif event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
                state = "look"
                look_time = 0.0

        elif state == "menu":
            if event.type == pygame.MOUSEMOTION:
                for i, item in enumerate(items):
                    if item.rect.collidepoint(event.pos):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for item in items:
                    if item.rect.collidepoint(event.pos):
                        choice = item.text
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = items[selected].text

        elif state in ("how_to_play", "settings"):
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                state = "menu"

    if choice == "PLAY":
        game.reset()
        state = "game"
    elif choice == "HOW TO PLAY":
        state = "how_to_play"
    elif choice == "SETTINGS":
        state = "settings"
    elif choice == "EXIT":
        running = False

    t = pygame.time.get_ticks() / 1000.0

    if state == "intro":
        eye.update(11 * math.sin(t * 0.6) + 4 * math.sin(t * 1.7),
                   3 * math.sin(t * 0.9))
        eye_surface.fill(bg_color)
        eye.draw(eye_surface)
        screen.blit(eye_surface, (0, 0))

        prompt = small_font.render("CLICK ANYWHERE TO ENTER", True, silver)
        prompt.set_alpha(int(140 + 115 * math.sin(t * 3)))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height - 50)))

    elif state == "look":
        look_time += dt
        index = int(look_time / look_step)
        goal = look_keys[index] if index < len(look_keys) else (0, 0)
        eye.update(goal[0], goal[1], 0.2)
        eye_surface.fill(bg_color)
        eye.draw(eye_surface)
        screen.blit(eye_surface, (0, 0))

        if look_time > look_step * len(look_keys) + 0.5:
            state = "zoom"

    elif state == "zoom":
        eye.update(0, 0, 0.2)
        eye_surface.fill(bg_color)
        eye.draw(eye_surface)

        zoom_amount = min(1, zoom_amount + dt / zoom_time)
        zoom = max_zoom ** zoom_amount
        piece_w = max(1, int(width / zoom))
        piece_h = max(1, int(height / zoom))
        pupil_x = int(eye.iris_x * eye.cell)
        pupil_y = int(eye.iris_y * eye.cell)
        left = max(0, min(width - piece_w, pupil_x - piece_w // 2))
        top = max(0, min(height - piece_h, pupil_y - piece_h // 2))
        piece = eye_surface.subsurface((left, top, piece_w, piece_h))
        screen.blit(pygame.transform.scale(piece, (width, height)), (0, 0))

        if zoom_amount > 0.6:
            cover.set_alpha(int(255 * (zoom_amount - 0.6) / 0.4))
            screen.blit(cover, (0, 0))

        if zoom_amount >= 1:
            state = "menu"
            fade = 255

    elif state == "menu":
        draw_menu_background(t, dt)
        screen.blit(panel, (0, 0))
        screen.blit(logo_1_shadow, (83, 123))
        screen.blit(logo_1, (80, 120))
        screen.blit(logo_2_shadow, (83, 173))
        screen.blit(logo_2, (80, 170))
        screen.blit(tagline, (84, 285))

        for i, item in enumerate(items):
            item.draw(screen, i == selected, dt)

        screen.blit(esc_hint, (width - esc_hint.get_width() - 30, height - 40))

        if fade > 0:
            fade = max(0, fade - 255 * dt)
            cover.set_alpha(int(fade))
            screen.blit(cover, (0, 0))

    elif state == "game":
        game.update(dt)
        game.draw(screen)

    elif state == "how_to_play":
        draw_menu_background(t, dt)
        screen.blit(panel, (0, 0))
        screen.blit(logo_1, (80, 100))
        heading = big_font.render("HOW TO PLAY", True, cream)
        screen.blit(heading, (80, 185))
        instructions = [
            "CLICK THE BATTLEFIELD TO DEPLOY AN ARCHER  -  50 FUNDS",
            "SELECT AN ARCHER, THEN PRESS U TO UPGRADE",
            "ARCHERS AUTOMATICALLY ATTACK ENEMIES IN RANGE",
            "PRESS N TO START THE NEXT WAVE EARLY",
            "EVERY 10 KILLS UNLOCKS DIVINE VOLLEY  -  SPACE",
            "PRESS P TO PAUSE  |  R TO RESTART  |  ESC FOR MENU",
        ]
        for i, line in enumerate(instructions):
            rendered = small_font.render(line, True, silver)
            screen.blit(rendered, (82, 300 + i * 42))
        hint = tiny_font.render("PRESS ANY KEY OR CLICK TO RETURN", True, GOLD)
        screen.blit(hint, (82, 590))

    elif state == "settings":
        draw_menu_background(t, dt)
        screen.blit(panel, (0, 0))
        screen.blit(logo_1, (80, 125))
        heading = big_font.render("SETTINGS", True, cream)
        screen.blit(heading, (80, 210))
        message = small_font.render("DISPLAY: 1280 x 720   |   FPS: 60", True, silver)
        screen.blit(message, (84, 330))
        hint = tiny_font.render("PRESS ANY KEY OR CLICK TO RETURN", True, GOLD)
        screen.blit(hint, (84, 390))

    pygame.display.flip()

pygame.quit()
sys.exit()
