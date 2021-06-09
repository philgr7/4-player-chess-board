import numpy as np
import matplotlib.pyplot as plt
import string
import tkinter as tk
import time

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

        self.board_init()
        self.piece_init()

    #Squares initialised to position on board
    def board_init(self):
        
        squares = np.empty((self.nrows, self.ncols), dtype = 'object')

        for i in range(self.nrows):
            for j in range(self.ncols):
                if ((i < self.corner or i >= self.nrows - self.corner) 
                    and (j < self.corner or j >= self.ncols - self.corner)):
                    squares[i][j] = Square(i+1, j+1, blocked = True)
                else:
                    squares[i][j] = Square(i+1, j+1)
        
        self.squares = squares
        
        #Initialise data for all pieces on board - assumed default piece
        #config if not stated otherwise which is defined 
    def piece_init(self, piece_order = ['Rook', 'Knight', 'Bishop',
        'King', 'Queen', 'Bishop', 'Knight', 'Rook']):
        pieces = []
            #Loop initialises based on default piece locations
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

    #Finds square object based on board co-ords
    def square_find(self, square_code):
        file_, rank = move_to_rank_file(square_code)
        return self.squares[rank-1][file_-1]

    #After a move is requested if rules is turned on then a check is done
    #for legality and the move is applied and stored
    def move(self, move_start, move_end):
        piece_start = self.square_find(move_start).piece

        #Checks if piece in start square
        if piece_start == None:
            return print('No piece in start square')

        #Based on move order sets what colour should be moving and what
        #move number has been reached
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

        #If rules turned on, checks if legal move has been made
        if self.rules == True:
            move_check = self.legal_check(attempt_move, piece_start)
        else:
            move_check = True

        #Carries out move and updates square objects, appending new move to
        #list
        if move_check == True:
            self.square_find(move_end).add_piece(piece_start)
            self.square_find(move_end).piece.moved = True
            self.square_find(move_start).remove_piece()
            self.move_list.append(attempt_move)
            return True
        else:
            print('Invalid move entered')
            return False

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

        #Tests check for obstructions and whether piece has capability
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

        #King can move 1 square in any direction (assuming not in check)
        elif piece.name == 'King':
            return self.king_test(move)

        elif piece.name == 'Knight':
            return self.knight_test(move)

        elif piece.name == 'Pawn':
            return self.pawn_test(move, piece)

    #Test movement along horizontal lines
    def hori_test(self, move):
        #movement can only occur if file changes and rank stays the same
        if move.f_start == move.f_end or move.r_start != move.r_end:
            return False
            
        #index in python starts at 0, file/rank at 1, don't want to include
        #start square so range_start unchanged from min
        range_start = min(move.f_start, move.f_end)
        range_end = max(move.f_start, move.f_end) - 1

        #Check for obstruction on path
        for i in range(range_start, range_end):
            if self.squares[move.r_start-1][i].obstruct() == True:
                return False
        return True

    #Test movement along vertical lines
    def verti_test(self, move):
        if move.r_start == move.r_end or move.f_start != move.f_end:
            return False

        range_start = min(move.r_start, move.r_end)
        range_end = max(move.r_start, move.r_end) - 1

        for i in range(range_start, range_end):
            if self.squares[i][move.f_start-1].obstruct() == True:
                return False
        return True

    #Tests for movement along diagonal lines
    def diag_test(self, move):

        #Either sum or difference of rank/file is constant along a diagonal

        sum_equal = (move.r_start + move.f_start) == (move.r_end + move.f_end)
        diff_equal = (move.r_start - move.f_start) == (move.r_end - move.f_end)

        if sum_equal == False and diff_equal == False:
            return False

        min_r = min(move.r_start, move.r_end) - 1
        diff = abs(move.r_diff())

        #If sum equal then rank/file increase in opposite direction
        if sum_equal == True:
            f_loop = max(move.f_start, move.f_end) - 1
            for i in range(1, diff):
                if self.squares[min_r+i][f_loop-i].obstruct() == True:
                    return False

        #if difference equal then rank/file increase in same direction
        elif diff_equal == True:
            f_loop = min(move.f_start, move.f_end) - 1
            for i in range(1, diff):
                if self.squares[min_r+i][f_loop+i].obstruct() == True:
                    return False

        return True

    def knight_test(self, move):

        #If rank/file change by 1/2 in any order than move is legal
        min_diff = min(abs(move.f_diff()), abs(move.r_diff()))
        max_diff = max(abs(move.f_diff()), abs(move.r_diff()))
        if max_diff == 2 and min_diff == 1:
            return True
        else:
            return False

    def king_test(self, move):
        #Moves by 1 in any direction
        if abs(move.f_diff()) <= 1 and abs(move.r_diff()) <= 1:
            return True
        else: 
            return False

    def pawn_test(self, move, piece):
        #Based on direction pawn is facing, defines rotation vectors that
        #allow for testing if move is valid
        direct = piece.direction
        theta = np.radians(90*direct)
        c, s = round(np.cos(theta)), round(np.sin(theta))

        #Arrays cover moving forward and capturing on either diagonal
        diff_arr = np.array([c,s])
        diff_diag_1 = np.array([c-s, s-c])
        diff_diag_2 = np.array([c+s, s+c])

        piece_check = self.square_find(move.end).piece
        moved_check = piece.moved

        #Compares allowed moves for pawn in certain direction with 
        #attempted move for cases of moving 1 or 2 squares forward or capture
        rf_diff = [move.r_diff(), move.f_diff()]
    
        m1_check = np.array_equal(rf_diff, diff_arr)
        m2_check = np.array_equal(rf_diff, 2*diff_arr)
        diag_check = (np.array_equal(rf_diff, diff_diag_1) or
                    np.array_equal(rf_diff, diff_diag_2))

        #If no piece present then check if can move 1 or 2 squares
        if piece_check == None:
            if m1_check == True:
                return True
            elif m2_check == True and moved_check == False:
                return True
        #If piece present then check if diagonal capture is possible
        elif piece_check != None:
            if diag_check == True:
                return True
        return False

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, moved = False, last_move = 0):
        self.name = name
        self.colour = colour
        self.value = piece_list[name]['value']
        self.moved = moved
        self.last_move = last_move

        if self.name == 'Pawn':
            self.direction = colour_list.index(colour)

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

class Display(tk.Tk):

    def __init__(self, board = Board()):
        super().__init__()
        self.board_height = 500
        self.board_width = 500

        self.nrows = board.nrows
        self.ncols = board.ncols
        self.corner = board.corner

        self.s_width = self.board_width/board.ncols
        self.s_height = self.board_height/board.nrows

        self.display(board)

    def display(self, board):
        self.geometry('1000x600')
        self.canvas = tk.Canvas(self, width=self.board_width, 
                                height = self.board_height)
        self.canvas.place(relx=0.5, rely=0.5, anchor = 'center')
        
        text_list = []
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i + j)%2 == 0:
                    colour = 'white'
                else:
                    colour = 'grey'
                if ((i < self.corner or i >= self.nrows - self.corner) and
                    (j < self.corner or j >= self.ncols - self.corner)):
                    colour = 'black'

                self.canvas.create_rectangle(i*self.s_width,
                        j*self.s_height, (i+1)*self.s_width,
                        (j+1)*self.s_height, fill = colour)
        
        #Checks if square has piece and if it does then plots it with 
        #respective symbol
        for square in board.squares.ravel():
            if square.piece == None:
                continue
            else:
                piece = square.piece

            pos_x = (square.file_ - 0.5) * self.s_height
            pos_y = (self.nrows + 0.5 - square.rank) * self.s_width

            text = self.canvas.create_text(pos_x, pos_y,
                text = piece_list[piece.name]['unicode'], 
                fill = piece.colour, font = (None, 35))
                
            text_list.append(text)

        self.text_list = text_list

        self.canvas.bind('<ButtonPress-1>', self.pick_up)
        self.canvas.bind('<B1-Motion>', self.drag)

        def handler(event, self=self, board=board):
            return self.drop(event, board)
        self.canvas.bind('<ButtonRelease-1>', handler) 

    def pick_up(self, event):
   
        object_id = self.canvas.find_closest(event.x, event.y, halo=5)[0]

        if object_id in self.text_list:
            self.drag_piece = object_id
            self.drag_init_x = event.x
            self.drag_init_y = event.y
            self.drag_x = event.x
            self.drag_y = event.y
        else:
            self.drag_piece = None

    def drag(self, event):
        if self.drag_piece == None:
            pass

        else:
            delta_x = event.x - self.drag_x
            delta_y = event.y - self.drag_y

            self.canvas.move(self.drag_piece, delta_x, delta_y)

            self.drag_x = event.x
            self.drag_y = event.y

    def drop(self, event, board):
        if self.drag_piece == None:
            pass
        else:
            index_init_x, index_init_y = self.coords_to_index(
                    self.drag_init_x, self.drag_init_y)
            index_x, index_y = self.coords_to_index(event.x, event.y)

            move_start = self.index_to_move(index_init_x, index_init_y)
            move_end = self.index_to_move(index_x, index_y)

            move_test = board.move(move_start, move_end)

            if move_test:
                pos_x = (index_x-0.5)*self.s_height
                pos_y = (index_y-0.5)*self.s_width

                piece_delete = self.canvas.find_closest(pos_x, pos_y)[0]

                if piece_delete == self.drag_piece:
                    pass

                elif piece_delete in self.text_list:
                    self.canvas.delete(piece_delete)

            else:
                pos_x = (index_init_x-0.5)*self.s_height
                pos_y = (index_init_y-0.5)*self.s_width
                time.sleep(1)

            self.canvas.coords(self.drag_piece, (pos_x, pos_y))

    def coords_to_index(self, x, y):
        index_x = np.ceil(x/self.s_width)
        index_y = np.ceil(y/self.s_height)
        return index_x, index_y

    def index_to_move(self, index_x, index_y):
        file_ = round(index_x)
        rank = round(self.nrows + 1 - index_y)
        move_code = alphabet[file_-1] + '{}'.format(rank)
        return move_code

#Converts cm to inches for figure size
def cm_to_inch(*args):
    inch = 2.54
    return tuple(i/inch for i in args)

def move_to_rank_file(move_name):
    file_letter = move_name[0]
    file_number = int(alphabet.find(file_letter))+1
    rank_number = int(move_name[1:])
    return file_number, rank_number

game = Display()
game.mainloop()

