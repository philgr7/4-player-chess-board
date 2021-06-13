import numpy as np
import matplotlib.pyplot as plt
import string
import tkinter as tk
import time

#Colours available in four player chess
COLOUR_INFO = ('Red', 'Blue', 'Yellow', 'Green')

#List of available pieces with point value and corresponding unicode 
PIECE_INFO = {
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
                COLOUR_INFO, rules = True):
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
    def move(self, move_start, move_end, dummy = False):
        piece_start = self.square_find(move_start).piece

        #Checks if piece in start square
        if piece_start == None:
            return print('No piece in start square')

        #If end square is blocked from initialisation then move cannot occur
        if self.square_find(move_end).blocked:
            return False

        if not dummy:
            #Based on move order sets what colour should be moving and what
            #move number has been reached
            if self.move_list == []:
                move_number = 1
                colour = self.colours[0]
            else:
                num_clrs = len(self.colours)
                index_ = ((self.colours.index(
                                self.move_list[-1].colour) + 1) %num_clrs)
                colour = self.colours[index_]
                if self.move_list[-1].colour == self.colours[-1]:
                    move_number = self.move_list[-1].number + 1
                else:
                    move_number = self.move_list[-1].number
        else:
            colour = None
            move_number = 0

        #Creates Move object for testing that will be applied if success 
        attempt_move = Move(move_number, colour, move_start, move_end)

        #If rules turned on, checks if legal move has been made
        if self.rules == True:
            move_check = self.legal_check(attempt_move, piece_start, dummy)
        else:
            move_check = True

        #Carries out move and does finally confirms existence of checks
        #if successful then updates square objects, appending new move to
        #list
        if move_check == True:
            old_piece = self.square_find(move_end).piece
            self.piece_add(self.square_find(move_end), piece_start)
            self.square_find(move_start).remove_piece()
            
            new_check = 0 #counter for how many new_checks are given
            #If rules on all kings are checked for whether in check
            if self.rules == True:
                king_checks = self.all_check_test()
                
                if dummy:
                    if old_piece is None:
                        self.square_find(move_end).remove_piece()
                    else:
                        self.piece_add(self.square_find(move_end), 
                                        old_piece)

                    self.piece_add(self.square_find(move_start), 
                                        piece_start)
                    return king_checks

                print(king_checks)

                for king_col in king_checks:
                    #if king of colour of move in check then move
                    #is illegal and so need to reset positions of 
                    #pieces which were shadow moved
                    if king_col == colour:
                        if old_piece is None:
                            self.square_find(move_end).remove_piece()
                        else:
                            self.piece_add(self.square_find(move_end), 
                                            old_piece)

                        self.piece_add(self.square_find(move_start), 
                                            piece_start)
                        print('King in check')
                        return False

                    #If king of different colour in check then need to 
                    #confirm if mated
                    else:
                        mate_test = self.test_mate(king_checks[king_col],
                                                    king_col)
                        if mate_test:
                            print('Checkmate')
            
                #Confirm whether move caused a new check
                if king_checks:
                    attempt_move.checks = king_checks
                    prev_move_checks = self.move_list[-1].checks
                    for king_col in king_checks:
                        if not king_col in prev_move_checks:
                            new_check = new_check + 1
                    
            #If reaches here then move is allowed to occur and is recorded

            self.square_find(move_end).piece.moved = True
            self.move_list.append(attempt_move)
            attempt_move.pgn_create(piece_start, old_piece, new_check)
            return True
        #Return invalid move if move_check has failed
        else:
            if not dummy:
                print('Invalid move entered')
            return False

    #Check if legal move is being made, dummy is true if move is not 
    #suggested but just a check for legality of a board position
    def legal_check(self, move, piece, dummy = False):
        #Checks if end square is blocked by piece of same colour
        try:
            if piece.colour == self.square_find(move.end).piece.colour:
                return False
        except AttributeError:
            pass

        #If colour in start square not same as player who should be playing
        #doesn't matter if dummy move
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
            
        #Checks if obstacle present - if no obstacle (False) or obstacle
        #is at end square then the move is legal. obstacle = True if 
        #trying to pass through blocked squares
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
        #movement can only occur if rank changes and file stays the same
        if move.r_start == move.r_end or move.f_start != move.f_end:
            return False

        #same obstacle logic as hori_test
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

        #Same obstacle logic as hori_test
        obstacle = self.diag_obst(move)
        
        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == move.end:
            return True
        else:
            return False

    #checks for first obstacle for a given horizontal move
    def hori_obst(self, move):

        #step sets if needs to loop positively or negatively through squares
        if move.f_start < move.f_end:
            step = 1
        else:
            step = -1

        #Don't want to check obstacles in starting square so need to add step
        #from before loop starts
        range_start = move.f_start - 1 + step
        range_end = move.f_end - 1 + step

        #Loops between two board locations and stops if obstacle is found
        for i in range(range_start, range_end, step):
            obstruction = self.squares[move.r_start-1][i].obstruct()
            if obstruction != False:
                return obstruction
        return False

    #checks for first obstacle in given vertical move - logic same as 
    #hori_obst
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

    #Checks for first obstacle in given diagonal move
    def diag_obst(self, move):
        #step for both rank/file based on which direction move is occuring in
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

        #Use difference to loop between board positions unless obstacle found
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
        #King can move 1 space in any direction - whether king is in check
        #is checked later on
        if abs(move.f_diff()) <= 1 and abs(move.r_diff()) <= 1:
            return True
        else: 
            return False

    def pawn_test(self, move, piece):
        #Based on direction pawn is facing, defines rotation vectors that
        #allow for testing if move is valid which represents
        #[change in rank, change in file]
        direct = piece.direction
        theta = np.radians(90*direct)
        c, s = round(np.cos(theta)), round(np.sin(theta))

        #Arrays cover moving forward and capturing on either diagonal
        diff_arr = np.array([c,s])
        diff_diag_1 = np.array([c-s, s-c])
        diff_diag_2 = np.array([c+s, s+c])

        #checks for piece at end square and whether pawn has moved before
        piece_check = self.square_find(move.end).piece
        moved_check = piece.last_move

        #The change in rank/file of the attempted move 
        rf_diff = [move.r_diff(), move.f_diff()]
        
        #Compares change in rank/file of attempted move with that of
        #theoretically allowed moves (either 1 move foward, 2 moves forward
        #or diagonal piece capture
        m1_check = np.array_equal(rf_diff, diff_arr)
        m2_check = np.array_equal(rf_diff, 2*diff_arr)
        diag_check = (np.array_equal(rf_diff, diff_diag_1) or
                    np.array_equal(rf_diff, diff_diag_2))

        #If no piece present then check if can move 1 or 2 squares
        if piece_check == None:
            if m1_check == True:
                return True
            #2 moves forward only allowed if pawn has not moved
            elif m2_check == True and moved_check == False:
                return True
        #If piece present then check if diagonal capture is possible
        elif piece_check != None:
            if diag_check == True:
                return True
        return False

    def all_check_test(self):
        print(self.king_loc)

        check_list = {}
        for key in self.king_loc:
            king_col = key
            king_loc = self.king_loc[key]
            piece_checks = self.check_test(king_col, king_loc)

            if piece_checks:
                check_list[king_col] = piece_checks

        return check_list

    #Find pieces in hori/verti/diag line of sight of a king as well as 
    #knight moves on king and check if there is piece that checks the
    #king
    def check_test(self, king_col, king_loc):

        king_checks = []

        check_pieces = self.hori_verti_diag_extent(king_loc)
        move_end = king_loc
        for idx, piece in enumerate(check_pieces):
            move_start = piece.loc
            colour = piece.colour
            if colour == king_col:
                continue
            attempt_move = Move(0, colour, move_start, move_end)
            check_test = self.legal_check(attempt_move, piece, 
                                        dummy = True)
            if check_test:
                king_checks.append(piece)

        knight_checks = self.knight_extent(king_loc)

        for knight in knight_checks:
            if knight.colour != king_col:
                king_checks.append(knight)

        return king_checks

    #Returns list of pieces in hori/verti/diag line of sight of king
    def hori_verti_diag_extent(self, move_code):

        #list of piece in line of sight (los)
        los_list = []
       
        file_, rank = move_to_rank_file(move_code)

        #8 direction vectors for hori/verti/diag from king to loop over
        loop_directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
                            [0, 1], [1, -1], [1, 0], [1, 1]]

        for idx, val in enumerate(loop_directions):
            f_index = file_ - 1 
            r_index = rank - 1
            f_step = val[0]
            r_step = val[1]
            stop = False

            #f/r indices need to be within extent of cols/rows of board 
            while ((f_index < self.ncols and f_index >= 0) and
                    (r_index < self.nrows and r_index >= 0) and 
                    stop == False):
                
                #f/r indices updated at start so that starting square not used
                f_index = f_index + f_step
                r_index = r_index + r_step

                #if index update pushes index out of board extent continues
                if f_index < 0 or r_index < 0:
                    continue

                #tries to check for obstruction except if out of board extent
                try:
                    los = self.squares[r_index][f_index].obstruct()
                except IndexError:
                    los = 0
                    pass

                #if obstruct = False or True then no piece obstruction found
                #booleans are counted as integers in isinstance
                if not isinstance(los, int):
                    stop = True
                    los_list.append(los)
                
        return los_list

    def knight_extent(self, move_code):
        knight_list = []

        file_, rank = move_to_rank_file(move_code)
        f_index_start = file_ - 1
        r_index_start = rank - 1
        knight_moves = [[2, 1], [2, -1], [-2, 1], [-2, -1],
                        [1, 2], [1, -2], [-1, 2], [-1, -2]]
        for idx, val in enumerate(knight_moves):
            r_index = r_index_start + val[0]
            f_index = f_index_start + val[1]
           
            if (f_index < 0 or r_index < 0 or f_index >= self.ncols or
                r_index >= self.nrows):
                continue

            knight_check = self.squares[r_index][f_index].obstruct()
            if not isinstance(knight_check, int):
                if knight_check.name == 'Knight':
                    knight_list.append(knight_check)

        return knight_list

    #Checks if king is mated - 3 checks: if double check then king has to
    #move/capture something, if single check then either capture attacking
    #piece, king moves/captures or block line of site of piece
    def test_mate(self, king_checks, king_col):

        #Checks if king can move/capture out of check
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

            checked_checks = self.move(move_start, move_end, dummy = True) 
            if checked_checks == False:
                continue
            if not king_col in checked_checks:
                return False

        #If double check (and king can't move) then king is mated
        if len(king_checks) > 1:
            return True

        #Checks if a piece can capture the checking piece
        move_end = king_checks[0].loc
        att_pieces = (self.hori_verti_diag_extent(move_end) + 
                    self.knight_extent(move_end))

        for idx, piece in enumerate(att_pieces):
            move_start = piece.loc
            colour = piece.colour
            if colour != king_col:
                continue
            checked_checks = self.move(move_start, move_end, dummy = True)
            if checked_checks == False:
                continue
            if not king_col in checked_checks:
                return False

        #Checks if the checking piece can be obstructed (can't if knight so)
        #if mate in that case
    
        if king_checks[0].name == 'Knight':
            return True

        king_f, king_r = move_to_rank_file(self.king_loc[king_col])
        checker_f, checker_r = move_to_rank_file(move_end)

        r_start = king_r - 1
        f_start = king_f - 1

        diff_f = checker_f - king_f
        diff_r = checker_r - king_r

        if diff_f > 0:
            f_step = 1
        elif diff_f == 0:
            f_step = 0
        elif diff_f < 0:
            f_step = -1
        if diff_r > 0:
            r_step = 1
        elif diff_r == 0:
            r_step = 0
        elif diff_r < 0:
            r_step = -1

        max_diff = max(abs(diff_f), abs(diff_r))

        print(max_diff, r_step, f_step)

        for i in range(1, max_diff):
            r_index = r_start + i*r_step
            f_index = f_start + i*f_step

            square = self.squares[r_index][f_index]
            
            obstr_loc = square.name

            obstr_pieces = (self.hori_verti_diag_extent(obstr_loc) + 
                                self.knight_extent(obstr_loc))

            print(obstr_pieces, obstr_loc)
            for piece in obstr_pieces:
                if piece.colour != king_col:
                    continue
                move_start = piece.loc
                checked_checks = self.move(move_start, obstr_loc, dummy = True)
                print(checked_checks)
                if checked_checks == False:
                    continue
                if not king_col in checked_checks:
                    return False

        return True

    #Add piece to a square and updates data on king locations
    def piece_add(self, square, piece):
        square.add_piece(piece)
        if piece.name == 'King':
            self.king_loc[piece.colour] = piece.loc

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, last_move = False):
        self.name = name
        self.colour = colour
        self.value = PIECE_INFO[name]['value']
        self.last_move = last_move

        self.loc = 0

        self.direction = COLOUR_INFO.index(colour)

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
        self.checks = []

    def r_diff(self):
        return self.r_end - self.r_start

    def f_diff(self):
        return self.f_end - self.f_start

    def pgn_create(self, piece_start, piece_end, check):
        
        start_string = PIECE_INFO[piece_start.name]['symbol'] + self.start

        if piece_end is None:
            middle = '-'
            end_string = self.end
        else:
            middle = 'x'
            end_string = PIECE_INFO[piece_end.name]['symbol'] + self.end

        if check:
            check_string = '+'
        else:
            check_string = ''
        
        self.pgn = start_string + middle + end_string + check_string
        print(self.pgn)

class Display(tk.Tk):

    #Initialises board and dimensions
    def __init__(self, board = Board()):
        super().__init__()
        self.board_height = 500
        self.board_width = 500

        self.board = board

        #stores square height/width
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
                text = PIECE_INFO[piece.name]['unicode'], 
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

