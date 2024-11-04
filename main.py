import argparse
import sys
from board import Board, DefaultBoard
from solver import Solver
from gui import GameGUI
from PyQt5.QtWidgets import QApplication

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Play Star Battle or Queens.")
    parser.add_argument("--board", type=str, default=None, 
                        help="File path of the board image to load.")
    parser.add_argument("--autosolve", type=bool, default=False, 
                        help="If True, automatically runs the solver.")
    args = parser.parse_args()
    
    app = QApplication(sys.argv)

    # Initialize the game board
    board = Board()
    if args.board:
        try:
            board.load_from_image(args.board)
            print(f"Loaded board from {args.board}")
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
