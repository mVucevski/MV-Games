import pygame
import math
import random

WIDTH = 640
HEIGHT = 480
DARKGRAY = (64, 64, 64)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
FPS = 60
DIR = [(0, 0), (0, HEIGHT/2), (0, HEIGHT), (WIDTH, 0), (WIDTH, HEIGHT/2), (WIDTH, HEIGHT), (WIDTH/2, 0), (WIDTH/2, HEIGHT)]

def load_image(image_name):
    try:
        image = pygame.image.load(image_name)
    except pygame.error:
        print('Cannot load image:', image_name)
        raise SystemExit()
    image = image.convert_alpha()
    return image

class Arrow:
    def __init__(self, image, position=(0, 0), pointTowards=(0, 0), speed=4):
        self.image = image
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
        surface.blit(self.image, (int(x), int(y)))

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
    def __init__(self, arrowImage):
        self.arrows = []
        self.circle = load_image("circle.png")
        self.arrowImage = arrowImage
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

        self.initGoalsArrows()


    def initGoalsArrows(self):

        center = (WIDTH / 2, HEIGHT / 2)
        img_size = self.arrowImage.get_size()

        # Left Direction Arrows
        arrow1 = Arrow(self.arrowImage, center, pointTowards=DIR[0], speed=0)
        arrow2 = Arrow(self.arrowImage, center, pointTowards=DIR[1], speed=0)
        arrow3 = Arrow(self.arrowImage, center, pointTowards=DIR[2], speed=0)

        arrow1.position = (arrow1.image.get_rect().center[0], arrow1.image.get_rect().center[1])
        arrow2.position = (arrow1.image.get_rect().center[0], HEIGHT // 2)
        arrow3.position = (arrow1.image.get_rect().center[0], HEIGHT - arrow1.image.get_rect().center[1])

        # Right Direction Arrows
        arrow4 = Arrow(self.arrowImage, center, pointTowards=DIR[3], speed=0)
        arrow5 = Arrow(self.arrowImage, center, pointTowards=DIR[4], speed=0)
        arrow6 = Arrow(self.arrowImage, center, pointTowards=DIR[5], speed=0)

        arrow4.position = (WIDTH - arrow1.image.get_rect().center[0], arrow1.image.get_rect().center[1])
        arrow5.position = (WIDTH - arrow1.image.get_rect().center[0], HEIGHT // 2)
        arrow6.position = (WIDTH - arrow1.image.get_rect().center[0], HEIGHT - arrow1.image.get_rect().center[1])

        # Up & Down Arrows
        arrow7 = Arrow(self.arrowImage, center, pointTowards=DIR[6], speed=0)
        arrow8 = Arrow(self.arrowImage, center, pointTowards=DIR[7], speed=0)

        arrow7.position = (WIDTH//2, arrow1.image.get_rect().center[1])
        arrow8.position = (WIDTH//2, HEIGHT - arrow1.image.get_rect().center[1])


        self.goalsArrows = [arrow1, arrow2, arrow3, arrow4, arrow5, arrow6, arrow7, arrow8]

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

        surface.blit(self.circle, (int(WIDTH/2-self.circle.get_rect().center[0]), int(HEIGHT/2-self.circle.get_rect().center[1])))

        for box in self.collisionBoxes:
            box = (int(box[0]), int(box[1]), box[2], box[3])
            pygame.draw.rect(surface, RED, box, 1)

        for goal in self.goalsArrows:
            goal.draw(surface)

        score = self.font.render(str(self.score), 1, WHITE)
        surface.blit(score, (int(WIDTH/2-score.get_rect()[2]/2), int(HEIGHT/2-score.get_rect()[3]/3)))

def main():
    pygame.init()
    fpsClock = pygame.time.Clock()
    delta = 0
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Dance Game')

    arrow_image = load_image("arrow.png")
    scene = Scene(arrow_image)

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
                c = random.choice(DIR)
                arrow = Arrow(arrow_image, (WIDTH / 2, HEIGHT / 2), c)
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