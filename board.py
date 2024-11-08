'''
Class to manage Star-Battle board
'''
import cv2
import numpy as np

class Segment():
    """
    Segment class to track segments within the board
    """
    def __init__(self) -> None:
        self.squares = []
        self.subsegs = []

    def update(self):
        pass

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

        # Maintain a cout of stars in each row, col and segment
        self.row_stars = None
        self.col_stars = None
        self.seg_stars = None

        # Locations where star placement is not valid
        self.invalid = None

        # Win status
        self.win = False

    def update(self):
        """
        Function to update the board based on the board_state entries

        Mark invalid stars
        Record if board is a win
        """
        # Update the star count of each row, col and segment
        self.update_star_count()

        # Update the segments and sub-segs
        self.update_segments()

        # Update the invalid squares
        self.update_invalid()

        # Check if board state is winning
        self.update_win()
    
    def update_star_count(self):
        n = self.board_size

        self.row_stars = [0] * n
        self.col_stars = [0] * n
        self.seg_stars = [0] * n

        for r in range(n):
            for c in range(n):
                if self.board_state[r][c] == 1:
                    self.row_stars[r] += 1
                    self.col_stars[c] += 1
                    self.seg_stars[self.board_segments[r][c]] += 1


    def update_segments(self):
        # Update all segment objects based on board
        if not self.segments:
            # Make new segments
            self.segments = []
            for i in range(self.board_size):
                self.segments.append(Segment())
            
            # Update the map from location to
            for r in range(self.board_size):
                for c in range(self.board_size):
                    s = self.board_segments[r][c]
                    self.segments[s].squares.append((r,c))

            

    def update_invalid(self):
        n = self.board_size
        b = self.board_state

        # Check if any stars are invalid
        invalid = [[False] * n for _ in range(n)]

        # For all squares
        for r in range(n):
            for c in range(n):
                # Mark stars as invalid if 
                if b[r][c] != 1:
                    continue

                # An adjacent star is present
                for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    rr = r + dr
                    cc = c + dc
                    if (rr < 0) or (rr > n - 1) or (cc < 0) or (cc > n - 1):
                        continue
                    invalid[r][c] |= (b[rr][cc] == 1)
                
                invalid[r][c] |= (self.row_stars[r] > self.n_stars)
                invalid[r][c] |= (self.col_stars[c] > self.n_stars)
                invalid[r][c] |= (self.seg_stars[self.board_segments[r][c]] > self.n_stars)

        self.invalid = invalid

    def update_win(self):
        n = self.board_size
        b = self.board_state

        star_count = 0
        invalid_stars = False
        for r in range(n):
            for c in range(n):
                if b[r][c] == 1:
                    star_count += 1
                    invalid_stars |= self.invalid[r][c]

        self.win = (star_count == self.board_size * self.n_stars) and not invalid_stars
        self.invalid = self.invalid

    def load_from_image(self, img_path: str) -> None:
        """
        Load a board from an image

        Create a new board with an empty state
        Load in board segments from image using CV
        Load in any already-populated stars and X's (TODO)
        """


        # Image
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("Image could not be loaded from: {img_path}")

        # Greyscale
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold
        _, binary = cv2.threshold(img_grey, 128, 255, cv2.THRESH_BINARY_INV)

        # Erode thinner lines
        eroded = cv2.morphologyEx(binary, cv2.MORPH_ERODE, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=2)

        # Get outline
        contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        outline = img.copy()
        cv2.drawContours(outline, contours, -1, (0, 255, 0), 2)

        # Crop so only game board is considered
        x, y, w, h = cv2.boundingRect(contours[0])
        cropped = eroded[x:x+w, y:y+h]

        # Flood fill each segment
        flooded = np.zeros_like(cropped)
        mask = cv2.copyMakeBorder(cropped, 1, 1, 1, 1, cv2.BORDER_REPLICATE)


        # Determine board size TODO and number of stars
        n = 5
        s = 1

        # Create segemt and board map
        curr_seg = 1
        board_segments = [[0] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                x, y = int(c/n * w + w/(2*n)), int(r/n * h + h/(2*n))

                if flooded[y, x] == 0:
                    seed = (x, y)
                    _, flooded, mask, _ = cv2.floodFill(flooded, mask, seed, curr_seg)

                    curr_seg += 1

                board_segments[r][c] = flooded[y, x]

        # 0 index segments
        for r in range(n):
            for c in range(n):
                board_segments[r][c] -= 1

        # Update the read state of the board
        board_state = [[0] * n for _ in range(n)]

        self.n_stars = s
        self.board_size = n
        self.board_state = board_state
        self.board_segments = board_segments
        self.segments = []



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