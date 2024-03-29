import numpy as np
import matplotlib.pyplot as plt
import string
import tkinter as tk
import time
import pyperclip
import random

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
                prom_rf = 8):
        self.nrows = nrows
        self.ncols = ncols
        self.corner = corner
        self.rules = rules
        self.prom_rf = prom_rf
        
        self.colours = [colour for colour in COLOUR_INFO]
        self.to_play = COLOUR_INFO[0]
        self.half_moves = [0, 4]
        self.total_moves = 0

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
        self.resign_list = []

        self.game_over = False

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
    def move(self, move_start, move_end, resign = False, dummy = False):

        piece_start = self.square_find(move_start).piece

        if piece_start is None:
            return print('No piece in start square')
        
        if self.square_find(move_end).blocked:
            print(move_start, move_end, dummy)
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
            k_castle = self.king_castle[colour] 
            q_castle = self.queen_castle[colour]
        else:
            colour = None
            move_number = 0
            k_castle, q_castle = 0, 0

        #Creates Move object for testing that will be applied if success 
        attempt_move = Move(move_number, colour, move_start, move_end, k_castle,
                q_castle)
        attempt_move.total_number = len(self.move_list)+1

        enpassant_piece = None
        #If rules turned on, checks if legal move has been made
        if self.rules:
            move_check = attempt_move.legal_check(piece_start, self.squares, dummy)
            if attempt_move.castling:
                checked_castle = self.castle_checking(piece_start, attempt_move)
                if not checked_castle:
                    move_check = False
            elif attempt_move.enpassant_cap:
                enpassant_piece =self.square_find(attempt_move.enpassant_cap).piece
                move_num_diff = (attempt_move.total_number - 
                        enpassant_piece.last_move.total_number)
                if move_num_diff > len(self.colours):
                    move_check = False
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

        self.board_move(attempt_move)

        #If rules on all kings are checked for whether in check
        if self.rules:
            king_checks = self.all_check_test()
        else:
            king_checks = {}

        #If dummy then want to return if king is checked
        if dummy:
            self.board_move_undo(attempt_move, old_piece, enpassant_piece)
            return king_checks

        #Either invalid move or does mate check based on king_col being checked
        new_mates = []
        for king_col, king_check_list in king_checks.items():
            if king_col == colour:
                self.board_move_undo(attempt_move, old_piece, enpassant_piece)
                print('King in check')
                return False
            else:
                mate_test = self.test_mate(king_check_list, king_col)
                if mate_test:
                    print('{} is checkmated!'.format(king_col))
                    new_mates.append(king_col)
                    self.mate_apply(king_col)

        if old_piece != None:
            attempt_move.old_piece = old_piece
            if old_piece.name == 'King' and not old_piece.dead:
                king_col = old_piece.colour
                print('{} is checkmated!'.format(king_col))
                new_mates.append(king_col)
                self.mate_apply(king_col)

        #Confirm whether move caused a new check
        if king_checks:
            attempt_move.checks = king_checks
            prev_move_checks = self.move_list[-1].checks
            new_checks = self.new_check_test(king_checks, prev_move_checks)
        else:
            new_checks = 0

        new_stale = self.stalemate_test()

        #If reaches here then move is allowed to occur and is recorded
        self.move_updates(attempt_move, piece_start, old_piece, end_square, 
                new_checks, new_mates, new_stale, colour, enpassant_piece, resign)

        return True

    def game_over_check(self):
        return len(self.colours) - len(self.resign_list) == 1

    def move_updates(self, attempt_move, piece_start, old_piece, end_square, 
            new_checks, new_mates, new_stale, clr, enpassant_piece, resign):
        
        self.total_moves = self.total_moves + 1
        
        self.half_move_update(attempt_move, piece_start, old_piece)
        
        game_over = False
        if self.game_over_check() or attempt_move.draw:
            game_over = True
            attempt_move.game_over = True
            self.game_over = True
            for col__ in self.resign_list:
                attempt_move.extra_resign.append(col__)

        end_square.piece.last_move = attempt_move
        self.move_list.append(attempt_move)
        
        if piece_start.promoted == 'Temp':
            piece_start.promoted = True
            attempt_move.promoting = True

        attempt_move.resign = resign
        attempt_move.mating = new_mates
        attempt_move.stale = new_stale
        attempt_move.pgn_create(piece_start, old_piece, new_checks)
        attempt_move.half_move = self.half_moves
        attempt_move.new_checks = new_checks
        col_idx = (self.colours.index(clr) + 1)% (len(self.colours))
        self.to_play = self.colours[col_idx]

        if piece_start.name == 'King':
            self.king_castle[clr] = 0
            self.queen_castle[clr] = 0

        elif piece_start.name == 'Rook':
            rook_type = piece_start.rook_type(self.king_loc[clr])
            if rook_type == 'King':
                self.king_castle[clr] = 0
            elif rook_type == 'Queen':
                self.queen_castle[clr] = 0
        
        if old_piece and not old_piece.dead:
            if old_piece.name == 'Rook':
                rook_type = old_piece.rook_type(self.king_loc[old_piece.colour],
                        attempt_move.start)
                if rook_type == 'King':
                    self.king_castle[old_piece.colour] = 0
                elif rook_type == 'Queen':
                    self.queen_castle[old_piece.colour] = 0

        self.score_update(new_checks, new_mates, new_stale, piece_start, 
                old_piece, enpassant_piece, clr, attempt_move.draw, game_over,
                self.resign_list)

    def score_update(self, new_checks, new_mates, new_stale, piece_start,
            old_piece, enpassant_piece, clr, draw, game_over, extra_resign,
            forward = True):
       
        bonus_score = 0
        if new_checks == 2:
            if piece_start.name == 'Queen':
                bonus_score = 1
            else:
                bonus_score = 5
        elif new_checks == 3:
            if piece_start.name == 'Queen':
                bonus_score = 5
            else:
                bonus_score = 20
        elif new_checks > 3:
            print('ERROR - MORE THAN 3 CHECKS DETECTED')

        bonus_score = bonus_score + 20*len(new_mates)

        for col in new_mates:
            if col in self.resign_list:
                self.resign_list.remove(col)

        for col in new_stale:
            if col in self.resign_list:
                self.resign_list.remove(col)
                for colour in self.colours:
                    bonus_score = bonus_score + 10
            else:
                bonus_score = bonus_score + 20

        cap_value = 0
       
        if old_piece:
            if ((old_piece.colour in new_mates or not old_piece.dead)
            and not old_piece.resigned and not piece_start.resigned 
            and old_piece.colour != clr and old_piece.name != 'King'):
                cap_value = old_piece.value

        if enpassant_piece:
            cap_value = cap_value + 1
            if forward:
                self.capture_list[clr].append(enpassant_piece)

        extra_score = bonus_score + cap_value
        if forward:
            self.scores[clr] = self.scores[clr] + extra_score
            if draw:
                for clr_ in self.colours:
                    self.scores[clr_] = self.scores[clr_] + 10
            elif game_over:
                last_clr = next(iter(set(self.colours) - set(self.resign_list)))
                self.scores[last_clr] += len(extra_resign)*20
        else:
            self.scores[clr] = self.scores[clr] - extra_score
            if draw:
                for clr_ in self.colours:
                    self.scores[clr_] = self.scores[clr_] - 10
            elif game_over:
                for clr_ in self.colours:
                    if clr_ not in extra_resign:
                        self.scores[clr_] -= len(extra_resign)*20

    def half_move_update(self, attempt_move, piece_start, old_piece):
        if old_piece or piece_start.name == 'Pawn' or attempt_move.promoting:
            self.half_moves[0] = 0
        elif self.half_moves[1] != len(self.colours):
            self.half_moves[0] = 0
            self.half_moves[1] = len(self.colours)
        else:
            self.half_moves[0] = self.half_moves[0] + 1
        if self.half_moves[0]/self.half_moves[1] > 50:
            attempt_move.draw = True    

    def promote_check(self, piece, square_code):
        #in board move, want true if pawn with prom_rf = piece_rf, 
        #in undo want true if piece.promoted = temp
        #in drop want true if newly promoted queen <- get around it 
        #check end square and put 1 over queen to indicate 1 point
        if piece.promoted == 'Temp':
            return True
        if piece.name != 'Pawn':
            return False
    
        file_, rank = move_to_rank_file(square_code)
        theta = np.radians(90*piece.direction)
        c, s = round(np.cos(theta)), round(np.sin(theta))

        if c > 0.5:
            prom_rf = self.prom_rf*c
            piece_rf = rank
        elif c < -0.5:
            prom_rf = self.nrows + self.prom_rf*c + 1
            piece_rf = rank
        elif s > 0.5:
            prom_rf = self.prom_rf*s
            piece_rf = file_
        elif s < -0.5:
            prom_rf = self.ncols + self.prom_rf*s + 1
            piece_rf = file_

        if prom_rf == piece_rf:
            return True
        else:
            return False

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

    def castle_checking(self, piece, attempt_move):
        
        direct = piece.direction
        theta = np.radians(90*direct)
        c, s = round(np.cos(theta)), round(np.sin(theta))
        r_step, f_step = s, c
        
        k_file, k_rank = move_to_rank_file(attempt_move.start)
        i = 0

        while i < 2:
            k_file_test, k_rank_test = k_file+i*f_step, k_rank+i*r_step
            king_pos_test = rank_file_to_move(k_file_test, k_rank_test)
            checks = self.check_test(attempt_move.colour, king_pos_test)
            if len(checks) > 0:
                return False
            i = i + 1
        return True
       
    def castle_move(self, king_piece, attempt_move):
        rook_start, rook_end = king_piece.rook_square(attempt_move.castling)
        start_square = self.square_find(rook_start)
        end_square = self.square_find(rook_end)
        rook_piece = self.square_find(start_square.name).piece
        attempt_move.castle_rook = [start_square, end_square, rook_piece]

        end_square.add_piece(rook_piece)
        start_square.remove_piece()
        rook_piece.last_move = attempt_move

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
            if colour == king_col or piece.dead:
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
            
            if self.square_find(move_end).obstruct() == True:
                continue

            checked_checks = self.move(move_start, move_end, dummy = True) 
            if checked_checks == False:
                continue
            if not king_col in checked_checks:
                return False

        #If double check (and king can't move) then king is mated
        if len(king_checks) > 1:
            return True
       
        #If resigned then only king remains so can't capture/obstruct
        if self.square_find(self.king_loc[king_col]).piece.resigned:
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
        #mate in that case or if king is resigned so no pieces to obstruct
   
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

    def mate_apply(self, king_col):
        self.colours.remove(king_col)
        del self.king_loc[king_col]
        for piece in self.piece_pos[king_col]:
            piece.dead = True

    def mate_undo(self, king_col):

        king_idx = COLOUR_INFO.index(king_col)
        col_before = self.colours[:king_idx]
        max_idx = len(self.colours) - 1

        stop = False
        i = 0

        while stop == False:
            if self.colours[i] not in col_before:
                self.colours.insert(i, king_col)
                stop = True
            elif i == max_idx:
                self.colours.append(king_col)
                stop = True
            i = i + 1
        
        for piece in self.piece_pos[king_col]:
            if piece.name == 'King':
                king_piece = piece
                king_piece.dead = False
        if not king_piece.resigned:
            for piece in self.piece_pos[king_col]:
                piece.dead = False
        self.king_loc[king_col] = king_piece.loc

    def resign_apply(self, move = True):
        king_col = self.to_play
        self.resign_list.append(king_col)
        for piece in self.piece_pos[king_col]:
            piece.dead = True
            piece.resigned = True
            if piece.name == 'King':
                piece.dead = False
                king_loc = piece.loc

        if move:
            self.king_random_move(king_loc, resign = True)

    def resign_undo(self, king_col):
        self.resign_list.remove(king_col)
        for piece in self.piece_pos[king_col]:
            piece.dead = False
            piece.resigned = False

    def king_random_move(self, king_loc, resign = False):
        file_, rank = move_to_rank_file(king_loc)
        
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
            if self.squares[r_index][f_index].obstruct() == True:
                continue
            moves.append(move_end)

        stop = False
        while not stop:
            king_att_end = random.choice(moves)
            move_check = self.move(king_loc, king_att_end, dummy = True)
            if move_check == False:
                moves.remove(king_att_end)
            elif self.to_play in move_check:
                moves.remove(king_att_end)
            else:
                self.move(king_loc, king_att_end, resign)
                stop = True

    def stalemate_test(self):
        #Knight_extent -> all knight moves
        #Hori_verti_diag_extent -> all rook/bishop/queen moves
        #King_extent -> trivial 
        #Need to write something for pawns extent
        
        stale_col = []
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
                        if self.squares[r_index][f_index].obstruct() == True:
                            continue
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
                    if move_test == False:
                        continue
                    if not colour in move_test:
                        stop = True
            
            if not stop:
                print('{} is stalemated'.format(colour))
                self.mate_apply()
                stale_col.append(colour)
        return stale_col

    #Add piece to a square and updates data on king locations
    def piece_add(self, square, piece):
        square.add_piece(piece)
        if piece.name == 'King':
            self.king_loc[piece.colour] = piece.loc

    def board_move(self, attempt_move):
        start_square = self.square_find(attempt_move.start)
        end_square = self.square_find(attempt_move.end)

        promotion = self.promote_check(start_square.piece, end_square.name)

        if promotion:
           start_square.piece.promoted = 'Temp'
           start_square.piece.name = 'Queen'

        if end_square.piece != None:
            end_square.piece.loc = None
            if not end_square.piece.dead and not start_square.piece.resigned:
                self.capture_list[self.to_play].append(end_square.piece)
        end_square.add_piece(start_square.piece)
        start_square.remove_piece()
    
        if end_square.piece != None:
            if end_square.piece.name == 'King':
                self.king_loc[end_square.piece.colour] = end_square.piece.loc
        
        if attempt_move.castling:
            self.castle_move(end_square.piece, attempt_move)

        if attempt_move.enpassant_cap:
            square_remove = self.square_find(attempt_move.enpassant_cap)
            square_remove.piece.loc = None
            square_remove.remove_piece()

    def board_move_undo(self, attempt_move, old_piece, enpassant_piece):
        start_square = self.square_find(attempt_move.start)
        end_square = self.square_find(attempt_move.end)

        promotion = self.promote_check(end_square.piece, end_square.name)

        if promotion:
            end_square.piece.promoted = False
            end_square.piece.name = 'Pawn'

        start_square.add_piece(end_square.piece)
        if old_piece != None:
            end_square.add_piece(old_piece)
            if not old_piece.dead and not start_square.piece.resigned:
                del self.capture_list[self.to_play][-1]
        else:
            end_square.remove_piece() 

        if start_square.piece.name == 'King':
            self.king_loc[start_square.piece.colour] = start_square.piece.loc

        if attempt_move.enpassant_cap:
            old_square = self.square_find(attempt_move.enpassant_cap)
            self.piece_add(old_square, enpassant_piece)
            enpassant_piece.loc = old_square.name

    def square_find(self, square_code):
            file_, rank = move_to_rank_file(square_code)
            return self.squares[rank-1][file_-1]

    def board_pos_fen(self):
        fen_string = ''
        for i in range(self.nrows):
            row_info = []
            empty_count = 0
            for j in range(self.ncols):
                piece = self.squares[self.nrows-1-i][j].piece
                if piece is None:
                    empty_count = empty_count + 1
                else:
                    if empty_count > 0:
                        row_info.append(str(empty_count))
                        empty_count = 0
                    row_info.append(piece.fen)
            if empty_count > 0:
                row_info.append(str(empty_count))
            fen_string = fen_string + ','.join(str(x) for x in row_info) + '/\n'
        fen_string = fen_string[:-2]
        
        return fen_string

    def fen_to_board(self, fen):
        fen_list = fen.split('-')

        letter_to_clr = {'R': 'Red', 'B': 'Blue', 'Y': 'Yellow', 'G': 'Green'}

        self.to_play = letter_to_clr[fen_list[0]]
        in_game = [int(x) for x in fen_list[1].split(',')] 
        king_castle = [int(x) for x in fen_list[2].split(',')]
        queen_castle = [int(x) for x in fen_list[3].split(',')]
        scores = [int(x) for x in fen_list[4].split(',')]

        for idx, clr in enumerate(COLOUR_INFO):
            if in_game[idx] == 1:
                self.colours.append(clr)
            self.king_castle[clr] = king_castle[idx]
            self.queen_castle[clr] = queen_castle[idx]
            self.scores[clr] = scores[idx]

        self.half_moves = [int(fen_list[5]), len(self.colours)]
        self.piece_fen_init(fen_list[6])

    def board_to_fen(self):
        in_game = []
        king_castle = []
        queen_castle = []
        scores = []
        
        clr_to_letter = {'Red': 'R', 'Blue': 'B', 'Yellow': 'Y', 'Green': 'G'}

        for idx, clr in enumerate(COLOUR_INFO):
            if self.colours[idx] in COLOUR_INFO:
                in_game.append(1)
            else:
                in_game.append(0)
            king_castle.append(self.king_castle[clr])
            queen_castle.append(self.queen_castle[clr])
            scores.append(self.scores[clr])

        fen_list = (clr_to_letter[self.to_play] + '-' + ','.join(in_game) + '-' +
                ','.join(king_castle) + '-' + ','.join(queen_castle) + '-' + 
                ','.join(scores) + '-' + ','.join(half_moves) + '-\n')
        
        for i in range(self.nrows):
            row_list = []
            counter = 0
            for j in range(self.ncols):
                piece = self.squares[i][j].piece
                if not piece:
                    counter = counter + 1
                else:
                    row_list.append(counter)
                    counter = 0
                    text = clr_to_letter[piece.colour] + piece.name[0]
                    row_list.append(text)
            if counter > 0:
                row_list.append(counter)
            fen_list + ','.join(row_list) + '/\n'
        fen_list = fen_list[:-3]

        return fen_list

    def temp_move_apply(self, move, direction):

        if direction == 1:
            start_square = self.square_find(move.start)
            end_square = self.square_find(move.end)
            self.total_moves = self.total_moves + 1

        elif direction == -1:
            start_square = self.square_find(move.end)
            end_square = self.square_find(move.start)
            self.total_moves = self.total_moves - 1

        piece_start = start_square.piece
        piece_end = end_square.piece
        old_piece = move.old_piece
        enpassant_piece = False
        colour = move.colour

        if move.promoting:
            if direction == 1:
                piece_start.promoted = True
                piece_start.name = 'Queen'
            elif direction == -1:
                piece_start.promoted = False
                piece_start.name = 'Pawn'

        if piece_end != None:
            piece_end.loc = None
            if not piece_end.dead and piece_end.colour != colour:
                self.capture_list[self.to_play].append(piece_end)
        end_square.add_piece(piece_start)
        start_square.remove_piece()

        if piece_start.name == 'King':
            self.king_loc[piece_start.colour] = piece_start.loc
        
        if move.castling:
            if direction == 1:
                self.castle_move(end_square.piece, move)
            elif direction == -1:
                rook_start = move.castle_rook[0]
                rook_end = move.castle_rook[1]
                rook_piece = move.castle_rook[-1]
                rook_start.add_piece(rook_piece)
                rook_end.remove_piece()

        if move.enpassant_cap:
            square_enp = self.square_find(move.enpassant_cap)
            if direction == 1:
                enpassant_piece = square_enp.piece
                square_enp.piece.loc = None
                square_enp.remove_piece()

            elif direction == -1:
                enpassant_piece = self.capture_list[colour].pop()
                square_enp.add_piece(enpassant_piece)
        
        if old_piece and not old_piece.dead and direction == 1:
            if old_piece.name == 'Rook':
                rook_type = old_piece.rook_type(self.king_loc[old_piece.colour],
                        move.start)
                if rook_type == 'King':
                    self.king_castle[old_piece.colour] = 0
                elif rook_type == 'Queen':
                    self.queen_castle[old_piece.colour] = 0
        
        elif old_piece and direction == -1:
            start_square.add_piece(old_piece)
            if ((old_piece.colour in move.mating or not old_piece.dead)
            and not old_piece.resigned and not piece_start.resigned 
            and old_piece.colour != colour and old_piece.name != 'King'):
                self.capture_list[colour].pop()

        for clr in move.mating:
            if direction == 1:
                self.mate_apply(clr)
            elif direction == -1:
                self.mate_undo(clr)

        if move.resign:
            if direction == 1:
                self.resign_apply(move = False)
            elif direction == -1:
                self.resign_undo(colour)
        end_square.piece.last_move = move
       
        if direction == 1:
            col_idx = (self.colours.index(colour) + 1)% (len(self.colours))
        elif direction == -1:
            col_idx = (self.colours.index(colour)) % (len(self.colours))
        
        self.to_play = self.colours[col_idx]

        if piece_start.name == 'King':
            if direction == 1:
                self.king_castle[colour] = 0
                self.queen_castle[colour] = 0

        elif piece_start.name == 'Rook':
            rook_type = piece_start.rook_type(self.king_loc[colour])
            if rook_type == 'King':
                self.king_castle[colour] = 0
            elif rook_type == 'Queen':
                self.queen_castle[colour] = 0
      
        new_checks = move.new_checks

        if direction == 1:
            frwd = True
        else:
            frwd = False
        
        game_over = move.game_over
        if game_over:
            if direction == 1:
                self.game_over = True
            elif direction == -1:
                self.game_over = False
                for col__ in move.extra_resign:
                    self.resign_list.append(col__)
        
        self.score_update(new_checks, move.mating, move.stale, piece_start, 
                old_piece, enpassant_piece, colour, move.draw, game_over,
                extra_resign = move.extra_resign, forward = frwd)

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
        self.promoted = False
        self.dead = False
        self.resigned = False

        self.fen = self.fen_code()

    def fen_code(self):
        fen = self.colour[0].lower() + PIECE_INFO[self.name]['FEN']
        return fen
   
    def rook_type(self, king_loc, rook_loc = False):
        if not rook_loc:
            rook_loc = self.loc
        theta = np.radians(90*self.direction)
        c, s = round(np.cos(theta)), round(np.sin(theta))
        k_file, k_rank = move_to_rank_file(king_loc)
        R_file, R_rank = move_to_rank_file(rook_loc)
        r_diff = k_rank - R_rank
        f_diff = k_file - R_file

        if s == 0:
            f_diff = k_file - R_file
            type_test = f_diff*c
        elif c == 0:
            r_diff = k_rank - R_rank
            type_test = r_diff*s

        if type_test > 0:
            r_type = 'Queen'
        elif type_test < 0:
            r_type = 'King'
        else:
            r_type = False
        return r_type

    def rook_square(self, rook_type):
        k_file, k_rank = move_to_rank_file(self.loc)

        theta = np.radians(90*self.direction)
        c, s = round(np.cos(theta)), round(np.sin(theta))
        diff_arr = np.array([c, s]) 
        if s == 0:
            r_step = 0
            f_step = c
        elif c == 0:
            r_step = s
            f_step = 0
        if rook_type == 'King':
            r_file_start, r_file_end = k_file + f_step*1, k_file + f_step*-1
            r_rank_start, r_rank_end = k_rank + r_step*1, k_rank + r_step*-1
        elif rook_type == 'Queen':
            r_file_start, r_file_end = k_file + f_step*-2, k_file + f_step*1
            r_rank_start, r_rank_end = k_rank + r_step*-2, k_rank + r_step*1
        r_start_square = rank_file_to_move(int(r_file_start), int(r_rank_start))
        r_end_square = rank_file_to_move(int(r_file_end), int(r_rank_end))
        return r_start_square, r_end_square

    def king_castle_square(self, castle_type):
        k_file_start, k_rank_start = move_to_rank_file(self.loc)
        
        theta = np.radians(90*self.direction)
        c, s = round(np.cos(theta)), round(np.sin(theta))
        diff_arr = np.array([c, s]) 
        if s == 0:
            r_step = 0
            f_step = c
        elif c == 0:
            r_step = s
            f_step = 0
        if castle_type == 'King':
            k_file_end = k_file_start + f_step*2 
            k_rank_end = k_rank_start + r_step*2
        elif castle_type == 'Queen':
            k_file_end = k_file_start + f_step*-2
            k_rank_end = k_rank_start + f_step*-2
        k_end_square = rank_file_to_move(int(k_file_end), int(k_rank_end))
        return k_end_square

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
    def __init__(self, number, colour, start, end, k_castle = 0, q_castle = 0):
        self.number = number
        self.total_number = 0
        self.half_moves = [0, 0]
        self.colour = colour
        self.start = start
        self.f_start, self.r_start = move_to_rank_file(self.start)
        self.end = end
        self.f_end, self.r_end = move_to_rank_file(self.end)
        self.checks = {}
        self.new_checks = 0
        self.k_castle = k_castle
        self.q_castle = q_castle

        self.old_piece = None
        self.castle_rook = None
        self.display = None

        self.castle_change = False
        self.double_push = False
        self.castling = False
        self.promoting = False
        self.enpassant_cap = False
        self.resign = False
        self.draw = False
        self.game_over = False
        self.extra_resign = []
        self.mating = []
        self.stale = []

    def r_diff(self):
        return self.r_end - self.r_start

    def f_diff(self):
        return self.f_end - self.f_start

    def pgn_create(self, piece_start, piece_end, checks):

        if self.castling == 'King':
            self.pgn = 'O-O'
            self.display = 'O-O'
            return
        elif self.castling == 'Queen':
            self.pgn = 'O-O-O'
            self.display = 'O-O-O'
            return

        start_string = PIECE_INFO[piece_start.name]['symbol'] + self.start

        if piece_end is None:
            middle = '-'
            end_string = self.end
        else:
            middle = 'x'
            end_string = PIECE_INFO[piece_end.name]['symbol'] + self.end
        if self.enpassant_cap:
            middle = 'x'

        if self.promoting:
            start_string = self.start
            end_string = end_string + '=D'

        check_string = '+'*checks+'#'*len(self.mating)

        if self.resign:
            check_string = check_string + 'R'

        self.pgn = start_string + middle + end_string + check_string

        self.display = (PIECE_INFO[piece_start.name]['symbol'] + self.end +
                        check_string)
        if self.promoting:   
            self.display = self.end + '=D'
    
    #Check if legal move is being made, dummy is true if move is not 
    #suggested but just a check for legality of a board position
    def legal_check(self, piece, squares, dummy = False):
        #Checks if end square is blocked by piece of same colour
        try:
            piece_end = square_find(self.end, squares).piece
            if piece.colour == piece_end.colour and not piece_end.dead:
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
            return self.king_test(squares, piece)

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

    def king_test(self, squares, piece):
        #King can move 1 space in any direction - whether king is in check
        #is checked later on
        if abs(self.f_diff()) <= 1 and abs(self.r_diff()) <= 1:
            return True
        castling = self.castle_check(squares, piece)
        if castling:
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

        if direct % 2 == 0:
            diff_diag_L = np.array([c-s, s-c])
            diff_diag_R = np.array([c+s, s+c])
        elif direct % 2 == 1:
            diff_diag_R = np.array([c-s, s-c])
            diff_diag_L = np.array([c+s, s+c])

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
        L_diag_check = np.array_equal(rf_diff, diff_diag_L)
        R_diag_check = np.array_equal(rf_diff, diff_diag_R)

        #If no piece present then check if can move 1 or 2 squares
        if piece_check == None:
            if m1_check:
                return True
            #2 moves forward only allowed if pawn has not moved
            elif m2_check and moved_check == False:
                self.double_push = True
                return True
        #If piece present then check if diagonal capture is possible
        elif piece_check != None:
            if R_diag_check or L_diag_check:
                return True
        
        if R_diag_check or L_diag_check:
            enpassant = self.enpassant_check(diff_arr, diff_diag_L, diff_diag_R, 
                    rf_diff, piece, squares)
            if enpassant:
                return True
        return False

    def enpassant_check(self, diff_arr, diff_diag_L, diff_diag_R, rf_diff, 
            moving_piece, squares):
        p_file_start, p_rank_start = move_to_rank_file(self.start)
        obstr_file = p_file_start + diff_arr[1]
        obstr_rank = p_rank_start + diff_arr[0]
        obstr_sqre = rank_file_to_move(obstr_file, obstr_rank)
        obstr_piece = square_find(obstr_sqre, squares).piece
        if obstr_piece == None:
            return False
        elif obstr_piece.name != 'Pawn' or not obstr_piece.last_move:
            return False
        elif not obstr_piece.last_move.double_push:
            return False

        direct_diff = (obstr_piece.direction - moving_piece.direction) %len(
                COLOUR_INFO)
        if ((direct_diff == 1 and np.array_equal(diff_diag_L, rf_diff)) or 
                (direct_diff == 3 and np.array_equal(diff_diag_R, rf_diff))):
            self.enpassant_cap = obstr_piece.loc
            return True
        else:
            return False

    def castle_check(self, squares, piece):
        if self.k_castle == 0 and self.q_castle == 0:
            return False
        
        rf_diff = np.array([self.r_diff(), self.f_diff()])
        
        direct = piece.direction
        theta = np.radians(90*direct)
        c, s = round(np.cos(theta)), round(np.sin(theta))
        diff_arr = np.array([s,c])

        king_cast_arr, queen_cast_arr = diff_arr*2, diff_arr*-2

        king_cast_check = np.array_equal(rf_diff, king_cast_arr)
        queen_cast_check = np.array_equal(rf_diff, queen_cast_arr)
        
        if king_cast_check and self.k_castle == 1:
            self.castling = 'King'
            r_step, f_step = king_cast_arr[0]/2, king_cast_arr[1]/2
            square_dist = 3
        elif queen_cast_check and self.q_castle == 1:
            self.castling = 'Queen'
            r_step, f_step = queen_cast_arr[0]/2, queen_cast_arr[1]/2
            square_dist = 4
        else:
            if king_cast_check or queen_cast_check:
                print('King cannot castle on this side anymore')
            return False

        k_file, k_rank = move_to_rank_file(self.start)
        r_file = int(k_file+f_step*square_dist)
        r_rank = int(k_rank+r_step*square_dist)
        r_square = rank_file_to_move(r_file, r_rank)
        stop = False
        i = 1

        while i <= square_dist and stop == False:
            file_, rank = int(k_file + i*f_step), int(k_rank + i*r_step)
            square = rank_file_to_move(file_, rank)
            obstruction = square_find(square, squares).obstruct()
            if obstruction == True:
                return False
            elif obstruction == False:
                i = i+1
                continue
            else:
                if obstruction.loc == r_square:
                    return True
                stop = True
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
