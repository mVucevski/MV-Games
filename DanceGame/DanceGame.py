import pygame
import math
import random

WIDTH = 640
HEIGHT = 480
DARKGRAY = (64, 64, 64)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FPS = 60

class Arrow:
    def __init__(self, image, position=(0, 0), pointTowards=(0, 0), speed=4):
        self.image = pygame.image.load(image)
        self.position = position
        self.rotation = math.atan2(-pointTowards[1]+position[1], pointTowards[0]-position[0])
        self.image = pygame.transform.rotate(self.image, self.rotation*180/math.pi)
        self.speed = speed

    def update(self):
        x = self.speed * math.cos(self.rotation)
        y = -self.speed * math.sin(self.rotation)
        self.position = (self.position[0] + x, self.position[1] + y)

    def draw(self, surface):
        x = self.position[0] - self.image.get_rect().center[0]
        y = self.position[1] - self.image.get_rect().center[1]
        surface.blit(self.image, (x, y))

    def outOfBounds(self):
        if self.position[0] < -self.image.get_rect().center[0]:
            return True
        if self.position[1] < -self.image.get_rect().center[1]:
            return True
        if self.position[0] >= WIDTH + self.image.get_rect().center[0]:
            return True
        if self.position[1] >= HEIGHT + self.image.get_rect().center[1]:
            return True
        return False


def pointInRectangle(point, rectangle):
    px = point[0]
    py = point[1]
    rx = rectangle[0]
    ry = rectangle[1]
    w = rectangle[2]
    h = rectangle[3]

    if px >= rx and py >= ry and px < rx+w and py < ry+h:
        return True
    return False

class Scene:
    def __init__(self):
        self.arrows = []
        self.circle = pygame.image.load("circle.png")
        self.circle = pygame.transform.scale(self.circle, (128, 128))
        self.collisionBoxes = []
        self.score = 0
        self.font = pygame.font.Font('freesansbold.ttf', 32)

        boxWidth = 96
        boxHeight = 96

        self.collisionBoxes.append((0, 0, boxWidth, boxHeight))
        self.collisionBoxes.append((WIDTH/2-boxWidth/2, 0, boxWidth, boxHeight))
        self.collisionBoxes.append((WIDTH - boxWidth, 0, boxWidth, boxHeight))

        self.collisionBoxes.append((0, HEIGHT / 2 - boxHeight / 2, boxWidth, boxHeight))
        self.collisionBoxes.append((WIDTH - boxWidth, HEIGHT / 2 - boxHeight / 2, boxWidth, boxHeight))

        self.collisionBoxes.append((0, HEIGHT - boxHeight, boxWidth, boxHeight))
        self.collisionBoxes.append((WIDTH / 2 - boxWidth / 2, HEIGHT - boxHeight, boxWidth, boxHeight))
        self.collisionBoxes.append((WIDTH - boxWidth, HEIGHT - boxHeight, boxWidth, boxHeight))

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def update(self, mousePos):
        for arrow in self.arrows:
            arrow.update()
            if arrow.outOfBounds():
                self.arrows.remove(arrow)
                self.score -= 10
            if mousePos is not None:
                for cb in self.collisionBoxes:
                    if pointInRectangle(arrow.position, cb) and pointInRectangle(mousePos, cb):
                        self.arrows.remove(arrow)
                        self.score += 10

    def draw(self, surface):
        for arrow in self.arrows:
            arrow.draw(surface)

        surface.blit(self.circle, (WIDTH/2-self.circle.get_rect().center[0], HEIGHT/2-self.circle.get_rect().center[1]))

        for box in self.collisionBoxes:
            pygame.draw.rect(surface, RED, box, 1)

        score = self.font.render(str(self.score), 1, WHITE)
        surface.blit(score, (WIDTH/2-score.get_rect()[2]/2, HEIGHT/2-score.get_rect()[3]/3))

def main():
    pygame.init()
    fpsClock = pygame.time.Clock()
    delta = 0
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Dance Game')

    scene = Scene()

    arrowTimer = 1

    while True:
        mousePos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()

        if arrowTimer > 0:
            arrowTimer -= delta
            if arrowTimer <= 0:
                c = random.choice(
                    [(0, 0), (WIDTH / 2, 0), (WIDTH, 0), (0, HEIGHT / 2), (WIDTH, HEIGHT / 2), (0, HEIGHT),
                     (WIDTH / 2, HEIGHT), (WIDTH, HEIGHT)])
                arrow = Arrow("arrow.png", (WIDTH / 2, HEIGHT / 2), c)
                scene.addArrow(arrow)
                arrowTimer = random.randint(1000, 2000)

        surface.fill(DARKGRAY)

        scene.update(mousePos)
        scene.draw(surface)
        pygame.display.update()

        mousePos = None
        delta = fpsClock.tick(FPS)

if __name__ == "__main__":
    main()