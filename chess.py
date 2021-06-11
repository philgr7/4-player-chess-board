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
        self.king_loc = {}

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
            #Loop initialises based on default piece locations
        for i in range(8):
            self.piece_add(self.squares[1][10-i], Piece('Pawn', 'Red'))
            self.piece_add(self.squares[10-i][1], Piece('Pawn', 'Blue'))
            self.piece_add(self.squares[12][3+i], Piece('Pawn', 'Yellow'))
            self.piece_add(self.squares[3+i][12], Piece('Pawn', 'Green'))

            self.piece_add(self.squares[0][10-i], Piece(piece_order[i], 'Red'))
            self.piece_add(self.squares[10-i][0], Piece(piece_order[i], 
                            'Blue'))
            self.piece_add(self.squares[13][3+i], Piece(piece_order[i], 
                            'Yellow'))
            self.piece_add(self.squares[3+i][13], Piece(piece_order[i], 
                            'Green'))

    #Finds square object based on board co-ords
    def square_find(self, square_code):
        file_, rank = move_to_rank_file(square_code)
        return self.squares[rank-1][file_-1]

    #After a move is requested if rules is turned on then a check is done
    #for legality and the move is applied and stored
    def move(self, move_start, move_end):
        piece_start = self.square_find(move_start).piece
        block_end = self.square_find(move_end).blocked

        #Checks if piece in start square
        if piece_start == None:
            return print('No piece in start square')

        if block_end:
            return False

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
            old_piece = self.square_find(move_end).piece
            self.piece_add(self.square_find(move_end), piece_start)
            self.square_find(move_start).remove_piece()

            if self.rules == True:
                king_checks = self.check_test()
                for idx, king_col in enumerate(king_checks):
                    if king_col == colour:
                        print('King in check')
                        if old_piece is None:
                            self.square_find(move_end).remove_piece()
                        else:
                            self.piece_add(self.square_find(move_end), 
                                            old_piece)

                        self.piece_add(self.square_find(move_start), 
                                            piece_start)
                        return False
                    else:
                        mate_test = self.test_mate(king_col)
                        if mate_test:
                            print('Checkmate')
            self.square_find(move_end).piece.moved = True
            self.move_list.append(attempt_move)
            return True
        else:
            print('Invalid move entered')
            return False

    #Check if legal move is being made
    def legal_check(self, move, piece, dummy = False):
        #Checks if end square is blocked by piece of same colour
        try:
            if move.colour == self.square_find(move.end).piece.colour:
                return False
        except AttributeError:
            pass

        if dummy == False:
            #If colour in start square not same as player who should be playing
            if move.colour != piece.colour and dummy == False:
                print('Invalid move - {} to move'.format(move.colour))
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
        obstacle = self.hori_obst(move)

        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == move.end:
            return True
        else:
            return False

    #Test movement along vertical lines
    def verti_test(self, move):
        if move.r_start == move.r_end or move.f_start != move.f_end:
            return False

        obstacle = self.verti_obst(move)

        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == move.end:
            return True
        else:
            return False

    #Tests for movement along diagonal lines
    def diag_test(self, move):

        #Either sum or difference of rank/file is constant along a diagonal

        sum_equal = (move.r_start + move.f_start) == (move.r_end + move.f_end)
        diff_equal = (move.r_start - move.f_start) == (move.r_end - move.f_end)

        if sum_equal == False and diff_equal == False:
            return False

        obstacle = self.diag_obst(move)
        
        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == move.end:
            return True
        else:
            return False

    def hori_obst(self, move):
        if move.f_start < move.f_end:
            step = 1
        else:
            step = -1

        range_start = move.f_start - 1 + step
        range_end = move.f_end - 1 + step

        #Check for obstruction on path
        for i in range(range_start, range_end, step):
            obstruction = self.squares[move.r_start-1][i].obstruct()
            if obstruction != False:
                return obstruction
        return False

    def verti_obst(self, move):
        if move.r_start < move.r_end:
            step = 1
        else:
            step = -1
        
        range_start = move.r_start - 1 + step
        range_end = move.r_end - 1 + step

        for i in range(range_start, range_end, step):
            obstruction = self.squares[i][move.f_start-1].obstruct()
            if obstruction != False:
                return obstruction
        return False

    def diag_obst(self, move):
        if move.r_start < move.r_end:
            step_r = 1
        else:
            step_r = -1
        if move.f_start < move.f_end:
            step_f = 1
        else:
            step_f = -1

        ind_r = move.r_start - 1 + step_r
        ind_f = move.f_start - 1 + step_f

        diff = abs(move.r_diff())

        for i in range(0, diff):
            obstruct_ = (self
            .squares[ind_r+i*step_r][ind_f+i*step_f].obstruct())
            if obstruct_ != False:
                return obstruct_
        return False
        
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
            self.king_loc[move.colour] = move.end
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
        moved_check = piece.last_move

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

    #Find pieces in hori/verti/diag line of sight of a king as well as 
    #knight moves on king and check if there is piece that checks the
    #king
    def check_test(self):
        print(self.king_loc)
        kings_in_check = []
        for key in self.king_loc:
            king_col = key
            king_loc = self.king_loc[key]

            check_pieces = self.hori_verti_diag_extent(king_loc)
            move_end = king_loc
            print(key)
            for idx, piece in enumerate(check_pieces):
                move_start = piece.loc
                colour = piece.colour
                attempt_move = Move(0, colour, move_start, move_end)
                check_test = self.legal_check(attempt_move, piece, 
                                            dummy = True)
                print(piece.loc, check_test)
                if check_test:
                    if king_col not in kings_in_check:
                        kings_in_check.append(king_col)
        return kings_in_check

    def hori_verti_diag_extent(self, move_code):
        los_list = []
       
        file_, rank = move_to_rank_file(move_code)

        loop_directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
                            [0, 1], [1, -1], [1, 0], [1, 1]]

        for idx, val in enumerate(loop_directions):
            f_index = file_ - 1 
            r_index = rank - 1
            f_step = val[0]
            r_step = val[1]
            stop = False
            while ((f_index < self.ncols and f_index >= 0) and
                    (r_index < self.nrows and r_index >= 0) and 
                    stop == False):
                
                f_index = f_index + f_step
                r_index = r_index + r_step

                if f_index < 0 or r_index < 0:
                    continue

                try:
                    los = self.squares[r_index][f_index].obstruct()
                except IndexError:
                    los = 0
                    pass

                if not isinstance(los, int):
                    stop = True
                    los_list.append(los)
                
        return los_list

    def test_mate(self, king_col):

        move_start = self.king_loc[king_col]
        piece = self.square_find(move_start).piece
        
        file_, rank = move_to_rank_file(move_start)
        
        move_direct = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
                        [0, 1], [1, -1], [1, 0], [1, 1]]

        for idx, val in enumerate(move_direct):
            f_index = file_ - 1 + val[0]
            r_index = rank - 1 + val[1]
            
            if (f_index < 0 or f_index > self.ncols - 1 or
                r_index < 0 or r_index > self.nrows - 1):
                continue
            move_end = self.squares[r_index][f_index].name

            attempt_move = Move(0, king_col, move_start, move_end)
            check_test = self.legal_check(attempt_move, piece, 
                                    dummy = True)
            if check_test:
                return False
        return True

    def piece_add(self, square, piece):
        square.add_piece(piece)
        if piece.name == 'King':
            self.king_loc[piece.colour] = piece.loc

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, last_move = False):
        self.name = name
        self.colour = colour
        self.value = piece_list[name]['value']
        self.last_move = last_move

        self.loc = 0

        self.direction = colour_list.index(colour)

class Square:
    def __init__(self, rank, file_, blocked = False):
        self.rank = rank
        self.file_ = file_
        self.name = alphabet[file_-1] + '{}'.format(rank)
        self.piece = None
        self.blocked = blocked

    def add_piece(self, piece):
        piece.loc = self.name
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
        elif self.blocked == True:
            return True
        else:
            return self.piece

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

        self.board = board

        self.s_width = self.board_width/self.board.ncols
        self.s_height = self.board_height/self.board.nrows

        self.display()

    def display(self):
        self.geometry('1000x700')
        self.canvas = tk.Canvas(self, width=self.board_width, 
                                height = self.board_height)
        self.canvas.place(relx=0.5, rely=0.5, anchor = 'center')
        
        piece_loc = {}
        for i in range(self.board.nrows):
            for j in range(self.board.ncols):
                if (i + j)%2 == 0:
                    colour = 'white'
                else:
                    colour = 'grey'
                if ((i < self.board.corner or 
                    i >= self.board.nrows - self.board.corner) and
                    (j < self.board.corner or 
                    j >= self.board.ncols - self.board.corner)):
                    colour = 'black'

                self.canvas.create_rectangle(i*self.s_width,
                        j*self.s_height, (i+1)*self.s_width,
                        (j+1)*self.s_height, fill = colour)
        
        #Checks if square has piece and if it does then plots it with 
        #respective symbol
        for square in self.board.squares.ravel():
            if square.piece == None:
                continue
            else:
                piece = square.piece

            pos_x = (square.file_ - 0.5) * self.s_height
            pos_y = (self.board.nrows + 0.5 - square.rank) * self.s_width

            text = self.canvas.create_text(pos_x, pos_y,
                text = piece_list[piece.name]['unicode'], 
                fill = piece.colour, font = (None, 35))

            piece_loc[text] = piece.loc

        self.piece_loc = piece_loc

        self.canvas.bind('<ButtonPress-1>', self.pick_up)
        self.canvas.bind('<B1-Motion>', self.drag)

        self.canvas.bind('<ButtonRelease-1>', self.drop) 

    def pick_up(self, event):
   
        object_id = self.canvas.find_closest(event.x, event.y, halo=0)[0]

        if object_id in self.piece_loc.keys():
            self.drag_piece = object_id
            self.drag_x = event.x
            self.drag_y = event.y
        else:
            self.drag_piece = None

    def drag(self, event):
        if self.drag_piece == None:
            return

        delta_x = event.x - self.drag_x
        delta_y = event.y - self.drag_y

        self.canvas.move(self.drag_piece, delta_x, delta_y)

        self.drag_x = event.x
        self.drag_y = event.y

    def drop(self, event):
        if self.drag_piece == None:
            return

        index_x, index_y = self.coords_to_index(event.x, event.y)
        
        move_start = self.piece_loc[self.drag_piece]
        init_file, init_rank = move_to_rank_file(move_start)
        index_init_x = init_file
        index_init_y = self.board.nrows + 1 - init_rank

        if (index_x > self.board.ncols or index_x < 1 or 
            index_y > self.board.nrows or index_y < 1):
            move_test = False

        else:
            move_end = self.index_to_move(index_x, index_y) 
            move_test = self.board.move(move_start, move_end)
        
        if move_test:
            pos_x = (index_x-0.5)*self.s_height
            pos_y = (index_y-0.5)*self.s_width

            try:
                piece_delete = list(self.piece_loc.keys())[list(
                    self.piece_loc.values()).index(move_end)]

                self.canvas.delete(piece_delete)
                
                self.piece_loc[piece_delete] = False
            except ValueError:
                pass

            self.piece_loc[self.drag_piece] = move_end

        else:
            pos_x = (index_init_x-0.5)*self.s_height
            pos_y = (index_init_y-0.5)*self.s_width

        self.canvas.coords(self.drag_piece, (pos_x, pos_y))

    def coords_to_index(self, x, y):
        index_x = np.ceil(x/self.s_width)
        index_y = np.ceil(y/self.s_height)
        return index_x, index_y

    def index_to_move(self, index_x, index_y):
        file_ = round(index_x)
        rank = round(self.board.nrows + 1 - index_y)
        move_code = alphabet[file_-1] + '{}'.format(rank)
        return move_code

def move_to_rank_file(move_name):
    file_letter = move_name[0]
    file_number = int(alphabet.find(file_letter))+1
    rank_number = int(move_name[1:])
    return file_number, rank_number

game = Display()
game.mainloop()

