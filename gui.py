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
        """
        Updates the display based on the square's state.
        
        board.board_state[r][c] denotes symbol: 0 empty, 1 star, 2 X
        board.invalid[r][c] denotes if (r,c) is an invalid star location
        board.winning denotes if board is a win

        symbol color is black by default, red for invalid stars, blue for winning stars
        background color is white by default, can be colored by segment
        """
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
        """
        Handle left or right click events to toggle the square's state.
        
        If this is an interactive SquareWidget:
        - Modify the board state at this square
        - Update the board object to calculate invalid or wins
        - Redraw the board widgets
        """
        if not self.interactive:
            return
        
        # Set the board_state in the board object
        b = self.board.board_state
        if event.button() == Qt.LeftButton:
            curr_state = b[self.r][self.c]
            new_state = 1 if curr_state != 1 else 0  # Toggle between 0 and 1
        elif event.button() == Qt.RightButton:
            curr_state = b[self.r][self.c]
            new_state = 2 if curr_state != 2 else 0  # Toggle between 0 and 1
        b[self.r][self.c] = new_state
        
        # Update the board and calculate any checks
        self.board.update()

        # GameGUI->CentralWidget->BoardWidget->SquareWidget
        boardWidget = self.parent()
        centralWidget = boardWidget.parent()
        game_gui = centralWidget.parent()

        game_gui.updateBoards()

class OutlineWidget(QLabel):
    """A widget representing an outline rectangle on the board."""

    def __init__(self, i, j, thick):
        super().__init__()

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

class GameBoardWidget(QWidget):
    """
    Widget to capture the interactive game board
    """
    def __init__(self, board: Board):
        super().__init__()
        self.board = board

        layout = QGridLayout()

        # Add outlines and board squares in a grid
        n_squares = self.board.board_size
        n_grids = 2 * n_squares + 1

        self.board_squares = [[None] * n_squares for _ in range(n_squares)]
        self.board_edges = [[None] * n_grids for _ in range(n_grids)]

        # Read through the board and add all outline and square elements to the layout
        for i in range(n_grids):
            for j in range(n_grids):

                if (i == 0) or (j == 0) or (i == n_grids - 1) or (j == n_grids - 1):
                    widget = OutlineWidget(i, j, thick=True)
                    self.board_edges[i][j] = widget
                elif (i%2) and (j%2):
                    # Is a square
                    r = (i - 1) // 2
                    c = (j - 1) // 2
                    widget = SquareWidget(board, r, c, interactive=True)
                    self.board_squares[r][c] = widget

                elif (i%2) and not (j%2):
                    # vertical line
                    c1, c2 = j//2 - 1, j//2
                    r = (i - 1) // 2
                    s1 = self.board.board_segments[r][c1]
                    s2 = self.board.board_segments[r][c2]
                    thick = (s1 != s2)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j] = widget
                elif not (i%2) and (j%2):
                    # horizontal line
                    r1, r2 = i//2 - 1, i//2
                    c = (j - 1) // 2
                    s1 = self.board.board_segments[r1][c]
                    s2 = self.board.board_segments[r2][c]
                    thick = (s1 != s2)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j] = widget
                else:
                    # corner
                    r1, r2 = i//2 - 1, i//2
                    c1, c2 = j//2 - 1, j//2
                    s1 = self.board.board_segments[r1][c1]
                    s2 = self.board.board_segments[r1][c2]
                    s3 = self.board.board_segments[r2][c1]
                    s4 = self.board.board_segments[r2][c2]
                    thick = (s1 != s2 or s1 != s3 or s1 != s4)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j]
                layout.addWidget(widget, i, j)
        layout.setSpacing(0)
        self.setLayout(layout)

    def update(self):
        """
        Update all squares to match the board state

        0: empty, 1: star, 2: x
        Mark invalid stars as red
        Mark solved board as all blue
        """
        n = self.board.board_size

        for r in range(n):
            for c in range(n):
                if self.board.win:
                    color = QColor('Blue')
                else:
                    if self.board.board_state[r][c] == 1 and self.board.invalid[r][c]:
                        color = QColor('Red')
                    else:
                        color = QColor('Black')
                self.board_squares[r][c].update_square(color=color)

class SolverBoardWidget(QWidget):
    """
    Widget to capture the solver board
    """
    def __init__(self, board: Board, solver: Solver):
        super().__init__()
        self.board = board
        self.solver = solver

        layout = QGridLayout()

        # Add outlines and board squares in a grid
        n_squares = self.board.board_size
        n_grids = 2 * n_squares + 1

        self.board_squares = [[None] * n_squares for _ in range(n_squares)]
        self.board_edges = [[None] * n_grids for _ in range(n_grids)]

        # Read through the board and add all outline and square elements to the layout
        for i in range(n_grids):
            for j in range(n_grids):

                if (i == 0) or (j == 0) or (i == n_grids - 1) or (j == n_grids - 1):
                    widget = OutlineWidget(i, j, thick=True)
                    self.board_edges[i][j] = widget
                elif (i%2) and (j%2):
                    # Is a square
                    r = (i - 1) // 2
                    c = (j - 1) // 2
                    widget = SquareWidget(board, r, c, interactive=False)
                    self.board_squares[r][c] = widget

                elif (i%2) and not (j%2):
                    # vertical line
                    c1, c2 = j//2 - 1, j//2
                    r = (i - 1) // 2
                    s1 = self.board.board_segments[r][c1]
                    s2 = self.board.board_segments[r][c2]
                    thick = (s1 != s2)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j] = widget
                elif not (i%2) and (j%2):
                    # horizontal line
                    r1, r2 = i//2 - 1, i//2
                    c = (j - 1) // 2
                    s1 = self.board.board_segments[r1][c]
                    s2 = self.board.board_segments[r2][c]
                    thick = (s1 != s2)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j] = widget
                else:
                    # corner
                    r1, r2 = i//2 - 1, i//2
                    c1, c2 = j//2 - 1, j//2
                    s1 = self.board.board_segments[r1][c1]
                    s2 = self.board.board_segments[r1][c2]
                    s3 = self.board.board_segments[r2][c1]
                    s4 = self.board.board_segments[r2][c2]
                    thick = (s1 != s2 or s1 != s3 or s1 != s4)
                    widget = OutlineWidget(i, j, thick=thick)
                    self.board_edges[i][j]
                layout.addWidget(widget, i, j)
        layout.setSpacing(0)
        self.setLayout(layout)

    def update(self):
        """
        Update all squares to match the board state

        0: empty, 1: star, 2: x
        Mark invalid stars as red
        Mark solved board as all blue
        """
        n = self.board.board_size

        for r in range(n):
            for c in range(n):
                if self.board.win:
                    color = QColor('Blue')
                else:
                    if self.board.board_state[r][c] == 1 and self.board.invalid[r][c]:
                        color = QColor('Red')
                    else:
                        color = QColor('Black')

                background = QColor('White')
                if self.solver.information_grid[r][c] == 1:
                    background = QColor(0, 100, 0, 128)
                elif self.solver.information_grid[r][c] == 2:
                    background = QColor(100, 0, 0, 128)
                self.board_squares[r][c].update_square(color=color, background=background)

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


        self.game_widget = GameBoardWidget(board)
        self.solver_widget = SolverBoardWidget(board, solver)


        self.initUI()
        self.updateBoards()

    def initUI(self):
        """Sets up the main window and grid layout."""
        self.setWindowTitle(f"Star Battle: {self.board.board_size}x{self.board.board_size} {self.board.n_stars}\u2605")
        self.setGeometry(100, 100, 600, 600)

        # Create a central widget with a grid layout for the board
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        central_widget.setLayout(layout)

        # Create the game widget
        game_layout = QVBoxLayout()
        game_label = QLabel('Game')
        game_label.setAlignment(Qt.AlignCenter)
        game_layout.addWidget(game_label)
        game_layout.addWidget(self.game_widget)
        game_layout.addStretch(0)

        # Create the solver widget
        solver_layout = QVBoxLayout()
        solver_label = QLabel('Solver')
        solver_label.setAlignment(Qt.AlignCenter)
        solver_layout.addWidget(solver_label)
        solver_layout.addWidget(self.solver_widget)
        solver_layout.addStretch(0)

        layout.addLayout(game_layout)
        layout.addLayout(solver_layout)

    def updateBoards(self):
        """
        Update the board squares to match the board

        Also scan for invalid stars
        Also scan for wins
        """
        self.game_widget.update()
        self.solver_widget.update()
        # If board is winning, call the win method
        if self.board.win:
            # Win!
            self.win()

    def win(self):
        """
        Function to handle winning the game
        """
        # Update the label to say: "Game: You Win!"
        print(f"Game won!")

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

