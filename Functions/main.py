import numpy as np
import cv2 as cv
import math
import time

input = "video1.mp4"

LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"
NONE = "NONE"

mousePosition = (0, 0)
mouseLeftClick = False

def main():
    testMotionDetection()
    #testColorExtractionAndSegmentation()


def testMotionDetection():
    cap = cv.VideoCapture(input)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    cv.namedWindow("Motion Detection")

    pFrameBGR = None
    pCenter = None

    while cap.isOpened():
        success, frameBGR = cap.read()

        if not success or cv.waitKey(1) == 27:
            break

        frameBGR = cv.pyrDown(frameBGR)

        if pFrameBGR is None:
            pFrameBGR = frameBGR
            continue

        contours = detectMotion(pFrameBGR, frameBGR)

        contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)
        biggestContour = []

        result = frameBGR
        if len(contours) > 0:
            biggestContour.append(contours[0])
            x, y, w, h = cv.boundingRect(biggestContour[0])
            cv.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv.circle(result, getCenter(biggestContour), 8, (0, 255, 0), 3)
            cv.circle(result, getCenter(biggestContour, False), 8, (255, 0, 0), 3)

            center = getCenter(biggestContour)
            print(getDirection(pCenter, center))
            pCenter = center

        pFrameBGR = frameBGR

        cv.imshow("Motion Detection", result)
        time.sleep(1 / 60)
    cap.release()


def testColorExtractionAndSegmentation():
    hsv = extractColor()
    segmentateColor(hsv)


def detectMotion(previousFrameBGR, currentFrameBGR, sensitivity=25, noiseDampening=2):
    prev = cv.cvtColor(previousFrameBGR, cv.COLOR_BGR2GRAY)
    prev = cv.GaussianBlur(prev, (21, 21), 0)
    curr = cv.cvtColor(currentFrameBGR, cv.COLOR_BGR2GRAY)
    curr = cv.GaussianBlur(curr, (21, 21), 0)

    delta = cv.absdiff(prev, curr)
    thresh = cv.threshold(delta, sensitivity, 255, cv.THRESH_BINARY)[1]

    thresh = cv.erode(thresh, None, iterations=noiseDampening)
    thresh = cv.dilate(thresh, None, iterations=noiseDampening)
    contours = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[0]

    return contours


def onMouse(event, x, y, flags, param):
    global mousePosition, mouseLeftClick

    mousePosition = (x, y)
    if event == cv.EVENT_LBUTTONDOWN:
        mouseLeftClick = True
    if event == cv.EVENT_LBUTTONUP:
        mouseLeftClick = False


def extractColor():
    global mouseLeftClick

    cap = cv.VideoCapture(input)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    cv.namedWindow("Extract Color")
    cv.setMouseCallback("Extract Color", onMouse)

    while cap.isOpened():
        success, frameBGR = cap.read()

        if not success or cv.waitKey(1) == 27:
            break

        frameBGR = cv.pyrDown(frameBGR)
        frameHSV = cv.cvtColor(frameBGR, cv.COLOR_BGR2HSV)
        frameHSVBlurred = cv.GaussianBlur(frameHSV, (11, 11), 0)

        x = mousePosition[0]
        y = mousePosition[1]

        if mouseLeftClick:
            cv.destroyWindow("Extract Color")
            return frameHSVBlurred[y][x]

        cv.imshow("Extract Color", frameBGR)
        time.sleep(1 / 60)
    cap.release()
    return None


def segmentateColor(hsv):
    cap = cv.VideoCapture(input)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    cv.namedWindow("Segmentate Color")

    pCenter = None

    while cap.isOpened():
        success, frameBGR = cap.read()

        if not success or cv.waitKey(1) == 27:
            break

        frameBGR = cv.pyrDown(frameBGR)
        contours = segmentate(frameBGR, hsv)

        contours = sorted(contours, key=lambda x: cv.contourArea(x), reverse=True)
        biggestContour = []

        result = frameBGR
        if len(contours) > 0:
            biggestContour.append(contours[0])
            x, y, w, h = cv.boundingRect(biggestContour[0])
            cv.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 3)
            cv.circle(result, getCenter(biggestContour), 8, (0, 255, 0), 3)
            cv.circle(result, getCenter(biggestContour, False), 8, (255, 0, 0), 3)

            center = getCenter(biggestContour)
            print(getDirection(pCenter, center))
            pCenter = center

        cv.imshow("Segmentate Color", result)
        time.sleep(1 / 60)
    cap.release()


def segmentate(frameBGR, hsv, hueThr=25, satThr=50, valThr=100):
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

    contours = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[0]

    return contours


def getDirection(prev, curr, minDistance = 10):
    if prev is None or curr is None:
        return NONE

    x1 = prev[0]
    y1 = prev[1]
    x2 = curr[0]
    y2 = curr[1]

    if math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)) < minDistance:
        return NONE

    dir = math.atan2(y2-y1, x2-x1)
    dir *= 180
    dir /= math.pi

    if dir >= -45 and dir < 45:
        return RIGHT
    elif dir >= 45 and dir < 135:
        return DOWN
    elif dir >= -135 and dir < -45:
        return UP
    else:
        return LEFT


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


if __name__ == "__main__":
    main()



