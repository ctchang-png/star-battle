'''
GUI to run the star-battle game
'''
from board import Board
from solver import Solver

# gui.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPixmap

class SquareWidget(QLabel):
    """
    A widget representing a single square on the board.
    
    A square is initialized with:
    - board: the board object to read the value from
    - r: the row in the board
    - c: the col in the board
    - interactive: True if this is a square the user can interact with (click to toggle)
    """
    
    def __init__(self, board, r, c, interactive=False):
        super().__init__()
        # Game board object
        self.board = board
        # Row/Col coordinates on board
        self.r = r
        self.c = c
        self.interactive = interactive
        self.setFixedSize(50, 50)
        self.update_square()

    def update_square(self, color=QColor('Black'), background=QColor('White')):
        """Updates the display based on the square's state."""
        pixmap = QPixmap(self.size())
        pixmap.fill(background)

        painter = QPainter(pixmap)
        b = self.board.board_state
        square_state = b[self.r][self.c]

        if square_state == 1:  # Draw a star
            painter.setPen(QPen(color, 4, Qt.SolidLine))
            painter.setBrush(QBrush(color, Qt.SolidPattern))
            painter.drawEllipse(10, 10, 30, 30)
        elif square_state == 2:  # Draw an X
            painter.setPen(QPen(color, 4, Qt.SolidLine))
            painter.drawLine(10, 10, 40, 40)
            painter.drawLine(10, 40, 40, 10)
        painter.end()

        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        """Handle left or right click events to toggle the square's state."""
        if not self.interactive:
            return
        b = self.board.board_state
        if event.button() == Qt.LeftButton:
            curr_state = b[self.r][self.c]
            new_state = 1 if curr_state != 1 else 0  # Toggle between 0 and 1
        elif event.button() == Qt.RightButton:
            curr_state = b[self.r][self.c]
            new_state = 2 if curr_state != 2 else 0  # Toggle between 0 and 1
        b[self.r][self.c] = new_state
        
        # GameGUI->CentralWidget->SquareWidget
        gameGui = self.parent().parent()
        gameGui.updateBoard()

class OutlineWidget(QLabel):
    """A widget representing an outline rectangle on the board."""

    def __init__(self, i, j, thick):
        super().__init__()

        #   01234
        # 0 @@@@@
        # 1 @1@2@
        # 2 @a@a@
        # 3 @1@2@
        # 4 @@@@@
        small = 6
        large = 50
        
        thin = 1
        center = small // 2


        lines = []
        if (i % 2) and (j % 2):
            # Both odd, do not draw
            return
        elif (i % 2) and not (j % 2):
            # odd row even col, vertical line
            self.setFixedSize(small, large)
            x = 0 if thick else center - (thin // 2)
            y = 0
            w = small if thick else thin
            h = large
            lines.append((x, y, w, h))
        
        elif not (i % 2) and (j % 2):
            # even row, odd col, horizontal line
            self.setFixedSize(large, small)
            x = 0
            y = 0 if thick else center - (thin // 2)
            w = large
            h = small if thick else thin
            lines.append((x, y, w, h))
        else:
            # Both even, is a corner
            self.setFixedSize(small, small)

            if thick:
                lines.append((0, 0, small, small))
            else:
                lines.append((center - thin//2, 0, thin, small))
                lines.append((0, center - thin//2, small, thin))

        pixmap = QPixmap(self.size())
        pixmap.fill(QColor('White'))
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor('Black')))
        for line in lines:
            painter.drawRect(*line)
        painter.end()
        self.setPixmap(pixmap)


class GameGUI(QMainWindow):
    """Main GUI for the Star Battle or Queens game."""

    def __init__(self, board: Board, solver: Solver):
        super().__init__()
        self.board = board
        self.solver = solver

        # Array of outline widgets to render
        self.gameOutlines = None
        self.solverOutlines = None
        # Array of game square widgets to render
        self.gameSquares = None
        # Array of solver square widgets to render (non-interactive game square)
        self.solverSquares = None
        self.initUI()

    def initUI(self):
        """Sets up the main window and grid layout."""
        self.setWindowTitle(f"Star Battle: {self.board.board_size}x{self.board.board_size} {self.board.n_stars}\u2605")
        self.setGeometry(100, 100, 600, 600)

        # Create a central widget with a grid layout for the board
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        self.makeOutlineArray()

        game_board_layout = self.createGameLayout()
        layout.addLayout(game_board_layout)

        solver_board_layout = self.createSolverLayout()
        layout.addLayout(solver_board_layout)

    def makeOutlineArray(self):
        n = self.board.board_size * 2 + 1

        self.gameOutlines = [[0] * n for _ in range(n)]
        self.solverOutlines = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if (i == 0) or (j == 0) or (i >= n - 1) or (j >= n - 1):
                   # Outline is necessarily thick
                   self.gameOutlines[i][j] = OutlineWidget(i, j, True)
                   self.solverOutlines[i][j] = OutlineWidget(i, j, True)
                   continue
                if i%2 and j%2:
                    # This square has no outline (is a square or star or empty)
                    continue
                elif i%2 and not j%2:
                    # Vertical line
                    c1, c2 = j//2 - 1, j//2
                    r = (i - 1) // 2
                    s1 = self.board.board_segments[r][c1]
                    s2 = self.board.board_segments[r][c2]
                    thick = (s1 != s2)
                elif not i%2 and j%2:
                    # Horizontal line
                    r1, r2 = i//2 - 1, i//2
                    c = (j - 1) // 2
                    s1 = self.board.board_segments[r1][c]
                    s2 = self.board.board_segments[r2][c]
                    thick = (s1 != s2)
                else:
                    r1, r2 = i//2 - 1, i//2
                    c1, c2 = j//2 - 1, j//2

                    s1 = self.board.board_segments[r1][c1]
                    s2 = self.board.board_segments[r1][c2]
                    s3 = self.board.board_segments[r2][c1]
                    s4 = self.board.board_segments[r2][c2]
                    thick = (s1 != s2 or s1 != s3 or s1 != s4)

                self.gameOutlines[i][j] = OutlineWidget(i, j, thick)
                self.solverOutlines[i][j] = OutlineWidget(i, j, thick)

    def createGameLayout(self):
        """Sets up the game board section of the UI"""
        layout = QVBoxLayout()
        label = QLabel('Game')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        board_layout = QGridLayout()

        self.gameSquares = []  # Keep track of square widgets

        # Create all board buttons
        n = self.board.board_size
        for r in range(n):
            row = []
            for c in range(n):
                square = SquareWidget(self.board, r, c, interactive=True)
                row.append(square)
            self.gameSquares.append(row)

        # Add outline and board square widgets to the UI
        n_widgets = 2 * self.board.board_size + 1
        for i in range(n_widgets):
            for j in range(n_widgets):
                if i%2 and j%2:
                    # Both indeces are odd: this is a square cell
                    r = (i - 1) // 2
                    c = (j - 1) // 2
                    board_layout.addWidget(self.gameSquares[r][c], i, j)
                else:
                    board_layout.addWidget(self.gameOutlines[i][j], i, j)
        board_layout.setSpacing(0)
        layout.addLayout(board_layout)

        layout.addStretch(0)
        return layout

    def createSolverLayout(self):
        """Sets up the solver board section of the UI"""
        layout = QVBoxLayout()
        label = QLabel('Solver')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.solverSquares = []

        board_layout = QGridLayout()
        # Create all board buttons
        n = self.board.board_size
        for r in range(n):
            row = []
            for c in range(n):
                square = SquareWidget(self.board, r, c, interactive=False)
                row.append(square)
            self.solverSquares.append(row)

        # Add outline and board square widgets to the UI
        n_widgets = 2 * self.board.board_size + 1
        for i in range(n_widgets):
            for j in range(n_widgets):
                if i%2 and j%2:
                    # Both indeces are odd: this is a square cell
                    r = (i - 1) // 2
                    c = (j - 1) // 2
                    board_layout.addWidget(self.solverSquares[r][c], i, j)
                else:
                    board_layout.addWidget(self.solverOutlines[i][j], i, j)
        board_layout.setSpacing(0)
        layout.addLayout(board_layout)

        layout.addStretch(0)
        return layout

    def updateBoard(self):
        """
        Update the board squares to match the board

        Also scan for invalid stars
        Also scan for wins
        """
        n = self.board.board_size
        b = self.board.board_state

        # Check if any stars are invalid
        invalid = [[False] * n for _ in range(n)]

        # Check Adjacency
        for r in range(n):
            for c in range(n):
                for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    rr = r + dr
                    cc = c + dc
                    if (rr < 0) or (rr > n - 1) or (cc < 0) or (cc > n - 1):
                        continue
                    if b[r][c] == 1 and b[rr][cc] == 1:
                        invalid[r][c] = True

        # Check rows
        for r in range(n):
            row_count = 0
            for c in range(n):
                if b[r][c] == 1:
                    row_count += 1
            if row_count > 2:
                for c in range(n):
                    if b[r][c] == 1:
                        invalid[r][c] = True

        # Check cols
        for c in range(n):
            col_count = 0
            for r in range(n):
                if b[r][c] == 1:
                    col_count += 1
            if col_count > 2:
                for r in range(n):
                    if b[r][c] == 1:
                        invalid[r][c] = True

        # Check segments

        # Check if board state is winning
        # Update any invalid squares
        star_count = 0
        any_invalid = False
        for r in range(n):
            for c in range(n):
                if b[r][c] == 1:
                    star_count += 1
                any_invalid |= invalid[r][c]

                color = QColor('Red') if invalid[r][c] else QColor('Black')
                self.gameSquares[r][c].update_square(color=color)
                self.solverSquares[r][c].update_square(color=color)

        # If board is winning, call the win method
        if star_count == (self.board.n_stars * self.board.board_size) and not any_invalid:
            # Win!
            self.win()

    def win(self):
        """
        Function to handle winning the game
        """
        # Update the label to say: "Game: You Win!"

        # Update the stars on the board
        n = self.board.board_size
        for r in range(n):
            for c in range(n):
                # Make stars blue
                if self.board.board_state[r][c] == 1:
                    color = QColor('Blue')
                    self.gameSquares[r][c].update_square(color=color)
                    self.solverSquares[r][c].update_square(color=color)

    def run(self):
        """Runs the GUI application."""
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mock board and solver, replace with actual instances
    board = None
    solver = None

    game_gui = GameGUI(board, solver)
    game_gui.run()
    sys.exit(app.exec_())

