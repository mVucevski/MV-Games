O = -1
X = 1


class TicTacToe:
    def __init__(self):
        self.board = [None] * 9
        self.playersTurn = X

    def printBoard(self):
        print(self.board)

    def changePlayer(self):
        self.playersTurn *= -1

    def isValidMove(self, move):
        if self.board[move] is None:
            return True
        return False

    def getPlayerChar(self):
        if self.playersTurn == X:
            return 'X'
        return 'O'

    def getCharAtBoardPos(self, i):
        if self.board[i] == X:
            return 'X'
        elif self.board[i] == O:
            return 'O'
        return None

    def makeMove(self, player, move):
        if self.isValidMove(move):
            self.board[move] = player
            return True
        return False

    def checkWinner(self, player):
        if self.board.count(player) >= 3:
            if self.board[0] == player and self.board[1] == player and self.board[2] == player:
                return 0, 1, 2
            elif self.board[3] == player and self.board[4] == player and self.board[5] == player:
                return 3, 4, 5
            elif self.board[6] == player and self.board[7] == player and self.board[8] == player:
                return 6, 7, 8
            elif self.board[0] == player and self.board[3] == player and self.board[6] == player:
                return 0, 3, 6
            elif self.board[1] == player and self.board[4] == player and self.board[7] == player:
                return 1, 4, 7
            elif self.board[2] == player and self.board[5] == player and self.board[8] == player:
                return 2, 5, 8
            elif self.board[2] == player and self.board[4] == player and self.board[6] == player:
                return 2, 4, 6
            elif self.board[0] == player and self.board[4] == player and self.board[8] == player:
                return 0, 4, 8

        return None

    def newBoard(self):
        self.board = [None] * 9
        self.playersTurn = X

    def checkDraw(self):
        if self.board.count(None) == 0:
            return True
        return False

# def test(tictactoe):
#
#     tictactoe.board[0] = X
#     tictactoe.board[1] = X
#     tictactoe.board[2] = X
#     tictactoe.board[3] = O
#
#     tmp_move = 8
#     if tictactoe.isValidMove(tmp_move):
#         tictactoe.makeMove(O, tmp_move)
#     else:
#         print("Invalid move")
#
#     tictactoe.printBoard()
#     print(tictactoe.checkWinner(X))
#     print(tictactoe.board.count(1))
#     print(tictactoe.board.count(None))

# test(TicTacToe())
