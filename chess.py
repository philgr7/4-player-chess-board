import numpy as np
import matplotlib.pyplot as plt
import string

#Colours available in four player chess
colour_list = ('Red', 'Blue', 'Yellow', 'Green')

#List of available pieces with point value and corresponding unicode 
piece_list = {
            'Pawn': {'value': 1, 'unicode': '\u265F'},
            'Knight': {'value': 3, 'unicode': '\u265E'},
            'Bishop': {'value': 5, 'unicode': '\u265D'},
            'Rook': {'value': 5, 'unicode': '\u265C'},
            'Queen': {'value': 9, 'unicode': '\u265B'},
            'King': {'value': 20, 'unicode': '\u265A'}
        }

#Creates class for chessboard
class Board:
    #Default board is set as 14 rows/columns and with RBYG colours
    def __init__(self, nrows = 14, ncols = 14, corner = 3, colours = 
                colour_list):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.colours = colours

    #Creates empty board
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

        #Initialise data for all pieces on board - assumed default piece
        #config if not stated otherwise
    def piece_init(self, piece_order = ['Rook', 'Knight', 'Bishop',
        'King', 'Queen', 'Bishop', 'Knight', 'Rook']):
        pieces = []
        for i in range(8):
            pieces.append(Piece('Pawn', 'Red', 2, 11-i))
            pieces.append(Piece('Pawn', 'Blue', 11-i, 2))
            pieces.append(Piece('Pawn', 'Yellow', 13, 4+i))
            pieces.append(Piece('Pawn', 'Green', 4+i, 13))
            pieces.append(Piece(piece_order[i], 'Red', 1, 11-i))
            pieces.append(Piece(piece_order[i], 'Blue', 11-i, 1))
            pieces.append(Piece(piece_order[i], 'Yellow', 14, 4+i))
            pieces.append(Piece(piece_order[i], 'Green', 4+i, 14))
        
        self.pieces = pieces

    #Outputs image of the current board position including pieces
    def display(self):
        fig, ax = plt.subplots(figsize=(cm_to_inch(self.nrows,self.ncols)))

        ax.imshow(self.image)

        for piece in self.pieces:
                plt.text(piece.coord_to_position('file', self.nrows),
                        piece.coord_to_position('rank', self.ncols),
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

    #converts rank/file variables into corresponding required position on
    #board. 0.2 is arbitary value found through testing and should center
    #the piece in its respective square
    def coord_to_position(self, type_, n_extent):
        if type_ == 'file':
            return (0.2+2*(self.file_-1)) / (2*n_extent)
        if type_ == 'rank':
            return (0.2+2*(self.rank-1)) / (2*n_extent)

    #Returns string of position of piece
    def position(self):
        return self.file_ + self.rank

#Creates class for a chess move
class Move:

    def __init__(self, number, colour):
        self.number = number
        self.colour = colour
#Converts cm to inches for figure size
def cm_to_inch(*args):
    inch = 2.54
    return tuple(i/inch for i in args)

test = Board()
test.base_board()
test.piece_init()
test.display()
