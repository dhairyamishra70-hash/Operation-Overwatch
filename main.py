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

# colors I use a lot
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
# setup
# ------------------------------------------------------------

eye = Eye()
panel = make_panel()

small_font = pygame.font.SysFont("segoeui,arial", 20, bold=True)
item_font = pygame.font.SysFont("segoeui,arial", 24, bold=True)
tiny_font = pygame.font.SysFont("segoeui,arial", 15, bold=True)
logo_small = pygame.font.SysFont("impact,arialblack,arial", 44)
logo_big = pygame.font.SysFont("impact,arialblack,arial", 88)
big_font = pygame.font.SysFont("georgia", 66, bold=True)

# the logo, drawn once (a dark copy a bit lower-right gives it a shadow)
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

# the eye is drawn on its own surface so we can zoom into it
eye_surface = pygame.Surface((width, height))
cover = pygame.Surface((width, height))      # black sheet for fading
cover.fill((0, 0, 0))

state = "intro"      # intro -> look -> zoom -> menu -> game

# the pupil looks around, then goes back to the middle
look_keys = [(-14, -2), (14, 2), (-12, 0), (12, -1), (0, 0)]
look_step = 0.55     # seconds for each look
look_time = 0.0

zoom_amount = 0.0    # goes from 0 to 1 during the zoom
zoom_time = 3.0      # seconds the zoom takes
max_zoom = 25        # how close we get at the end
fade = 0             # 255 = all black, 0 = normal

running = True
while running:
    dt = clock.tick(60) / 1000   # seconds since last frame
    choice = None                # which menu item got picked this frame

    # ----- events -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if state == "game":
                state = "menu"
            else:
                running = False

        if state == "intro":
            # any click or key starts the looking around
            if event.type == pygame.MOUSEBUTTONDOWN:
                state = "look"
                look_time = 0.0
            if event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE:
                state = "look"
                look_time = 0.0

        elif state == "menu":
            # mouse
            if event.type == pygame.MOUSEMOTION:
                for i in range(len(items)):
                    if items[i].rect.collidepoint(event.pos):
                        selected = i
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for item in items:
                    if item.rect.collidepoint(event.pos):
                        choice = item.text
            # keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % len(items)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected = (selected + 1) % len(items)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    choice = items[selected].text

    if choice == "PLAY":
        state = "game"
    elif choice == "EXIT":
        running = False
    # TODO: HOW TO PLAY and SETTINGS pages

    t = pygame.time.get_ticks() / 1000

    # ----- drawing -----
    if state == "intro":
        # the pupil wanders left and right by itself
        eye.update(11 * math.sin(t * 0.6) + 4 * math.sin(t * 1.7), 3 * math.sin(t * 0.9))
        eye_surface.fill(bg_color)
        eye.draw(eye_surface)
        screen.blit(eye_surface, (0, 0))

        # blinking text at the bottom
        prompt = small_font.render("CLICK ANYWHERE TO ENTER", True, silver)
        prompt.set_alpha(int(140 + 115 * math.sin(t * 3)))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height - 50)))

    elif state == "look":
        # quick looks left and right, then back to the middle
        look_time += dt
        index = int(look_time / look_step)
        if index < len(look_keys):
            goal = look_keys[index]
        else:
            goal = (0, 0)
        eye.update(goal[0], goal[1], 0.2)

        eye_surface.fill(bg_color)
        eye.draw(eye_surface)
        screen.blit(eye_surface, (0, 0))

        # when it is back in the middle (plus a short pause) the zoom starts
        if look_time > look_step * len(look_keys) + 0.5:
            state = "zoom"

    elif state == "zoom":
        eye.update(0, 0, 0.2)
        eye_surface.fill(bg_color)
        eye.draw(eye_surface)

        zoom_amount += dt / zoom_time
        if zoom_amount > 1:
            zoom_amount = 1
        zoom = max_zoom ** zoom_amount    # gets faster and faster

        # cut out a small piece around the pupil and stretch it to full screen
        piece_w = int(width / zoom)
        piece_h = int(height / zoom)
        pupil_x = int(eye.iris_x * eye.cell)
        pupil_y = int(eye.iris_y * eye.cell)
        left = pupil_x - piece_w // 2
        top = pupil_y - piece_h // 2
        left = max(0, min(width - piece_w, left))     # stay inside the screen
        top = max(0, min(height - piece_h, top))
        piece = eye_surface.subsurface((left, top, piece_w, piece_h))
        screen.blit(pygame.transform.scale(piece, (width, height)), (0, 0))

        # fade to black at the end
        if zoom_amount > 0.6:
            cover.set_alpha(int(255 * (zoom_amount - 0.6) / 0.4))
            screen.blit(cover, (0, 0))

        if zoom_amount >= 1:
            state = "menu"
            fade = 255

    elif state == "menu":
        draw_menu_background(t, dt)
        screen.blit(panel, (0, 0))

        # logo + tagline
        screen.blit(logo_1_shadow, (83, 123))
        screen.blit(logo_1, (80, 120))
        screen.blit(logo_2_shadow, (83, 173))
        screen.blit(logo_2, (80, 170))
        screen.blit(tagline, (84, 285))

        # menu
        for i in range(len(items)):
            items[i].draw(screen, i == selected, dt)

        screen.blit(esc_hint, (width - esc_hint.get_width() - 30, height - 40))

        # fade in from black (takes 1 second)
        if fade > 0:
            fade -= 255 * dt
            if fade < 0:
                fade = 0
            cover.set_alpha(int(fade))
            screen.blit(cover, (0, 0))

    elif state == "game":
        screen.fill((6, 12, 20))
        text = big_font.render("GAME STARTS HERE", True, cream)
        screen.blit(text, text.get_rect(center=(width // 2, height // 2)))
        note = small_font.render("(teammates add their game here - ESC goes back)", True, (150, 160, 170))
        screen.blit(note, note.get_rect(center=(width // 2, height // 2 + 70)))

    pygame.display.flip()

pygame.quit()
sys.exit()


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
    "grunt":  {"health": 35,  "speed": 60,  "damage": 20, "reward": 5, "radius": 10, "color": (200, 70, 70)},
    "runner": {"health": 70,  "speed": 150, "damage": 25,  "reward": 10, "radius": 8,  "color": (230, 150, 40)},
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
class Enemy:

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
        bar = pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius - 7, w, 4)
        pygame.draw.rect(screen, GREY, bar)
        bar.width = max(0, int(w*self.health / self.max_health))
        pygame.draw.rect(screen, GREEN, bar)
 # Arrow 
class Arrow:
            SPEED = 450

            def __init__(self, x, y,target,damage):
                self.x = x
                self.y = y
                self.target = target
                self.damage = damage
                self.alive = True

            def update(self, dt):

                if self.target_is_dead():
                    self.alive = False
                    return

                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = math.hypot(dx, dy)
                step = self.SPEED * dt

                if dist <= step + self.target.radius:
                    self.target.health -= self.damage
                    self.alive = False

                else:
                    self.x += dx/dist*step
                    self.y += dy / dist*step

            def draw(self, screen):
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)),  3)

# Archer

class Archer:
    def __init__(self,x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.damage = 12
        self.range = 100
        self.cooldown = 0.8
        self.timer = 0.0


    @property
    def upgrade_cost(self):
        return 40 * self.level

    def upgrade(self):
        self.level += 1
        self.damage = round(self.damage * 1.2, 1)
        self.range += 12
        self.cooldown =  max(0.25, self.cooldown * 0.92)

    def update (self, dt, enemies, arrows):
        self.timer -= dt
        if self.timer > 0:
            return

        target = None
        best = self.range  + 1
        for enemy in enemies:
            d = distance(self.x, self.y, enemies.x, enemy.y)
            if d <= self.range and d < best:
                best = d
                target = enemy

            if target is not None:
                arrows.append(Arrow(self.x, self.y, target, self.damage))
                self.timer = self.cooldown


    def draw(self, screen, font, selected = False):
        if selected:
            ring = pygame.Surface((self.range * 2, self.range *2 ), pygame.SRCALPHA)
            pygame.draw.circle(ring, (255, 255, 255, 40), (self.range, self.range), self.range)
            pygame.draw.circle(ring, (255, 255, 255, 255, 120),  (self.range, self.range), self.range, 2)

            screen.blit(ring, (self.x - self.range, self.y - self.range))
            pygame.draw.circle(screen, BLUE, (self.x, self.y), 14)
            pygame.draw.circle(screen, GOLD if selected else BLACK, (self.x, self.y), 14, 2)
            label = font.render(str(self.level), True, WHITE)
            screen.blit(label, label.get_rect(center=(self.x, self.y)))






#  Game Systems
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Operation Overwatch")
        self.clock = pygame.time.clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.big_font = pygame.font.SysFont("consolas", 56, bold= True)

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
        self.countdown = INTERMISSION_TIME
        self.spawn_queue = []
        self.spawn_timer = 0.0
        self.selected = None
        self.message = ""
        self.message_timer = 0.0
        self.flash =  0.0

    def say(self, text):
        self.message =  text
        self.message_timer = 2.0


    def start_wave(self):
        self.wave += 1
        self.wave_active = True
        count = 4 + 2 * self.wave
        kinds = ["grunt"]
        weights = [15]
        if self.wave >= 2:
            kinds.append("runner")
            weights.append(3)
        if self.wave >= 3:
            kinds.append("brute")
            weights.append(1 + self.wave // 3)

        self.spawn.queue = random.choices(kinds,weights, k=count)
        self.spawn_timer = 0.0

    def update_waves(self, dt):
        if not self.wave_active:
            self.countdown -= dt
            if self.spawn.timer <= 0:
                self.enemies.append(Enemy(self.spawn_queue.pop(), self.wave))
                self.spawn_timer = max(0.4, 1.3 - 0.06 *self.wave)

        elif not self.enemies:
            bonus = 20 + 5 * self.wave
            self.funds +=  bonus
            self.say(f"Wave {self.wave} cleared ! + {bonus} funds")
            self.countdown = INTERMISSION_TIME

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
        if self.killstreak <KILLSTREAK_NEEDED:
            self.say(f"Killstreak {self.killstreak}/{KILLSTREAK_NEEDED} - not ready")
            return
        for enemy in self.enemies:
            enemy.health -= VOLLEY_DAMAGE

        self.collect_dead_enemies()
        self.killstreak = 0
        self.flash = 0.25
        self.say("Divine Volley !")


    def handle_click(self, pos):
        x,y = pos
        if y < HUD_HEIGHT or y > HEIGHT - FOOTER_HEIGHT:
            return

        for archer in self.archers:
            if distance(x,y, archer.x, archer.y) <= 16:
                self.selected = archer
                return

        if x > self.base.rect.left - 20:
            self.say("Too close to the base !")
        elif any(distance(x,y, a.x,a.y)  <32 for a in self.archers):
            self.say("Too close to another archer !")
        elif self.funds < ARCHER_COST:
            self.say("Not enough funds !")

        else:
            self.archer -= ARCHER_COST
            new_archer = archer(x, y)
            self.archers.append(new_archer)
            self.selected = new_archer


    def upgrade_selected(self):
        archer =  self.selected
        if archer is None:
            self.say("Select an archer !")

        elif archer.level >= MAX_ARCHER_LEVEL:
            self.say("Archer is ready max level !")

        elif self.funds < archer.upgrade_cost:
            self.say(f"Need {archer.ipgrade_cost} funds to upgrade")

        else:
            self.funds -= archer.upgrade.cost
            archer.upgrade()


    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

        if self.flash > 0:
            self.flash -= dt

        if self.state != "playing":
            return


        self.update_waves(dt)


        stil_walking = []
        for enemy in self.enemies:
            enemy.update(dt, self.base)

            if enemy.reached_base(self.base):
                self.base.take_damage(enemy.damage)
                self.kilstreak = 0

            else:
                still_walking.append(enemy) 

        self.enemies = stil_walking


        for archer in self.archers:
            archer.update(dt, self.enemies, self.arrows)

        for arrow in self.arrows:
            arrow.update(dt)
        self.arrows = [a for a in self.arrows if a.alive]

        self.collect_dead_enemies()

        if self.base.is_destroyed():
            self.state = "game over"



    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center = (WIDTH // 2)))


    def draw_hud(self):
        pygame.draw.rect(self.screen,  (25, 25, 30), (0, 0, WIDTH, HUD_HEIGHT))
        text = (f"Wave: {self.wave} | Funds: {self.funds} | "
                f"Base HP: {self.base.health} | "
                f"Killstreak: {self.killstreak}/{KILLSTREAK_NEEDED}")

        self.screen.blit(self.font.render(text, True, WHITE), (12, 10))
        if self.killstreak >= KILLSTREAK_NEEDED:
            ready = self.font.render("Space: Volley Ready !", True, GOLD)
            self.screen.blit(ready, (WIDTH - ready.get_width() - 12, 10))


        pygame.draw.rect(self.screen, (25, 25, 30), (0,HEIGHT - FOOTER_HEIGHT, WIDTH, FOOTER_HEIGHT))

        if self.selected:
            a = self.selected
            info = (f"Archer Level{a.level} damage{a.damage} range{a.range} "
                    f"| U: upgrade ({a.upgrade_cost if a.level  <MAX_ARCHER_LEVEL else 'MAX'})")

        else: 
            info = f"Click ground: place Archer ({ARCHER_COST}) | P: Pause | N: Next Wave | R: Restart"
            self.screen.blit(self.small_font.render(info, True, WHITE), (12, HEIGHT - FOOTER_HEIGHT + 6))

        if not self.wave_active and self.active and self.state == "playing":
            self.draw._text_center(f"{self.wave + 1} in {max(0, math.ceil(self.countdown))} (N to start now)"
                                   , self.font, GOLD, HUD_HEIGHT + 20)

        if self.message_timer > 0:
            self.draw_text_center(self.message, self.font, WHITE, HUD_HEIGHT + 50)

        def draw(self):
            self.screen.fill(GRASS)
            self.base.draw(self.screen)
            for archer in self.archers:
                archer.draw(self.screen, self.small_font, archer is self.selected)

            for enemy in self.enemies:
                enemy.draw(self.screen, self.small_font, archer is self.selected)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            for arrow in self.arrows:
                arrow.draw(self.screen)
            self.draw_hud()

            if self.flash > 0:
                overlay =  pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
                overlay.fill((255, 255, 200, int(255 * self.flash / 0.25 * 0.6)))
                self.screen.blit(overlay, (0,0))

            if self.state == "Paused":
                self.dim_screen()
                self.draw_text_center("PAUSED", self.big_font, WHITE, HEIGHT // 2)
                self.draw_text_center("Press P to resume", self.font, WHITE, HEIGHT // 2 + 50)

            elif self.state == "game over":
                self.dim.screen()
                self.draw_text_center("SECTOR LOST", self.big_font, RED, HEIGHT // 2 - 30)
                self.draw_text_center(f"You reached wave {self.wave} with {self.kills} kills", 
                                      self.font, WHITE, HEIGHT // 2 + 25)

                self.draw_text_center("Press R to restart", self.font, GOLD, HEIGHT // 2 + 60)

            pygame.display.flip()

        def dim_screen(self):
              overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
              overlay.fill((0, 0, 0, 150)) 
              self.screen.blit(overlay, (0,0))


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
                        self.reset()

                        if self.state == "playing":
                            self.state == "paused"

                        elif self.state == "paused":
                            self.state == "playing"

                    elif self.state == "playing":
                        if event.key == pygame.K_SPACE:
                            self.use.volley()

                        elif event.key == pygame.K_n and not self.wave_active:
                            self.countdown = 0

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "playing":
                        self.handle_click(event.pos)

            return True

        def run(self):
            running = True
            while running:
                dt = self.clock.tick(FPS) / 1000.0
                dt = min(dt, 0.05)
                running = self.handel_events()
                self.update(dt)
                self.draw()

            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    Game().run()