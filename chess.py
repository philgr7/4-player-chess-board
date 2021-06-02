import numpy as np
import matplotlib.pyplot as plt
import string

colours = ('Red', 'Blue', 'Yellow', 'Green')

piece_list = {
        'Pawn': {
            'value': 1,
            'unicode': '\u265F'
            },
        'Knight': {
            'value': 3,
            'unicode': '\u265E'
            },
        'Bishop': {
            'value': 5,
            'unicode': '\u265D'
            },
        'Rook': {
            'value': 5,
            'unicode': '\u265C'
            },
        'Queen': {
            'value': 9,
            'unicode': '\u265B'
            },
        'King': {
            'value': 20,
            'unicode': '\u265A'
            }
        }
            
#Creates class for chessboard
class Board:
    def __init__(self, nrows = 14, ncols = 14, corner = 3, colours = 
                ['red', 'blue', 'yellow', 'green']):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.colours = colours

    #Creates board without pieces based on initialisation (assumed default)
    def base_board(self):
        #Initialise matrix of grid to be encoded with rgb colour code
        image = np.zeros((self.nrows, self.ncols, 3))

        #White squares are white, black squares are grey and corner 
        #squares that are not part of the board are black
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i + j)%2 == 0: 
                    image[i][j] = np.array([1, 1, 1])
                else:
                    image[i][j] = np.array([0.5, 0.5, 0.5])
                if ((i < self.corner or i >= self.nrows - self.corner) 
                    and (j < self.corner or j >= self.ncols - self.corner)):
                    image[i][j] = np.array([0, 0, 0])
        self.image = image

        #Initialise data for all pieces on board
    def piece_init(self):
        pieces = []
        for i in range(8):
            pieces.append(Piece('Pawn', 'Red', 2, 4+i))
        pieces.append(Piece('Knight', 'Red', 1, 5))
        pieces.append(Piece('Knight', 'Red', 1, 10))
        pieces.append(Piece('Bishop', 'Red', 1, 6))
        pieces.append(Piece('Bishop', 'Red', 1, 9))
        pieces.append(Piece('Rook', 'Red', 1, 4))
        pieces.append(Piece('Rook', 'Red', 1, 11))
        pieces.append(Piece('Queen', 'Red', 1, 7))
        pieces.append(Piece('King', 'Red', 1, 8))
        self.pieces = pieces

    #creates display of the current position of the board, including pieces
    def display(self):
        fig, ax = plt.subplots(figsize=(cm_to_inch(self.nrows,self.ncols)))

        ax.imshow(self.image)

        for piece in self.pieces:
            plt.text((0.2+2*(piece.file_- 1)) / (2*self.nrows), 
                    (0.2+2*(piece.rank - 1)) / (2*self.ncols), 
                    piece_list[piece.name]['unicode'], 
                    fontsize = '20', color = piece.colour, 
                    transform = ax.transAxes)
    
        row_labels = range(self.nrows, 0, -1)
        col_labels = list(string.ascii_uppercase[:self.ncols])
        plt.xticks(range(self.ncols), col_labels)
        plt.yticks(range(self.nrows), row_labels)

        plt.show()

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, rank, file_):
        self.name = name
        self.colour = colour
        self.value = piece_list[name]['value']
        self.rank = rank
        self.file_ = file_

    def coord_to_position(self):
        y = 2*(self.file_-1)
        return

    def position(self):
        return self.file_ + self.rank

def cm_to_inch(*args):
    inch = 2.54
    return tuple(i/inch for i in args)
'''
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

fig, ax = plt.subplots(figsize=(cm_to_inch(nrows,ncols)))

ax.imshow(image)

piece = '\u265F'
piece_2 = '\u2659'
row_labels = range(nrows, 0, -1)
col_labels = list(string.ascii_uppercase[:ncols])
plt.xticks(range(ncols), col_labels)
plt.yticks(range(nrows), row_labels)

plt.text(8.2/(2*nrows), 0.2/(2*ncols), piece, fontsize = '20', color = 'white', 
        transform = ax.transAxes)
plt.text(6.2/(2*nrows), 0.2/(2*ncols), piece_2, fontsize = '20', color = 'black', 
        transform = ax.transAxes)
plt.show()

'''

test = Board()
test.base_board()
test.piece_init()
test.display()
