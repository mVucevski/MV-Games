import numpy as np
import cv2 as cv
import math
import time

input = "video1.mp4"

def main():
    cap = cv.VideoCapture(input)

    if not cap.isOpened():
        print("Error loading stream or video.")
        cap.release()
        return

    cv.namedWindow("Dance Game")

    pFrameBGR = None

    while cap.isOpened():
        success, frameBGR = cap.read()

        if not success or cv.waitKey(1) == 27:
            break

        frameBGR = cv.pyrDown(frameBGR)

        if pFrameBGR is None:
            pFrameBGR = frameBGR
            continue

        pBlocks = divideImageInBlocks(pFrameBGR, 96, 96)
        blocks = divideImageInBlocks(frameBGR, 96, 96)
        masks = []
        for i in range(len(blocks)):
            masks.append(detectMotion(pBlocks[i], blocks[i]))
        movements = []
        for mask in masks:
            movements.append(cv.countNonZero(mask))
        print(movements)

        pFrameBGR = frameBGR

        cv.imshow("Dance Game", frameBGR)
        time.sleep(1 / 60)
    cap.release()


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


def divideImageInBlocks(frameBGR, blockWidth, blockHeight):
    height = frameBGR.shape[0]
    width = frameBGR.shape[1]
    blocks = []

    blocks.append(frameBGR[0:blockHeight, 0:blockWidth])
    blocks.append(frameBGR[0:blockHeight, int(width / 2 - blockWidth / 2):int(width / 2 + blockWidth / 2)])
    blocks.append(frameBGR[0:blockHeight, width - blockWidth:width])

    blocks.append(frameBGR[int(height / 2 - blockHeight / 2):int(height / 2 + blockHeight / 2), 0:blockWidth])
    blocks.append(frameBGR[int(height / 2 - blockHeight / 2):int(height / 2 + blockHeight / 2), int(width / 2 - blockWidth / 2):int(width / 2 + blockWidth / 2)])
    blocks.append(frameBGR[int(height / 2 - blockHeight / 2):int(height / 2 + blockHeight / 2), width - blockWidth:width])

    blocks.append(frameBGR[height - blockHeight:height, 0:blockWidth])
    blocks.append(frameBGR[height - blockHeight:height, int(width / 2 - blockWidth / 2):int(width / 2 + blockWidth / 2)])
    blocks.append(frameBGR[height - blockHeight:height, width - blockWidth:width])

    return blocks


if __name__ == "__main__":
    main()



