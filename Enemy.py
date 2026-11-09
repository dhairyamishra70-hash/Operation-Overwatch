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
