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