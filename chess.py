import numpy as np
import matplotlib.pyplot as plt

colours = ('Red', 'Blue', 'Yellow', 'Green')

pieces = ('Pawn', 'Knight', 'Bishop', 'Rook', 'Queen', 'King')

piece_val = {'Pawn': 1, 'Knight': 3, 'Bishop': 5, 'Rook': 5,
                'Queen': 9, 'King': 20}

#Creates class for chessboard
class Board:
    def __init__(self):
        self.pieces = {'Red': [], 'Blue': [], 'Yellow': [], 'Green': []}
    
    #Resets chess board to initial setup
    def reset(self):
        

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, rank, file_):
        self.name = name
        self.colour = colour
        self.value = piece_value
        self.rank = rank
        self.file_ = file_

    def position(self):
        return self.file_ + self.rank
