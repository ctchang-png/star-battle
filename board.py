'''
Class to manage Star-Battle board
'''

class Board():
    def __init__(self) -> None:
        # Stars per row, col, segment
        self.n_stars = 0
        # Board size (n rows, n cols, n segs)
        self.board_size = 0

        # 2D array of board state (0 for empty, 1 for star, 2 for X)
        self.board = None
        # List of segments in the board
        self.segs = None


class DefaultBoard(Board):

    def __init__(self) -> None:
        super().__init__()
        self.n_stars = 1
        self.board_size = 5
        self.board = [[0] * 5 for _ in range(5)]

        self.segs = [[0, 0, 0, 0, 0],
                     [0, 1, 1, 1, 1],
                     [0, 1, 3, 4, 2],
                     [3, 3, 3, 4, 2],
                     [3, 3, 2, 2, 2]]