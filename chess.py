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
                colour_list, rules = True):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.colours = colours
        self.rules = rules
        self.move_list = []

        self.base_board()
        self.piece_init()
        self.display(init = True)

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
                    squares[i][j] = Square(i+1, j+1, blocked = True)
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
    def display(self, init = False):
        if init == True:
            fig, ax = plt.subplots(figsize=(cm_to_inch(self.nrows,self.ncols)))
        else:
            plt.cla()
            ax = self.ax
            fig = self.fig
        
        ax.imshow(self.image)

        #Checks if square has piece and if it does then plots it with 
        #respective symbol
        for square in self.squares.ravel():
            if square.piece == None:
                continue
            else:
                piece = square.piece

            ax.text(square.coord_to_position('file', self.nrows),
                    square.coord_to_position('rank', self.ncols),
                    piece_list[piece.name]['unicode'], 
                    fontsize = '20', color = piece.colour, 
                    transform = ax.transAxes) 

        row_labels = range(self.nrows, 0, -1)
        col_labels = list(alphabet[:self.ncols])
        ax.set_xticks(range(self.ncols))
        ax.set_xticklabels(col_labels)
        ax.set_yticks(range(self.nrows))
        ax.set_yticklabels(row_labels)
        
        if init == True:
            plt.show(block = False)
        else:
            plt.draw()

        self.ax = ax
        self.fig = fig

    def square_find(self, square_code):
        file_, rank = move_to_rank_file(square_code)
        return self.squares[rank-1][file_-1]

    #After a move is requested if rules is turned on then a check is done
    #for legality and the move is applied and stored
    def move(self, move_start, move_end):
        piece_start = self.square_find(move_start).piece

        if piece_start == None:
            return print('No piece in start square')

        if self.move_list == []:
            move_number = 1
            colour = colour_list[0]
        else:
            index_ = (colour_list.index(self.move_list[-1].colour) + 1) %4
            colour = colour_list[index_]
            if self.move_list[-1].colour == colour_list[-1]:
                move_number = self.move_list[-1].number + 1
            else:
                move_number = self.move_list[-1].number

        attempt_move = Move(move_number, colour, move_start, move_end)

        if self.rules == True:
            move_check = self.legal_check(attempt_move, piece_start)
        else:
            move_check = True

        file_start, rank_start = move_to_rank_file(move_start)
        file_end, rank_end = move_to_rank_file(move_end)

        if move_check == True:
            self.squares[rank_end-1][file_end-1].add_piece(piece_start)
            self.squares[rank_start-1][file_start-1].remove_piece()
            self.move_list.append(attempt_move)
            
        else:
            print('Invalid move entered')

    #Check if legal move is being made
    def legal_check(self, move, piece):
        #Checks if end square is blocked by piece of same colour
        try:
            if move.colour == self.square_find(move.end).piece.colour:
                return False
        except AttributeError:
            pass

        #If colour in start square not same as player who should be playing
        if move.colour != piece.colour:
            return False

        #Tests for obstructions and whether piece has capability
        #to move between designated squares

        #Rook move horizontally or vertically
        if piece.name == 'Rook':
            return any((self.hori_test(move), self.verti_test(move)))

        #Queen move horizontally, vertically or diagonally
        elif piece.name == 'Queen':
            return any((self.hori_test(move), self.verti_test(move),
                        self.diag_test(move)))

        #Bishop move diagonally
        elif piece.name == 'Bishop':
            return self.diag_test(move)

        #Pawn moves forwards 1 square or can capture diagonally 1 square or
        #can enpassant
        elif piece.name == 'Pawn':
            direct = piece.direction
            piece_check = self.square_find(move.end).piece
            print(direct, piece_check, move.r_diff(), move.f_diff())
            if direct == 1 and move.r_diff() == 1:
                if abs(move.f_diff()) == 1:
                    if piece_check != None:
                        return True
                elif move.f_diff() == 0:
                    if piece_check == None:
                        return True

            if direct == 2 and move.f_diff() == 1:
                if abs(move.r_diff()) == 1:
                    if piece_check != None:
                        return True
                elif move.r_diff() == 0:
                    if piece_check == None:
                        return True

            if direct == 3 and move.r_diff() == -1:
                if abs(move.f_diff()) == 1:
                    if piece_check != None:
                        return True
                elif move.f_diff() == 0:
                    if piece_check == None:
                        return True

            if direct == 4 and move.f_diff() == -1:
                if abs(move.r_diff()) == 1:
                    if piece_check != None:
                        return True
                elif move.r_diff() == 0:
                    if piece_check == None:
                        return True
            return False


        #King can move 1 square in any direction (assuming not in check)
        elif piece.name == 'King':
            if abs(move.f_diff()) <= 1 and abs(move.r_diff()) <= 1:
                return True
            else: 
                return False

        elif piece.name == 'Knight':
            min_diff = abs(min(move.f_diff()), abs(move.r_diff()))
            max_diff = abs(max(move.f_diff()), abs(move.r_diff()))
            if max_diff == 2 and min_diff == 1:
                return True
            else:
                return False
        return True           


    #Test movement along horizontal lines
    def hori_test(self, move):
        #movement can only occur if file changes and rank stays the same
        if move.f_start == move.f_end or move.r_start != move.r_end:
            return False
            
        range_start = min(move.f_start, move.f_end)
        range_end = max(move.f_start, move.f_end) - 1

        #Check if square on path is blocked or contains a piece
        for i in range(range_start, range_end):
            if self.squares[move.r_start-1][i].obstruct() == True:
                return False
        
        return True


    def verti_test(self, move):
        if move.r_start == move.r_end or move.f_start != move.f_end:
            return False

        range_start = min(move.r_start, move.r_end)
        range_end = max(move.r_start, move.r_end) - 1

        #Check if square on path is blocked or contains a piece
        for i in range(range_start, range_end):
            if self.squares[i][move.f_start-1].obstruct() == True:
                return False
        
        return True

    def diag_test(self, move):
        if (((move.r_start + move.f_start) != (move.r_end + move.f_end)) and
        ((move.r_start - move.f_start) != (move.r_end - move.f_end))):
            return False
        min_r = min(move.r_start, move.r_end) - 1
        diff = abs(move.r_diff())

        if (move.r_start + move.f_start) == (move.r_end + move.f_end):
            f_loop = max(move.f_start, move.f_end) - 1
            for i in range(1, diff):
                if self.squares[min_r+i][f_loop-i].obstruct() == True:
                    return False
        else:
            f_loop = min(move.f_start, move.f_end) - 1
            for i in range(1, diff):
                if self.squares[min_r+i][f_loop+i].obstruct() == True:
                    return False

        return True

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
        self.value = piece_list[name]['value']
        if self.name == 'Pawn':
            self.direction = colour_list.index(colour) + 1

    #Returns string of position of piece
    def position(self):
        return self.file_ + self.rank

class Square:
    def __init__(self, rank, file_, blocked = False):
        self.rank = rank
        self.file_ = file_
        self.name = alphabet[file_-1] + '{}'.format(rank)
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

    def obstruct(self):
        if self.blocked == False and self.piece == None:
            return False
        else:
            return True

    #Returns string of position of piece
    def position(self):
        return self.file_ + self.rank

#Creates class for a chess move
class Move:
    def __init__(self, number, colour, start, end):
        self.number = number
        self.colour = colour
        self.start = start
        self.f_start, self.r_start = move_to_rank_file(self.start)
        self.end = end
        self.f_end, self.r_end = move_to_rank_file(self.end)

    def r_diff(self):
        return self.r_end - self.r_start

    def f_diff(self):
        return self.f_end - self.f_start
    
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

game = True

while game == True:
    move_start = input("Square to move from: ")
    if move_start == 'end':
        break
    move_end = input("Square to move to: ")
    if move_end == 'end':
        break
    test.move(move_start, move_end)
    test.display()
