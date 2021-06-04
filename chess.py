import numpy as np
import matplotlib.pyplot as plt
import string

#Colours available in four player chess
colour_list = ('Red', 'Blue', 'Yellow', 'Green')

#List of available pieces with point value and corresponding unicode 
piece_list = {
            'Pawn': {'value': 1, 'unicode': '\u265F', 'symbol': ''},
            'Knight': {'value': 3, 'unicode': '\u265E', 'symbol': 'N'},
            'Bishop': {'value': 5, 'unicode': '\u265D', 'symbol': 'B'},
            'Rook': {'value': 5, 'unicode': '\u265C', 'symbol': 'R'},
            'Queen': {'value': 9, 'unicode': '\u265B', 'symbol': 'Q'},
            'King': {'value': 20, 'unicode': '\u265A', 'symbol': 'K'}
        }

alphabet = string.ascii_lowercase

#Creates class for chessboard
class Board:
    #Default board is set as 14 rows/columns and with RBYG colours
    def __init__(self, nrows = 14, ncols = 14, corner = 3, colours = 
                colour_list):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.colours = colours
        self.move_list = []

    #Creates empty board and initialises squares
    def base_board(self):
        #Initialise matrix of grid to be encoded with rgb colour code
        image = np.zeros((self.nrows, self.ncols, 3))
        squares = np.empty((self.nrows, self.ncols), dtype = 'object')

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
                    squares[i][j] = Square(i+1, j+1, blocked = 'True')
                else:
                    squares[i][j] = Square(i+1, j+1)
        self.image = image
        self.squares = squares
        #Initialise data for all pieces on board - assumed default piece
        #config if not stated otherwise
    def piece_init(self, piece_order = ['Rook', 'Knight', 'Bishop',
        'King', 'Queen', 'Bishop', 'Knight', 'Rook']):
        pieces = []
        for i in range(8):
            self.squares[1][10-i].add_piece(Piece('Pawn', 'Red'))
            self.squares[10-i][1].add_piece(Piece('Pawn', 'Blue'))
            self.squares[12][3+i].add_piece(Piece('Pawn', 'Yellow'))
            self.squares[3+i][12].add_piece(Piece('Pawn', 'Green'))

            self.squares[0][10-i].add_piece(Piece(piece_order[i], 'Red'))
            self.squares[10-i][0].add_piece(Piece(piece_order[i], 'Blue'))
            self.squares[13][3+i].add_piece(Piece(piece_order[i], 'Yellow'))
            self.squares[3+i][13].add_piece(Piece(piece_order[i], 'Green'))
        self.pieces = pieces

    #Outputs image of the current board position including pieces
    def display(self):

        fig, ax = plt.subplots(figsize=(cm_to_inch(self.nrows,self.ncols)))

        ax.imshow(self.image)

        for square in self.squares.ravel():
            if square.piece == None:
                continue
            else:
                piece = square.piece

            plt.text(square.coord_to_position('file', self.nrows),
                    square.coord_to_position('rank', self.ncols),
                    piece_list[piece.name]['unicode'], 
                    fontsize = '20', color = piece.colour, 
                    transform = ax.transAxes) 

        row_labels = range(self.nrows, 0, -1)
        col_labels = list(alphabet[:self.ncols])
        plt.xticks(range(self.ncols), col_labels)
        plt.yticks(range(self.nrows), row_labels)

        plt.show(block = False)

    def move(self, move_start, move_end):
        if self.move_list == []:
            self.move_list.append(Move(1, colour_list[0]))
        else:
            index_ = (colour_list.index(self.move_list[-1].colour) + 1) %4
            if self.move_list[-1].colour == colour_list[-1]:
                move_number = self.move_list[-1].number + 1
            else:
                move_number = self.move_list[-1].number

            self.move_list.append(Move(move_number, colour_list[index_]))

        file_start, rank_start = move_to_rank_file(move_start)
        file_end, rank_end = move_to_rank_file(move_end)

        piece_start = self.squares[rank_start-1][file_start-1].piece
        self.squares[rank_end-1][file_end-1].add_piece(piece_start)
        self.squares[rank_start-1][file_start-1].remove_piece()

        
        plt.gca().clear()

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.value = piece_list[name]['value']

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

class Square:
    def __init__(self, rank, file_, blocked = False):
        self.rank = rank
        self.file_ = file_
        self.name = rank + file_
        self.piece = None
        self.blocked = blocked

    def add_piece(self, piece):
        self.piece = piece

    def remove_piece(self):
        self.piece = None
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

def move_to_rank_file(move_name):
    file_letter = move_name[0]
    file_number = int(alphabet.find(file_letter))+1
    rank_number = int(move_name[1:])
    return file_number, rank_number

test = Board()
test.base_board()
test.piece_init()
test.display()

game = True

while game == True:
    move_start = input("Square to move from: ")
    move_end = input("Square to move to: ")
    test.move(move_start, move_end)
    test.display()
