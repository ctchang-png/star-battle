'''
Star-Battle solver
'''
from board import Board, Segment
import copy
import numpy as np

class Solver():
    def __init__(self, board: Board) -> None:
        self.board = board

        # information codes:
        # - 0 Unknown
        # - 1 Star
        # - 2 X
        # - 3 star must be on square
        # - 4 x must be on square
        # - 5 1 star must be in segment
        self.information_grid = [[0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [0, 0, 0, 0, 0],
                                 [5, 4, 0, 5, 5],
                                 [5, 4, 0, 4, 5]]
        
    def update(self):
        """
        Update the solver based on the current board state
        """
        # Copy the board state
        self.information_grid = copy.deepcopy(self.board.board_state)

        # Update any missing Xs from star rules
        self.updateBlocked()

        # Update the segments where 1 star is required
        self.update1StarSegs()

        # Update the overlap from mandatory regions
        self.update1StarBlocked()

        # Mark location of deduced information
        # Mark 3 on all segments of size 1 that require 1 star
        # Mark 4 on all segments that require 1 star

    def updateBlocked(self):
        """
        Update all blocked locations from the current board
        """
        n = self.board.board_size
        b = self.board.board_state

        # For each square
        for r in range(n):
            for c in range(n):
                # Only mark open squares
                if b[r][c] != 0:
                    continue
                segment = self.board.board_segments[r][c]
                # Square is blocked if row, col, segment is full
                if self.board.row_stars[r] >= self.board.n_stars:
                    self.information_grid[r][c] = 4
                if self.board.col_stars[c] >= self.board.n_stars:
                    self.information_grid[r][c] = 4
                if self.board.seg_stars[segment] >= self.board.n_stars:
                    self.information_grid[r][c] = 4
                # Square is blocked if an adjacent star exists
                for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    rr, cc = r + dr, c + dc
                    if (rr < 0) or (cc < 0) or (rr >= n) or (cc >= n):
                        continue
                    if b[rr][cc] == 1:
                        self.information_grid[r][c] = 4

    def update1StarSegs(self):
        """
        Scan the board and build all segments that require 1 star

        TODO: Need to scan for stars present to determine if there is or is not a 1 star seg of this type. Consider tracking stars for each row, col, segment to board to easily access this
        """
        n = self.board.board_size
        b = self.board.board_state

        # Horizontal slices
        horizontal_segs = []
        for r in range(n):
            if self.board.row_stars[r] >= self.board.n_stars:
                continue
            h_seg = Segment()
            for c in range(n):
                if b[r][c] == 0:
                    h_seg.squares.append((r, c))
            horizontal_segs.append(h_seg)

        # Vertical slices
        vertical_segs = []
        for c in range(n):
            if self.board.col_stars[c] >= self.board.n_stars:
                continue
            v_seg = Segment()
            for r in range(n):
                if b[r][c] == 0:
                    v_seg.squares.append((r, c))
            vertical_segs.append(v_seg)

        # Sub segs:
        sub_segs = []
        for i, s in enumerate(self.board.segments):
            if self.board.seg_stars[i] >= self.board.n_stars:
                continue
            s_seg = Segment()
            for r, c in s.squares:
                if b[r][c] == 0:
                    s_seg.squares.append((r, c))
            sub_segs.append(s_seg)

        all_segs = horizontal_segs + vertical_segs + sub_segs
        self.one_star_segs = all_segs
            
    def update1StarBlocked(self):
        n = self.board.board_size

        blocking = [[False] * n for _ in range(n)]

        # Row constraints

        # Col constraints

        # Seg constraints


        # Adjacency constraints
        # No star may block a region that must contain a star
        for segment in self.one_star_segs:
            if not segment.squares:
                continue
            # Map of items blocking this segment
            seg_blocking = None
            for r, c in segment.squares:
                mask = [[False] * n for _ in range(n)]
                for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
                    rr, cc = r + dr, c + dc
                    if (rr < 0) or (cc < 0) or (rr >= n) or (cc >= n):
                        continue
                    mask[rr][cc] = True

                if seg_blocking is None:
                    seg_blocking = mask
                seg_blocking = np.bitwise_and(seg_blocking, mask)
            blocking = np.bitwise_or(seg_blocking, blocking)

        # Set info array from blocking
        for r in range(n):
            for c in range(n):
                if not blocking[r][c]:
                    continue
                if self.information_grid[r][c] == 0:
                    self.information_grid[r][c] = 4