import numpy as np
import matplotlib.pyplot as plt
import string

colours = ('Red', 'Blue', 'Yellow', 'Green')

pieces = ('Pawn', 'Knight', 'Bishop', 'Rook', 'Queen', 'King')

piece_val = {'Pawn': 1, 'Knight': 3, 'Bishop': 5, 'Rook': 5,
                'Queen': 9, 'King': 20}

#Creates class for chessboard
class Board:
    def __init__(self):
        self.pieces = {'Red': [], 'Blue': [], 'Yellow': [], 'Green': []}

    def display(self):
        for piece in self.pieces:
            print('test')

    #Resets chess board to initial setup
    def reset(self):
        self.pieces = {}        

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

corner = 3
nrows = 14
ncols = 14

image = np.zeros((nrows, ncols, 3))

for i in range(nrows):
    for j in range(ncols):
        if (i + j)%2 == 0: 
            image[i][j] = np.array([1, 1, 1])
        else:
            image[i][j] = np.array([0.5, 0.5, 0.5])
        if ((i < corner or i >= nrows - corner) and (j < corner or 
                j >= ncols - corner)):
            image[i][j] = np.array([0, 0, 0])

plt.figure(figsize = (5, 5))

piece = '\u265F'
row_labels = range(1, nrows + 1)
col_labels = list(string.ascii_uppercase[:ncols])
plt.xticks(range(ncols), col_labels)
plt.yticks(range(nrows), row_labels)

plt.imshow(image)
plt.text(5, 5, piece, color = 'red')
plt.show()
