import argparse
import sys
from board import Board, DefaultBoard
from solver import Solver
from gui import GameGUI
from PyQt5.QtWidgets import QApplication
import os
from pathlib import Path
import PyQt5


os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.fspath(
    Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins"
)


def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Star Battle Game/Solver.")
    parser.add_argument("--board", type=str, default=None, 
                        help="File path of the board to load.")
    parser.add_argument("--board_img", type=str, default=None,
                        help="File path of the board image to load.")
    parser.add_argument("--autosolve", type=bool, default=False, 
                        help="If True, automatically runs the solver.")
    args = parser.parse_args()
    
    app = QApplication(sys.argv)

    # Initialize the game board
    board = Board()
    if args.board_img:
        try:
            board.load_from_image(args.board_img)
            print(f"Loaded board from {args.board_img}")
        except Exception as e:
            print(f"Error loading board: {e}")
            sys.exit(1)
    else:
        print("No board image provided. Starting with default board.")
        board = DefaultBoard()
    
    # Initialize the solver
    solver = Solver(board)

    # Set up the game GUI
    gui = GameGUI(board, solver)
    gui.autosolve = args.autosolve  # Enable autosolve if specified
    gui.run()  # Start the interactive game window

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
