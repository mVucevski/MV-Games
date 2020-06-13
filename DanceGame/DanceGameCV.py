import cv2 as cv
from VideoGet import VideoGet
from DanceGame import WIDTH, HEIGHT

input = 0

def initCV():
    cap = cv.VideoCapture(input)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    video_getter = VideoGet(input).start()

    return cap, video_getter

def mainCV(pFrameBGR, video_getter=None):
    success, frameBGR = video_getter.grabbed, video_getter.frame

    if not success:
        return

    frameBGR = cv.resize(frameBGR, (WIDTH, HEIGHT))

    if pFrameBGR is None:
        pFrameBGR = frameBGR.copy()

    cFrameBGR = frameBGR.copy()

    pFrameBGR = cv.flip(pFrameBGR, 1)
    cFrameBGR = cv.flip(cFrameBGR, 1)

    pBlocks = divideImageInBlocks(pFrameBGR, 96, 96)
    blocks = divideImageInBlocks(cFrameBGR, 96, 96)

    masks = []
    for i in range(len(blocks)):
        masks.append(detectMotion(pBlocks[i], blocks[i]))

    movements = []
    for mask in masks:
        movements.append(detectChange(mask))

    return frameBGR, movements

def detectChange(block, percentage=0.1):
    totalNumPixels = block.shape[0] * block.shape[1]
    requiredNumPixels = totalNumPixels * percentage
    nonZeroPixels = cv.countNonZero(block)

    if (nonZeroPixels >= requiredNumPixels):
        return True

    return False

def detectMotion(previousFrameBGR, currentFrameBGR, sensitivity=25, noiseDampening=2):
    prev = cv.cvtColor(previousFrameBGR, cv.COLOR_BGR2GRAY)
    prev = cv.GaussianBlur(prev, (21, 21), 0)
    curr = cv.cvtColor(currentFrameBGR, cv.COLOR_BGR2GRAY)
    curr = cv.GaussianBlur(curr, (21, 21), 0)

    delta = cv.absdiff(prev, curr)
    mask = cv.threshold(delta, sensitivity, 255, cv.THRESH_BINARY)[1]

    mask = cv.erode(mask, None, iterations=noiseDampening)
    mask = cv.dilate(mask, None, iterations=noiseDampening)

    return mask

def convertBGR2RGB(image):
    return cv.cvtColor(image, cv.COLOR_BGR2RGB)

def divideImageInBlocks(frameBGR, blockWidth, blockHeight):
    height = frameBGR.shape[0]
    width = frameBGR.shape[1]
    blocks = []

    # 0 1 2
    # 3   4
    # 5 6 7

    blocks.append(frameBGR[0:blockHeight, 0:blockWidth]) # 0
    blocks.append(frameBGR[0:blockHeight, int(width / 2 - blockWidth / 2):int(width / 2 + blockWidth / 2)]) # 1
    blocks.append(frameBGR[0:blockHeight, width - blockWidth:width]) # 2

    blocks.append(frameBGR[int(height / 2 - blockHeight / 2):int(height / 2 + blockHeight / 2), 0:blockWidth]) # 3
    blocks.append(frameBGR[int(height / 2 - blockHeight / 2):int(height / 2 + blockHeight / 2), width - blockWidth:width]) # 4

    blocks.append(frameBGR[height - blockHeight:height, 0:blockWidth])  # 5
    blocks.append(frameBGR[height - blockHeight:height, int(width / 2 - blockWidth / 2):int(width / 2 + blockWidth / 2)])  # 6
    blocks.append(frameBGR[height - blockHeight:height, width - blockWidth:width])  # 7

    return blocks





