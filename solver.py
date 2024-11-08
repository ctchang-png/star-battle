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

        # Update regions that block 1 star regions completely
        self.update1StarBlocked()

        # Update the locations where stars must be (1 star regions of size 1)
        self.update1StarMandatory()

        # Information grid:
        # 0 for empty or no info
        # 1 for star placed on board
        # 2 for x placed on board
        # 3 for star must be placed here
        # 4 for x must be placed here

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

        """
        n = self.board.board_size
        b = self.board.board_state

        # Horizontal slices
        horizontal_segs = []
        for r in range(n):
            if (self.board.n_stars - self.board.row_stars[r]) != 1:
                continue
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
            if (self.board.n_stars - self.board.col_stars[c]) != 1:
                continue
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
            if (self.board.n_stars - self.board.seg_stars[i]) != 1:
                continue
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
        """
        Update all board locations with (X required) that block a 1 star seg
        """
        n = self.board.board_size

        blocking = [[False] * n for _ in range(n)]

        # Segment constraints
        # If segment s2 is a sub-seg of segment s1, block all squares in s1 that are not in s2
        for s1 in self.one_star_segs:
            s1_set = set(s1.squares)
            for s2 in self.one_star_segs:
                if len(s2.squares) >= len(s1.squares):
                    continue
                s2_set = set(s2.squares)
                if not s2_set.issubset(s1_set):
                    continue

                # X all non-overlapping locations
                for r, c in (s1_set - s2_set):
                    blocking[r][c] = True
                

        # Adjacency constraints
        # If placing a star at a square would X a 1 star seg, block this square
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

    def update1StarMandatory(self):
        """
        Update all squares where 1 star is necessarily located
        """

        for s in self.one_star_segs:
            if len(s.squares) == 1:
                r, c = s.squares[0]
                self.information_grid[r][c] = 3