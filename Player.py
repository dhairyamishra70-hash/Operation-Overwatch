# This would be the Archer class with it's own attributes and methods

import math

class player:

    def __init__(self,):

        self.x,self.y = Width // 2, Height// 2 
        self.helath = 200
        self.rect = pygame.rect(self.x - 25, self.y - 25,50,50)

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)
        pygame.draw.rect(surface, RED (self.x - 25, self.y- 30,50,5))
        pygame.draw.rect(surface, GREEN, (self.x - 25, self.y - 35, self.helath/2,5))
