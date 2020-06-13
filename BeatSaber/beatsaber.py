import pygame
import cv2 as cv
import random
import math
import colorsys
import numpy as np
from VideoGet import VideoGet

WIDTH = 640
HEIGHT = 480
FPS = 60

DARKGRAY = (64, 64, 64)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

INPUT = 0

ARROW = pygame.image.load("arrow.png")

MOUSEPOS = None
MOUSELCLICK = False

class Box:
    def __init__(self, image, position, color, type, rotation=0, speed=4):
        self.image = pygame.transform.rotate(image, rotation)
        self.position = position
        self.color = color
        self.type = type
        self.rotation = rotation
        self.speed = speed
        self.size = max(self.image.get_rect()[2], self.image.get_rect()[3]) + 32

    def draw(self, surface):
        x, y, w, h = self.image.get_rect()
        x = self.position[0] - w/2
        y = self.position[1] - h/2
        pygame.draw.rect(surface, self.color, self.get_rect())
        surface.blit(self.image, (x, y))


    def get_rect(self):
        x, y, w, h = self.image.get_rect()
        x = self.position[0] - w / 2
        y = self.position[1] - h / 2
        return (x-(self.size-w)/2, y-(self.size-h)/2, self.size, self.size)

    def update(self):
        x, y = self.position
        self.position = (x, y+self.speed)

    def outOfBounds(self):
        return self.position[1] > HEIGHT + self.size/2


class Scene:
    def __init__(self):
        self.boxes = []
        self.score = 0
        self.font = pygame.font.Font('freesansbold.ttf', 32)

    def draw(self, surface):
        for box in self.boxes:
            box.draw(surface)

        score = self.font.render(str(self.score), 1, RED)
        surface.blit(score, (int(WIDTH / 2 - score.get_rect()[2] / 2), int(score.get_rect()[3] / 2)))
        self.drawFixedLine(surface)

    def update(self, centers, directions):
        for box in self.boxes:
            box.update()
            if box.outOfBounds():
                self.score -= 10
                self.boxes.remove(box)

        if centers is None or directions is None:
            return

        for i in range(len(centers)):
            center = centers[i]
            direction = directions[i]

            if center is None or direction is None:
                continue

            for box in self.boxes:
                #if pointInRectangle(center, box.get_rect()) and direction == box.rotation and box.type == i and box.position[1] >= HEIGHT*3/4:
                if direction == box.rotation and box.type == i and box.position[1] >= HEIGHT * 3 / 4:
                    self.score += 10
                    self.boxes.remove(box)


    def spawnBox(self, position, color, type, direction):
        self.boxes.append(Box(ARROW, position, color, type, direction))

    def drawFixedLine(self, screen):
        pygame.draw.line(screen, RED, (0, HEIGHT * 3 / 4), (WIDTH, HEIGHT * 3 / 4))

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


def cvimage_to_pygame(image):
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = cv.resize(image, (WIDTH, HEIGHT))
    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")


def main():
    colors = chooseColors(2)
    runGame(colors)


def runGame(hsvcolors):
    pygame.init()
    fpsClock = pygame.time.Clock()
    delta = 0
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Dance Game')

    video_getter = VideoGet(INPUT).start()

    if not video_getter.grabbed:
        print("Error loading stream or video.")
        #cap.release()
        video_getter.stream.release()
        video_getter.stop()
        return

    scene = Scene()

    spawnBoxTimer = 1
    pCenters = None

    rgbcolors = []
    for hsv in hsvcolors:
        rgb = colorsys.hsv_to_rgb( hsv[0] / 180, hsv[1] / 255, hsv[2] / 255)
        rgb = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        rgbcolors.append(rgb)

    print(hsvcolors)
    print(rgbcolors)

    while video_getter.stream.isOpened():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                video_getter.stream.release()
                video_getter.stop()
                return

        success, frameBGR = video_getter.grabbed, video_getter.frame

        if not success:
            pygame.quit()
            video_getter.stream.release()
            video_getter.stop()
            return

        if spawnBoxTimer > 0:
            spawnBoxTimer -= delta
            if spawnBoxTimer <= 0:
                position = random.choice([(WIDTH * 1 / 4, 0), (WIDTH * 3 / 4, 0)])
                direction = random.choice([0, 90, 180, 270])
                type = random.randint(0, 1)
                color = rgbcolors[type]
                scene.spawnBox(position, color, type, direction)
                spawnBoxTimer = random.randint(1000, 2000)

        surface.fill(DARKGRAY)

        frameBGR = cv.resize(frameBGR, (WIDTH, HEIGHT))
        frameBGR = cv.flip(frameBGR, 1)
        centers = getCenters(frameBGR, hsvcolors)
        cv.circle(frameBGR, centers[0], 8, (0, 0, 0), -1)
        cv.circle(frameBGR, centers[1], 8, (0, 0, 0), -1)

        img = cvimage_to_pygame(frameBGR)
        surface.blit(img, (0, 0))

        directions = getDirections(pCenters, centers, 50)
        scene.update(centers, directions)
        scene.draw(surface)

        pygame.display.update()
        pCenters = centers

        delta = fpsClock.tick(FPS)


def onMouse(event, x, y, flags, param):
    global MOUSEPOS, MOUSELCLICK

    MOUSEPOS = (x, y)
    if event == cv.EVENT_LBUTTONDOWN:
        MOUSELCLICK = True
    if event == cv.EVENT_LBUTTONUP:
        MOUSELCLICK = False

def drawPickedColorsBoxes(image, colors):
    cv.putText(image, "Please select 2 colors", (10,20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    if len(colors) > 0:
        cv.putText(image, "Color 1:", (10, 40), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        color1 = (int(colors[0][0]),int(colors[0][1]),int(colors[0][2]))
        cv.rectangle(image, (90, 25), (110, 45), color1, thickness=-1, lineType=1)
    if len(colors) > 1:
        cv.putText(image, "Color 2:", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        color2 = (int(colors[1][0]),int(colors[1][1]),int(colors[1][2]))
        cv.rectangle(image, (90, 45), (110, 65), color2, thickness=-1, lineType=1)

def chooseColors(numColors):
    global MOUSELCLICK

    cap = cv.VideoCapture(INPUT)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    cv.namedWindow("Choose Color")
    cv.setMouseCallback("Choose Color", onMouse)

    colors = []
    colorsBGR = []

    while cap.isOpened():
        success, frameBGR = cap.read()

        if not success or cv.waitKey(1) == 27:
            break

        frameBGR = cv.resize(frameBGR, (WIDTH, HEIGHT))
        frameBGR = cv.flip(frameBGR, 1)
        frameHSV = cv.cvtColor(frameBGR, cv.COLOR_BGR2HSV)
        frameHSVBlurred = cv.GaussianBlur(frameHSV, (11, 11), 0)

        drawPickedColorsBoxes(frameBGR, colorsBGR)

        if MOUSELCLICK:
            x = MOUSEPOS[0]
            y = MOUSEPOS[1]
            colors.append(frameHSVBlurred[y][x])
            colorsBGR.append(frameBGR[y][x])
            numColors -= 1
            MOUSELCLICK = False

            if numColors == 0:
                cv.destroyWindow("Choose Color")
                return colors

        cv.imshow("Choose Color", frameBGR)
    cap.release()
    return None


def segmentate(frameBGR, hsv, hueThr=25, satThr=25, valThr=25):
    frameHSV = cv.cvtColor(frameBGR, cv.COLOR_BGR2HSV)
    frameHSVBlurred = cv.GaussianBlur(frameHSV, (11, 11), 0)

    hue = hsv[0]
    sat = hsv[1]
    val = hsv[2]

    h1s, h1e, h2s, h2e = splitRange(hue, hueThr, 0, 180)
    s1s, s1e, s2s, s2e = splitRange(sat, satThr, 0, 255)
    v1s, v1e, v2s, v2e = splitRange(val, valThr, 0, 255)

    mask1 = cv.inRange(frameHSVBlurred, (h1s, s1s, v1s), (h1e, s1e, v1e))
    mask2 = cv.inRange(frameHSVBlurred, (h2s, s2s, v2s), (h2e, s2e, v2e))

    mask = cv.bitwise_or(mask1, mask2)

    return mask


def splitRange(value, threshold, rangeStart, rangeEnd):
    start1 = value - threshold
    end1 = value + threshold
    start2 = start1
    end2 = end1

    if start1 < rangeStart:
        start2 = rangeEnd+start1
        end2 = rangeEnd
        start1 = rangeStart
    if end1 > rangeEnd:
        start2 = rangeStart
        end2 = end1-rangeEnd
        end1 = rangeEnd

    return int(start1), int(end1), int(start2), int(end2)


def getCenters(image, colors):

    centers = []

    for i in range(len(colors)):
        mask = segmentate(image, colors[i])
        cv.imshow("mask " + str(i), mask)
        contours = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[0]
        contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)

        center = None
        if contours.__len__() > 0:
            biggestContour = [contours[0]]
            center = getCenter(biggestContour)
        centers.append(center)

    return centers


def getCenter(contour, absolute=True):
    if absolute:
        sx = 0
        sy = 0
        for i in range(len(contour[0])):
            sx += contour[0][i][0][0]
            sy += contour[0][i][0][1]
        center = (int(sx / len(contour[0])), int(sy / len(contour[0])))
    else:
        x, y, w, h = cv.boundingRect(contour[0])
        center = (int(x+w/2), int(y+h/2))
    return center


def getDirections(prev, curr, minDistance = 10):
    if not prev or not curr:
        return None

    directions = []

    for i in range(len(curr)):
        if prev[i] is None or curr[i] is None:
            directions.append(None)
            continue
        x1 = prev[i][0]
        y1 = prev[i][1]
        x2 = curr[i][0]
        y2 = curr[i][1]

        if math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)) < minDistance:
            directions.append(None)
            continue

        dir = math.atan2(y2 - y1, x2 - x1)
        dir *= 180
        dir /= math.pi

        if dir >= -45 and dir < 45:
            directions.append(0)
        elif dir >= 45 and dir < 135:
            directions.append(270)
        elif dir >= -135 and dir < -45:
            directions.append(90)
        else:
            directions.append(180)
    return directions

if __name__ == "__main__":
    main()