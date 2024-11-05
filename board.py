'''
Class to manage Star-Battle board
'''

class Segment():
    def __init__(self) -> None:
        self.squares = []

class Board():
    def __init__(self) -> None:
        # Stars per row, col, segment
        self.n_stars = 0
        # Board size (n rows, n cols, n segs)
        self.board_size = 0

        # 2D array of board state (0 for empty, 1 for star, 2 for X)
        self.board_state = None
        # 2D array of board segments
        self.board_segments = None
        # List of segment objects in board
        self.segments = []

    def update(self):
        """
        Function to update the board based on the board_state entries

        Mark invalid stars
        Record if board is a win
        """
        pass

class DefaultBoard(Board):

    def __init__(self) -> None:
        super().__init__()
        self.n_stars = 1
        self.board_size = 5
        self.board_state = [[0] * 5 for _ in range(5)]

        self.board_segments = [[0, 0, 0, 0, 0],
                               [0, 1, 1, 1, 1],
                               [0, 1, 3, 4, 2],
                               [3, 3, 3, 4, 2],
                               [3, 3, 2, 2, 2]]