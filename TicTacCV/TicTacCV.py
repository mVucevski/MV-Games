import cv2
import numpy as np
import time
from TicTacToe import TicTacToe

# CONSTANTS
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 360
WHITE = (255, 255, 255)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
gridRows = 3
gridCols = 3
TIMER_S = 1.5
END_SCREEN_S = 5
#tmp_matrix = np.arange(gridRows * gridCols).reshape((gridRows, gridCols))


def hasTimerPassed(startTime, passedSeconds):
    if time.time() - startTime >= passedSeconds:
        return True
    return False

def initCamera():
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, WINDOW_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_HEIGHT)
    return camera


def nothing(x):
    pass


def initTrackbars():
    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("LH", "Trackbars", 0, 255, nothing)
    cv2.createTrackbar("LS", "Trackbars", 92, 255, nothing)
    cv2.createTrackbar("LV", "Trackbars", 18, 255, nothing)
    cv2.createTrackbar("UH", "Trackbars", 25, 255, nothing)
    cv2.createTrackbar("US", "Trackbars", 255, 255, nothing)
    cv2.createTrackbar("UV", "Trackbars", 117, 250, nothing)


def getTrackBarsValues():
    l_h = cv2.getTrackbarPos("LH", "Trackbars")
    l_s = cv2.getTrackbarPos("LS", "Trackbars")
    l_v = cv2.getTrackbarPos("LV", "Trackbars")

    u_h = cv2.getTrackbarPos("UH", "Trackbars")
    u_s = cv2.getTrackbarPos("US", "Trackbars")
    u_v = cv2.getTrackbarPos("UV", "Trackbars")

    return [l_h, l_s, l_v], [u_h, u_s, u_v]


def extractSkinFromImage(image, lower_bound, upper_bound):
    mask = cv2.inRange(image, lower_bound, upper_bound)

    blurMask = cv2.medianBlur(mask, 25)
    mask1 = cv2.morphologyEx(blurMask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask1 = cv2.morphologyEx(mask1, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))

    result1 = cv2.bitwise_and(image, image, mask=mask1)
    result1 = cv2.cvtColor(result1, cv2.COLOR_HSV2BGR)

    kernel = np.ones((5, 5), np.uint8) / 25
    mask2 = cv2.erode(mask1, kernel, iterations=2)
    mask2 = cv2.dilate(mask2, kernel, iterations=2)

    result = cv2.bitwise_and(result1, result1, mask=mask2)
    return result

def divideImageInBlocks(image, rows = 2, cols = 2, drawLines = False):
    height = image.shape[0]
    width = image.shape[1]
    blockList = list()

    for i in range(rows):
        for j in range(cols):
            block = image[int(i*height/rows):int(i*height/rows+height/rows), int(j*width/cols):int(j *width/cols+width/cols)]
            #cv2.imshow("Block: " + str(i) + str(j), block)
            if drawLines:
                cv2.line(image, (int(i*width/cols+width/cols), 0), (int(i*width/cols+width/cols), height), color=WHITE, lineType=cv2.LINE_AA, thickness=1)
            blockList.append(block)
        if drawLines:
            cv2.line(image, (0, int(i * height / rows + height / rows)), (width, int(i * height / rows + height / rows)), color=WHITE, lineType=cv2.LINE_AA, thickness=1)
    return blockList

# If the block fulfills the requirement for activation, return the number of non-black pixels in the block
# If not returns 0
def isBlockPressed(block, triggerPercentage = 0.5):
    grayBlock = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    totalNumPixels = grayBlock.shape[0] * grayBlock.shape[1]
    requiredNumPixels = totalNumPixels * triggerPercentage
    nonZeroPixels = cv2.countNonZero(grayBlock)

    if(nonZeroPixels >= requiredNumPixels):
        #print(nonZeroPixels)
        return nonZeroPixels

    return 0

def drawBlockRectengle(image, start_cordinates, rectengleHeight, rectengleWidth, color=RED):
    start_position = (start_cordinates[1] * rectengleHeight, start_cordinates[0] * rectengleWidth)
    end_position = (start_position[0] + rectengleHeight, start_position[1] + rectengleWidth)
    cv2.rectangle(image,start_position,end_position,color,2)
    return None

def drawCharacters(image, char, cordPos, rectengleHeight, rectengleWidth, color=WHITE):
    position = (cordPos[1] * rectengleHeight + 15, cordPos[0] * rectengleWidth + rectengleWidth)
    cv2.putText(image, char, position, cv2.FONT_HERSHEY_SIMPLEX, 4.5, color, 2)

def drawWinningLine(image, startPos, endPos, rectengleHeight, rectengleWidth):
    startPos = (startPos[1] * rectengleHeight + rectengleHeight//2, startPos[0] * rectengleWidth + rectengleWidth//2)
    endPos = (endPos[1] * rectengleHeight + rectengleHeight//2, endPos[0] * rectengleWidth + rectengleWidth//2)
    cv2.line(image, startPos, endPos, color=YELLOW, lineType=cv2.LINE_AA, thickness=2)

def mainLoop(camera):
    start_time = time.time()
    timer_active = False
    pressedBlockIndex = -1
    pressedBlockNonBlackPixes = 0
    game = TicTacToe()
    winner_pos = None
    isDraw = False

    while True:

        lower, upper = getTrackBarsValues()
        lower_bound = np.array(lower)
        upper_bound = np.array(upper)

        (_, image) = camera.read()
        image = cv2.flip(image, 1)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        skinImage = extractSkinFromImage(hsv, lower_bound, upper_bound)
        blocks = divideImageInBlocks(skinImage, gridRows, gridCols, True)

        # Checking if a hand is present in one of the blocks,
        # If yes, then start the timer for activation
        blockW = blocks[0].shape[0]
        blockH = blocks[0].shape[1]
        pressedBlock = False
        for i in range(len(blocks)):
            if game.board[i] is not None:
                matrixPos = (i // gridRows, i % gridRows)
                if winner_pos is not None and i in winner_pos:
                    drawCharacters(skinImage, game.getCharAtBoardPos(i), matrixPos, blockH, blockW, GREEN)
                else:
                    drawCharacters(skinImage, game.getCharAtBoardPos(i), matrixPos, blockH, blockW)

            numSkinPixels = isBlockPressed(blocks[i], 0.4)
            if numSkinPixels > 0:
                if i != pressedBlockIndex:
                    if numSkinPixels > pressedBlockNonBlackPixes:
                        start_time = time.time()
                        timer_active = True
                        pressedBlockIndex = i
                        pressedBlockNonBlackPixes = numSkinPixels

                pressedBlock = True

        if not pressedBlock:
            timer_active = False
            pressedBlockNonBlackPixes = 0
            pressedBlockIndex = -1
        elif pressedBlockIndex >= 0:
            matrixPos = (pressedBlockIndex // gridRows, pressedBlockIndex % gridRows)
            drawBlockRectengle(skinImage, matrixPos, blockH, blockW)


        if winner_pos is not None:
            matrixPosStart = (winner_pos[0] // gridRows, winner_pos[0] % gridRows)
            matrixPosEnd = (winner_pos[2] // gridRows, winner_pos[2] % gridRows)
            drawWinningLine(skinImage,matrixPosStart, matrixPosEnd,blockH,blockW)
            cv2.putText(skinImage, "Winner is " + game.getCharAtBoardPos(winner_pos[0]), (5,20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, MAGENTA, 2)
        elif isDraw:
            cv2.putText(skinImage, "DRAW / TIE", (5, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, MAGENTA, 2)

        cv2.imshow("Final Result", skinImage)
        #cv2.imshow("Block 1", blocks[0])

        if isDraw or winner_pos is not None:
            if hasTimerPassed(start_time, END_SCREEN_S):
                print("RESTART!!!!")
                game.newBoard()
                timer_active = False
                pressedBlockNonBlackPixes = 0
                pressedBlockIndex = -1
                isDraw = False
                winner_pos = None
        else:
            if timer_active and hasTimerPassed(start_time, TIMER_S):
                print(str(TIMER_S) + " Seconds have passed!")
                print("Block " + str(pressedBlockIndex) + " is pressed!")
                if game.makeMove(game.playersTurn, pressedBlockIndex):
                    game.printBoard()
                    winner_pos = game.checkWinner(game.playersTurn)
                    if winner_pos is not None:
                        print("Winner is " + game.getPlayerChar())
                    elif game.checkDraw():
                        isDraw = True
                        print("DRAW")

                    game.changePlayer()
                else:
                    print("INVALID MOVE")

                timer_active = False
                pressedBlockNonBlackPixes = 0
                pressedBlockIndex = -1

        if cv2.waitKey(1) != -1:
            break


if __name__ == "__main__":
    initTrackbars()
    camera = initCamera()

    mainLoop(camera)

    cv2.destroyAllWindows()
    camera.release()
