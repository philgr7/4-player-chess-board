import numpy as np
import matplotlib.pyplot as plt
import string
import tkinter as tk
import time
import pyperclip

#Colours available in four player chess
COLOUR_INFO = ['Red', 'Blue', 'Yellow', 'Green']

#List of available pieces with point value and corresponding unicode 
PIECE_INFO = {
        'Pawn': {'value': 1, 'unicode': '\u265F', 'symbol': '', 'FEN': 'P'},
        'Knight': {'value': 3, 'unicode': '\u265E', 'symbol': 'N', 'FEN': 'N'},
        'Bishop': {'value': 5, 'unicode': '\u265D', 'symbol': 'B', 'FEN': 'B'},
        'Rook': {'value': 5, 'unicode': '\u265C', 'symbol': 'R', 'FEN': 'R'},
        'Queen': {'value': 9, 'unicode': '\u265B', 'symbol': 'Q', 'FEN': 'Q'},
        'King': {'value': 20, 'unicode': '\u265A', 'symbol': 'K', 'FEN': 'K'}
        }

alphabet = string.ascii_lowercase

#Creates class for chessboard
class Board:
    #Default board is set as 14 rows/columns and with RBYG colours
    def __init__(self, nrows = 14, ncols = 14, corner = 3, rules = True,
                prom_rank = 8):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.rules = rules
        self.prom_rank = prom_rank
        
        self.colours = [colour for colour in COLOUR_INFO]
        self.to_play = COLOUR_INFO[0]
        self.half_moves = 0

        #Stores move objects, king_piece objects, piece objects and square 
        #objects respectively
        self.king_loc = {}
        self.scores = {}
        self.king_castle = {}
        self.queen_castle = {}
        self.piece_pos = {}
        self.capture_list = {}
        
        self.squares = np.empty((self.nrows, self.ncols), dtype = 'object')
        self.move_list = []

        self.board_init()
        self.colour_init()
        self.piece_init()

    #Squares initialised to position on board
    def board_init(self):
        for i in range(self.nrows):
            for j in range(self.ncols):
                if ((i < self.corner or i >= self.nrows - self.corner) 
                    and (j < self.corner or j >= self.ncols - self.corner)):
                    self.squares[i][j] = Square(i+1, j+1, blocked = True)
                else:
                    self.squares[i][j] = Square(i+1, j+1)
    
    def colour_init(self):
        for colour in COLOUR_INFO:
            if colour not in self.piece_pos:
                self.piece_pos[colour] = []
                self.capture_list[colour] = []
                self.scores[colour] = 0
                self.king_castle[colour] = 1
                self.queen_castle[colour] = 1

        #Initialise data for all pieces on board - assumed default piece
        #config if not stated otherwise which is defined 
    def piece_init(self, pce_ord = ['Rook', 'Knight', 'Bishop',
        'King', 'Queen', 'Bishop', 'Knight', 'Rook']):
            #Loop initialises based on default piece locations
        for i in range(8):
            self.piece_add(self.squares[1][10-i], Piece('Pawn', 'Red'))
            self.piece_add(self.squares[10-i][1], Piece('Pawn', 'Blue'))
            self.piece_add(self.squares[12][3+i], Piece('Pawn', 'Yellow'))
            self.piece_add(self.squares[3+i][12], Piece('Pawn', 'Green'))

            self.piece_add(self.squares[0][10-i], Piece(pce_ord[i], 'Red'))
            self.piece_add(self.squares[10-i][0], Piece(pce_ord[i], 'Blue'))
            self.piece_add(self.squares[13][3+i], Piece(pce_ord[i], 'Yellow'))
            self.piece_add(self.squares[3+i][13], Piece(pce_ord[i], 'Green'))
        
        self.piece_pos_init()

    def piece_fen_init(self, fen_board):
        self.piece_pos = {}
        self.colour_init()
        if fen_board[:1] == '\n':
            fen_board = fen_board[1:]
        fen_rows = fen_board.split('/\n')
        fen_rows = fen_rows[::-1]

        fen_colour = {'r': 'Red', 'b': 'Blue', 'y': 'Yellow', 'g': 'Green'}
        piece_abr = {}

        for key, val in PIECE_INFO.items():
            piece_abr[val['FEN']] = key

        if len(fen_rows) != self.nrows:
            print("FEN format doesn't match board format")

        space_counter = 0
        for i in range(self.nrows):
            row_list = fen_rows[i].split(',')
            for j in range(self.ncols):
                if space_counter > 0:
                    space_counter = space_counter - 1
                    continue
                else:
                    next_square = row_list.pop(0)
                    try:
                        next_square = int(next_square)
                    except ValueError:
                        pass
                if isinstance(next_square, int):
                    space_counter = next_square - 1
                    continue
                piece_colour = fen_colour[next_square[0]]
                piece_name = piece_abr[next_square[1]]
                self.piece_add(self.squares[i][j], Piece(piece_name, piece_colour))
                
        self.piece_pos_init(start_square_info = False)

    def piece_pos_init(self, start_square_info = True):
        for square in self.squares.ravel():
            piece = square.piece
            if piece == None:
                continue
            elif square.piece == 'King':
                self.king_loc[piece.colour].append(piece.loc)
            
            self.piece_pos[piece.colour].append(piece)
            if not start_square_info:
                piece.start_square = None

    #After a move is requested if rules is turned on then a check is done
    #for legality and the move is applied and stored
    def move(self, move_start, move_end, dummy = False):
         
        piece_start = self.square_find(move_start).piece

        if piece_start is None:
            return print('No piece in start square')
        if self.square_find(move_end).blocked:
            print('End square is blocked')
            return False

        if not dummy:
            #Sets colour/move_number based on previous move
            colour = self.to_play
            if self.move_list == []:
                move_number = 1
            elif self.move_list[-1].colour == self.colours[-1]:
                move_number = self.move_list[-1].number + 1
            else:
                move_number = self.move_list[-1].number
        else:
            colour = None
            move_number = 0

        #Creates Move object for testing that will be applied if success 
        attempt_move = Move(move_number, colour, move_start, move_end)

        #If rules turned on, checks if legal move has been made
        if self.rules:
            move_check = attempt_move.legal_check(piece_start, self.squares, dummy)
        else:
            move_check = True
 
        if not move_check:
            if not dummy:
                print('Invalid move entered')
            return False

        #Carries out move and confirms existence of checks if successful 
        #then updates square objects, appending new move to list
        start_square = self.square_find(move_start)
        end_square = self.square_find(move_end)
        old_piece = end_square.piece

        self.board_move(start_square, end_square)
        
        #If rules on all kings are checked for whether in check
        if self.rules:
            king_checks = self.all_check_test()
        else:
            king_checks = {}

        #If dummy then want to return if king is checked
        if dummy:
            self.board_move_undo(start_square, end_square, old_piece)    
            return king_checks

        #Either invalid move or does mate check based on king_col being checked
        for king_col, king_check_list in king_checks.items():
            if king_col == colour:
                self.board_move_undo(start_square, end_square, old_piece)
                print('King in check')
                return False
            else:
                mate_test = self.test_mate(king_check_list, king_col)
                if mate_test:
                    print('Checkmate')
    
        #Confirm whether move caused a new check
        if king_checks:
            attempt_move.checks = king_checks
            prev_move_checks = self.move_list[-1].checks
            new_checks = self.new_check_test(king_checks, prev_move_checks)
        else:
            new_checks = 0

        self.stalemate_test()
        #If reaches here then move is allowed to occur and is recorded

        end_square.last_move = attempt_move
        self.move_list.append(attempt_move)
        attempt_move.pgn_create(piece_start, old_piece, new_checks)
        
        col_idx = (self.colours.index(colour) + 1)% (len(self.colours))
        self.to_play = self.colours[col_idx]
        return True

    #Confirms the status of all kings for checks
    def all_check_test(self):

        check_list = {}
        for key in self.king_loc:
            king_col = key
            king_loc = self.king_loc[key]
            piece_checks = self.check_test(king_col, king_loc)

            if piece_checks:
                check_list[king_col] = piece_checks

        return check_list

    def new_check_test(self, king_checks, prev_move_checks):
        new_checks = 0
        for king_col, checks_list in king_checks.items():
            if not king_col in prev_move_checks:
                new_checks = new_checks + 1
                continue
            
            sub_set = set(checks_list).issubset(set(prev_move_checks[king_col]))
            if not sub_set:
                new_checks = new_checks + 1
        return new_checks

    #Find pieces in hori/verti/diag line of sight of a king as well as 
    #knight moves on king and check if there is piece that checks the
    #king
    def check_test(self, king_col, king_loc):

        king_checks = []
        check_pieces = self.hori_verti_diag_extent(king_loc)
        print(king_col, king_loc)
        move_end = king_loc
        for idx, piece in enumerate(check_pieces):
            move_start = piece.loc
            colour = piece.colour
            if colour == king_col:
                continue
            attempt_move = Move(0, colour, move_start, move_end)
            check_test = attempt_move.legal_check(piece, self.squares,
                                        dummy = True)
            if check_test:
                king_checks.append(piece)

        knight_checks = self.knight_extent(king_loc)

        for knight in knight_checks:
            if knight.colour != king_col:
                king_checks.append(knight)

        return king_checks

    #Returns list of pieces in hori/verti/diag line of sight of king
    def hori_verti_diag_extent(self, move_code, extent_type = 'all',
                                include_gap = False):

        #list of piece in line of sight (los)
        los_list = []
       
        file_, rank = move_to_rank_file(move_code)

        #8 direction vectors for hori/verti/diag from king to loop over
        if extent_type == 'all':
            loop_directions = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
                            [0, 1], [1, -1], [1, 0], [1, 1]]
        elif extent_type == 'hori':
            loop_directions = [[-1, 0], [0, -1], [0, 1], [1, 0]]

        elif extent_type == 'diag':
            loop_directions = [[-1, -1], [-1, 1], [1, -1], [1, 1]]

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
                    continue

                if include_gap and los == False:
                    los_list.append(self.squares[r_index][f_index].name)

                #if obstruct = False or True then no piece obstruction found
                #booleans are counted as integers in isinstance
                if not isinstance(los, int):
                    stop = True
                    if include_gap:
                        los_list.append(los.loc)
                    else:
                        los_list.append(los)
                
        return los_list

    def knight_extent(self, move_code, start_square = False):
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
            if start_square:
                if not knight_check:
                    knight_list.append(self.squares[r_index][f_index].name)
            else:
                if not isinstance(knight_check, int):
                    if knight_check.name == 'Knight':
                        knight_list.append(knight_check)

        return knight_list

    def pawn_extent(self, move_code, direct):
        move_list = []

        theta = np.radians(90*direct)
        c, s = round(np.cos(theta)), round(np.sin(theta))

        #Arrays cover moving forward and capturing on either diagonal
        file_start, rank_start = move_to_rank_file(move_code)
        
        forward = np.array([c,s])
        diag_1 = np.array([c-s, s-c])
        diag_2 = np.array([c+s, s+c])
       
        move_differ = [forward, 2*forward, diag_1, diag_2]

        for move in move_differ:
            rank_end = rank_start + move[0]
            file_end = file_start + move[1]
            move_end = rank_file_to_move(file_end, rank_end)
            print(move_code, move_end)
            if self.square_find(move_end).obstruct() != True:
                move_list.append(move_end)

        return move_list

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

        for i in range(1, max_diff):
            r_index = r_start + i*r_step
            f_index = f_start + i*f_step

            square = self.squares[r_index][f_index]
            
            obstr_loc = square.name

            obstr_pieces = (self.hori_verti_diag_extent(obstr_loc) + 
                                self.knight_extent(obstr_loc))

            for piece in obstr_pieces:
                if piece.colour != king_col:
                    continue
                move_start = piece.loc
                checked_checks = self.move(move_start, obstr_loc, dummy = True)
                if checked_checks == False:
                    continue
                if not king_col in checked_checks:
                    return False

        return True

    def stalemate_test(self):
        #Knight_extent -> all knight moves
        #Hori_verti_diag_extent -> all rook/bishop/queen moves
        #King_extent -> trivial 
        #Need to write something for pawns extent
        
        for colour in self.colours:
            stop = False
            for piece in self.piece_pos[colour]:
                if piece.loc == None:
                    continue
                if stop:
                    continue

                pos = piece.loc

                if piece.name == 'Rook':
                    moves = self.hori_verti_diag_extent(pos, 
                            extent_type = 'hori', include_gap = True)
                    
                elif piece.name == 'Queen':
                    moves = self.hori_verti_diag_extent(pos,
                            extent_type = 'all', include_gap = True)

                elif piece.name == 'King':
                    file_, rank = move_to_rank_file(pos)
                    
                    move_direct = [[-1, -1], [-1, 0], [-1, 1], [0, -1],
                                    [0, 1], [1, -1], [1, 0], [1, 1]]

                    moves = []
                    for idx, val in enumerate(move_direct):
                        f_index = file_ - 1 + val[0]
                        r_index = rank - 1 + val[1]
                        
                        if (f_index < 0 or f_index > self.ncols - 1 or
                            r_index < 0 or r_index > self.nrows - 1):
                            continue
                        move_end = self.squares[r_index][f_index].name
                        moves.append(move_end)

                elif piece.name == 'Pawn':
                    moves = self.pawn_extent(pos, piece.direction)
                elif piece.name == 'Bishop':
                    moves = self.hori_verti_diag_extent(pos,
                            extent_type = 'diag', include_gap = True)

                elif piece.name == 'Knight':
                    moves = self.knight_extent(pos, start_square = True)

                for move_end in moves:
                    move_test = self.move(pos, move_end, dummy = True)
                    print(move_test, pos, move_end, piece.name)                    
                    if move_test == False:
                        continue
                    if not colour in move_test:
                        stop = True
            
            if not stop:
                print('{} is stalemated'.format(colour))
                
    #Add piece to a square and updates data on king locations
    def piece_add(self, square, piece):
        square.add_piece(piece)
        if piece.name == 'King':
            self.king_loc[piece.colour] = piece.loc

    def board_move(self, start_square, end_square):
        if end_square.piece != None:
            end_square.piece.loc = None
            self.capture_list[self.to_play].append(end_square.piece)
        end_square.add_piece(start_square.piece)
        start_square.remove_piece()

        if end_square.piece.name == 'King':
            self.king_loc[end_square.piece.colour] = end_square.piece.loc

    def board_move_undo(self, start_square, end_square, old_piece):
        start_square.add_piece(end_square.piece)
        if old_piece != None:
            end_square.add_piece(old_piece)
            del self.capture_list[self.to_play][-1]
        else:
            end_square.remove_piece()
        
        if start_square.piece.name == 'King':
            self.king_loc[start_square.piece.colour] = start_square.piece.loc

    def square_find(self, square_code):
            file_, rank = move_to_rank_file(square_code)
            return self.squares[rank-1][file_-1]

    def board_pos_fen(self):
        empty_count = 0
        fen_string = ''
        for i in range(self.nrows):
            row_info = []
            for j in range(self.ncols):
                piece = self.squares[i][self.ncols-1-j].piece
                if piece is None:
                    empty_count = empty_count + 1
                else:
                    if empty_count > 0:
                        row_info.append(str(empty_count))
                    row_info.append(piece.fen)
            if empty_count > 0:
                row_info.append(str(empty_count))
            fen_string = fen_string + ','.join(row_info) + '/\n'
        return fen_string

    def fen_to_board(self, fen):
        fen_list = fen.split('-')

        letter_to_clr = {'R': 'Red', 'B': 'Blue', 'Y': 'Yellow', 'G': 'Green'}

        self.to_play = letter_to_clr[fen_list[0]]
        in_game = [int(x) for x in fen_list[1].split(',')] 
        king_castle = [int(x) for x in fen_list[2].split(',')]
        queen_castle = [int(x) for x in fen_list[3].split(',')]
        scores = [int(x) for x in fen_list[4].split(',')]

        self.half_moves = int(fen_list[5])

        for idx, clr in enumerate(COLOUR_INFO):
            if in_game[idx] == 1:
                self.colours.append(clr)
            self.king_castle[clr] = king_castle[idx]
            self.queen_castle[clr] = queen_castle[idx]
            self.scores[clr] = scores[idx]

        self.piece_fen_init(fen_list[6])

#Creates class for a chess piece
class Piece:

    def __init__(self, name, colour, last_move = False):
        self.name = name
        self.colour = colour
        self.value = PIECE_INFO[name]['value']
        self.last_move = last_move

        self.start_square = None
        self.loc = None
        self.direction = COLOUR_INFO.index(colour)
    
    def fen_code(self):
        lower(colour[0])
        return lower(colour[0]) + PIECE_INFO[name]['FEN']
    
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
        self.checks = {}

    def r_diff(self):
        return self.r_end - self.r_start

    def f_diff(self):
        return self.f_end - self.f_start

    def pgn_create(self, piece_start, piece_end, checks):
        
        start_string = PIECE_INFO[piece_start.name]['symbol'] + self.start

        if piece_end is None:
            middle = '-'
            end_string = self.end
        else:
            middle = 'x'
            end_string = PIECE_INFO[piece_end.name]['symbol'] + self.end

        check_string = '+'*checks

        self.pgn = start_string + middle + end_string + check_string

        self.display = (PIECE_INFO[piece_start.name]['symbol'] + self.end +
                        check_string)
        print(self.pgn)
    
    #Check if legal move is being made, dummy is true if move is not 
    #suggested but just a check for legality of a board position
    def legal_check(self, piece, squares, dummy = False):
        #Checks if end square is blocked by piece of same colour
        try:
            if piece.colour == square_find(self.end, squares).piece.colour:
                return False
        except AttributeError:
            pass

        #If colour in start square not same as player who should be playing
        #doesn't matter if dummy move
        if self.colour != piece.colour and dummy == False:
            print('Invalid move - {} to move'.format(self.colour))
            return False

        #Tests check for obstructions and whether piece has capability
        #to move between designated squares

        #Rook move horizontally or vertically
        if piece.name == 'Rook':
            return any((self.hori_test(squares), self.verti_test(squares)))

        #Queen move horizontally, vertically or diagonally
        elif piece.name == 'Queen':
            return any((self.hori_test(squares), self.verti_test(squares),
                        self.diag_test(squares)))

        #Bishop move diagonally
        elif piece.name == 'Bishop':
            return self.diag_test(squares)

        #King can move 1 square in any direction (assuming not in check)
        elif piece.name == 'King':
            return self.king_test()

        elif piece.name == 'Knight':
            return self.knight_test(squares)

        elif piece.name == 'Pawn':
            return self.pawn_test(squares, piece)

    #Test movement along horizontal lines
    def hori_test(self, squares):
        #movement can only occur if file changes and rank stays the same
        if self.f_start == self.f_end or self.r_start != self.r_end:
            return False
            
        #Checks if obstacle present - if no obstacle (False) or obstacle
        #is at end square then the move is legal. obstacle = True if 
        #trying to pass through blocked squares
        obstacle = self.hori_obst(squares)

        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == self.end:
            return True
        else:
            return False

    #Test movement along vertical lines 
    def verti_test(self, squares):
        #movement can only occur if rank changes and file stays the same
        if self.r_start == self.r_end or self.f_start != self.f_end:
            return False

        #same obstacle logic as hori_test
        obstacle = self.verti_obst(squares)

        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == self.end:
            return True
        else:
            return False

    #Tests for movement along diagonal lines
    def diag_test(self, squares):

        #Either sum or difference of rank/file is constant along a diagonal

        sum_equal = (self.r_start + self.f_start) == (self.r_end + self.f_end)
        diff_equal = (self.r_start - self.f_start) == (self.r_end - self.f_end)

        if sum_equal == False and diff_equal == False:
            return False

        #Same obstacle logic as hori_test
        obstacle = self.diag_obst(squares)
        
        if obstacle == False:
            return True
        elif obstacle == True:
            return False
        elif obstacle.loc == self.end:
            return True
        else:
            return False

    #checks for first obstacle for a given horizontal move
    def hori_obst(self, squares):

        #step sets if needs to loop positively or negatively through squares
        if self.f_start < self.f_end:
            step = 1
        else:
            step = -1

        #Don't want to check obstacles in starting square so need to add step
        #from before loop starts
        range_start = self.f_start - 1 + step
        range_end = self.f_end - 1 + step

        #Loops between two board locations and stops if obstacle is found
        for i in range(range_start, range_end, step):
            obstruction = squares[self.r_start-1][i].obstruct()
            if obstruction != False:
                return obstruction
        return False

    #checks for first obstacle in given vertical move - logic same as 
    #hori_obst
    def verti_obst(self, squares):
        if self.r_start < self.r_end:
            step = 1
        else:
            step = -1
        
        range_start = self.r_start - 1 + step
        range_end = self.r_end - 1 + step

        for i in range(range_start, range_end, step):
            obstruction = squares[i][self.f_start-1].obstruct()
            if obstruction != False:
                return obstruction
        return False

    #Checks for first obstacle in given diagonal move
    def diag_obst(self, squares):
        #step for both rank/file based on which direction move is occuring in
        if self.r_start < self.r_end:
            step_r = 1
        else:
            step_r = -1
        if self.f_start < self.f_end:
            step_f = 1
        else:
            step_f = -1

        ind_r = self.r_start - 1 + step_r
        ind_f = self.f_start - 1 + step_f

        #Use difference to loop between board positions unless obstacle found
        diff = abs(self.r_diff())

        for i in range(0, diff):
            obstruct_ = squares[ind_r+i*step_r][ind_f+i*step_f].obstruct()
            if obstruct_ != False:
                return obstruct_
        return False
        
    def knight_test(self, squares):

        #If rank/file change by 1/2 in any order than move is legal
        min_diff = min(abs(self.f_diff()), abs(self.r_diff()))
        max_diff = max(abs(self.f_diff()), abs(self.r_diff()))
        if max_diff == 2 and min_diff == 1:
            return True
        else:
            return False

    def king_test(self):
        #King can move 1 space in any direction - whether king is in check
        #is checked later on
        if abs(self.f_diff()) <= 1 and abs(self.r_diff()) <= 1:
            return True
        else: 
            return False

    def pawn_test(self, squares, piece):
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
        piece_check = square_find(self.end, squares).piece
        moved_check = piece.last_move

        #The change in rank/file of the attempted move 
        rf_diff = [self.r_diff(), self.f_diff()]
        
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

def move_to_rank_file(move_name):
    file_letter = move_name[0]
    file_number = int(alphabet.find(file_letter))+1
    rank_number = int(move_name[1:])
    return file_number, rank_number

def rank_file_to_move(file_, rank):
    move_code = alphabet[file_-1] + '{}'.format(rank)
    return move_code

#Finds square object based on board co-ords
def square_find(square_code, squares):
    file_, rank = move_to_rank_file(square_code)
    return squares[rank-1][file_-1]
