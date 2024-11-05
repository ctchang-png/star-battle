'''
Star-Battle solver
'''
from board import Board

class Solver():
    def __init__(self, board: Board) -> None:
        self.board = board

        self.information_grid = [[0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [1, 2, 0, 1, 1],
                                 [1, 2, 0, 2, 1]]