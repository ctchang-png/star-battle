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
    """A widget representing a single square on the board."""
    
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.state = 0  # 0 = blank, 1 = star, 2 = X
        self.setFixedSize(50, 50)
        self.update_square()

    def update_square(self):
        """Updates the display based on the square's state."""
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        if self.state == 1:  # Draw a star
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
            painter.drawEllipse(10, 10, 30, 30)
        elif self.state == 2:  # Draw an X
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine))
            painter.drawLine(10, 10, 40, 40)
            painter.drawLine(10, 40, 40, 10)
        painter.end()

        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        """Handle left or right click events to toggle the square's state."""
        if event.button() == Qt.LeftButton:
            self.state = 1 if self.state != 1 else 0  # Toggle between 0 and 1
        elif event.button() == Qt.RightButton:
            self.state = 2 if self.state != 2 else 0  # Toggle between 0 and 2
        self.update_square()


class GameGUI(QMainWindow):
    """Main GUI for the Star Battle or Queens game."""

    def __init__(self, board: Board, solver: Solver):
        super().__init__()
        self.board = board
        self.solver = solver
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

        game_board_layout = self.createGameLayout()
        layout.addLayout(game_board_layout)

        solver_board_layout = self.createSolverLayout()
        layout.addLayout(solver_board_layout)




    def createGameLayout(self):
        """Sets up the game board section of the UI"""
        layout = QVBoxLayout()
        label = QLabel('Game')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        board_layout = QGridLayout()

        self.squares = []  # Keep track of square widgets

        # Create all board buttons
        for i in range(self.board.board_size):
            row = []
            for j in range(self.board.board_size):
                square = SquareWidget(i, j)
                board_layout.addWidget(square, i, j)
                row.append(square)
            self.squares.append(row)

        layout.addLayout(board_layout)
        # Create all segment outlines
        layout.addStretch(0)
        return layout


    def createSolverLayout(self):
        """Sets up the solver board section of the UI"""
        layout = QVBoxLayout()
        label = QLabel('Solver')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        board_layout = QGridLayout()
        # Create all board buttons
        for i in range(self.board.board_size):
            for j in range(self.board.board_size):
                square = SquareWidget(i, j)
                board_layout.addWidget(square, i, j)
        layout.addLayout(board_layout)
        layout.addStretch(0)
        return layout

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

