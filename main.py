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

            