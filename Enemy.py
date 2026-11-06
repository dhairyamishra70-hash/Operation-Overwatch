# This would be the Enemy class with it's own attributes and methods

import math
import random

class Enemy:
    def __init__(self, wave_multiplier):

        if random.choice([True,False]):
            self.x = random.choice([0, Width])
            self.y = random.choice([0, Height])

        else:
            self.x = random.randint(0, Width)
            self.y = random.choice([0, Height])


        self.health =  20 + (wave.multiplier*5)
        self.speed = 1 + (wave_multiplier*0.5)
        self.damage = 10
        self.reward = 10

        def draw (self, target_x, target_y):
            angle = math.atan2(target_y - self.y, target_x - self.x)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed

        def draw(self, surface):
                    pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), 10)

