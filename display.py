import numpy as np
import string
import tkinter as tk
import time
import pyperclip
from chess import Board

COLOUR_INFO = ['Red', 'Blue', 'Yellow', 'Green']

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

class Display(tk.Tk):

    #Initialises board and dimensions
    def __init__(self, board = Board()):
        super().__init__()

        self.board = board
        
        self.board_width = 500
        self.board_height = 500

        #stores square height/width
        self.s_width = self.board_width/self.board.ncols
        self.s_height = self.board_height/self.board.nrows

        self.game_over = False
        self.board_review = False

        self.saving_moves = None

        self.move_obj = []
        self.move_number = 0
        self.state_idx = -1

        self.display_init()
        self.board_init()
        self.piece_init()

    def display_init(self):
        self.frame = tk.Frame(self)

        self.frame.pack()

        self.board_canvas = tk.Canvas(self.frame, height = self.board_height,
                        width = self.board_width, highlightthickness = 0)
        self.board_canvas.grid(column = 2, row = 1)
        
        self.colour_init()
        self.tools_init()
        self.rank_file_labels()
        self.to_move_init()

    def colour_init(self):
        self.score_displays = {}
        self.clr_1 = self.clr_dis(self.frame, COLOUR_INFO[0], 
                90, self.board_width, 2, 3)
        self.clr_2 = self.clr_dis(self.frame, COLOUR_INFO[1], 
                self.board_height, 90, 0, 1)
        self.clr_3 = self.clr_dis(self.frame, COLOUR_INFO[2], 
                90, self.board_width, 2, 0)
        self.clr_4 = self.clr_dis(self.frame, COLOUR_INFO[3], 
                self.board_height, 90, 3, 1)
        self.cap_update_all()
        
    def to_move_init(self):
        self.to_move_canvas = tk.Canvas(self.frame, background = 'white',
            width = 300, height = 90, highlightthickness = 0)
        self.to_move_canvas.grid(row = 3, column = 4)
        self.to_move_label = tk.Label(self.to_move_canvas, text =
            '{} to play'.format(self.board.to_play), fg = self.board.to_play,
            font = (None, 35), bg = 'white')
        self.to_move_label.pack(side = 'left')
        self.resign_but = tk.Button(self.to_move_canvas, text = 'Resign', bd = 0,
            width = 5, height = 1, highlightthickness = 0, padx = 0, pady = 0, 
            command = self.comm_resign)
        self.resign_but.pack(side = 'left')

    def clr_dis(self, root, colour, height, width, col, row):
        clr_frame = tk.Frame(root, height = height, width = width)
        clr_frame.grid(column = col, row = row)
        score_disp = tk.Label(clr_frame, text = self.board.scores[colour],
                fg = colour, font = (None, 40))
        if height > width:
            cap_disp = tk.Canvas(clr_frame, highlightthickness = 0,
                    width = width, bg = 'white')
            score_disp.pack(side = 'top', expand = 0)
            cap_disp.pack(side = 'top', fill = 'y', expand = 1)
        else:
            cap_disp = tk.Canvas(clr_frame, highlightthickness = 0,
                    height = height, bg = 'white')
            score_disp.pack(side = 'left', expand = 0)
            cap_disp.pack(side = 'left', fill = 'x', expand = 1)

        self.score_displays[colour] = score_disp
        return cap_disp
            
    def cap_update_all(self):
        self.cap_piece_update(self.clr_1, COLOUR_INFO[0], 4, 0)
        self.cap_piece_update(self.clr_2, COLOUR_INFO[1], 0, 4)
        self.cap_piece_update(self.clr_3, COLOUR_INFO[2], 4, 0)
        self.cap_piece_update(self.clr_4, COLOUR_INFO[3], 0, 4)
        if self.board.game_over:
            self.game_over_apply()

    def cap_piece_update(self, disp, colour,  rows, cols):
        cap_list = self.board.capture_list[colour]
        disp.delete('all')
        if len(cap_list) == 0:
            return
        if rows > 0:
            cols = int(np.ceil(len(cap_list) / rows))
            remainder = (rows - len(cap_list)) % rows
            cap_dummy = cap_list + remainder * [False]
            spacing = 90/rows
        elif cols > 0:
            rows = int(np.ceil(len(cap_list) / cols))
            remainder = (cols - len(cap_list)) % cols
            cap_dummy = cap_list + remainder * [False]
            spacing = 90/cols
        cap_arr = np.reshape(cap_dummy, (rows, cols)) 
        for i in range(rows):
            for j in range(cols):
                piece = cap_arr[i][j]
                if not piece:
                    continue
                pos_x = 10+j*spacing
                pos_y = 10+i*spacing
                text = PIECE_INFO[piece.name]['unicode']
                fill = piece.colour
                disp.create_text(pos_x, pos_y, text = text, fill = fill, 
                    font = (None, 20))

    def tools_init(self):
        self.tools = tk.Canvas(self.frame, background = 'white', width = 300,
            height = self.board_height, highlightthickness = 0)
        self.tools.grid(column = 4, row = 1)

        self.tool_frame = tk.Frame(self.tools, background = 'white',
            width = 300, height = self.board_height)
        self.tool_scroll = tk.Scrollbar(self.frame, orient = 'vertical',
            command = self.tools.yview)

        self.tools.config(yscrollcommand = self.tool_scroll.set)

        self.tool_frame.grid(column = 0, row = 0)
        self.tool_scroll.grid(column = 5, row = 1, sticky = 'ns')

        self.tool_window = self.tools.create_window((0,0),
                window = self.tool_frame, anchor = 'nw')

        self.tool_frame.bind('<Configure>', self.toolconfig)

        self.tool_opt()

    def tool_opt(self):
        self.tool_options = tk.LabelFrame(self.frame, background = 'white',
            width = 300, height = 15, highlightthickness = 0)
        self.tool_options.grid(row = 2, column = 4)

        self.new_but = tk.Button(self.tool_options, text = 'New game',
                width = 5, height = 1, command = self.new_game)
        self.new_but.pack(side = 'left')

        self.save_but = tk.Button(self.tool_options, text = 'Save',
                width = 5, height = 1, command = self.save_game)
        self.save_but.pack(side = 'left')

        self.load_but = tk.Button(self.tool_options, text = 'Load',
                width = 5, height = 1, command = self.load_game)
        self.load_but.pack(side = 'left')

    def toolconfig(self, event):
        self.tools.configure(scrollregion = self.tool_frame.bbox('all'))

    def new_game(self):
        new_game_win = tk.Toplevel()
        
        new_warning_text = tk.Label(new_game_win, text = ('Are you sure '+
            'you want to reset the board?'))
        new_warning_text.pack(fill = 'x', side = 'top')

        game_reset = tk.Button(new_game_win, text = 'Reset', 
                command = lambda: [self.reset(), self.piece_init(), 
                        new_game_win.destroy()])
        game_reset.pack(side = 'left')

        game_reset_cancel = tk.Button(new_game_win, text = 'Cancel',
                command = lambda: new_game_win.destroy())
        game_reset_cancel.pack(side = 'right')        

    def save_game(self):

        self.comm_pgn_save()

        win = tk.Toplevel()
        win.geometry('600x600')

        save_text = tk.Text(win)
        save_text.grid(row = 0, column = 0, sticky = 'nsew')
        save_text.insert(tk.END, self.saving_moves)
        
        save_but_frame = tk.LabelFrame(win, background = 'white',
            highlightthickness = 0, height = 15, width = 600)
        save_but_frame.grid(row = 1, column = 0)

        save_pgn_but = tk.Button(save_but_frame, text = 'PGN4', 
                command = lambda: [self.comm_pgn_save(), 
                    save_text.delete('1.0', tk.END),
                    save_text.insert(tk.END, self.saving_moves)])
        save_pgn_but.pack(side = 'left')

        save_fen_but = tk.Button(save_but_frame, text = 'FEN4', 
                command = lambda: [self.comm_fen_save(),
                    save_text.delete('1.0', tk.END),
                    save_text.insert(tk.END, self.saving_moves)])
        save_fen_but.pack(side = 'left')

        save_text_but = tk.Button(save_but_frame, text = 'Copy to clipboard',
                command = lambda: pyperclip.copy(self.saving_moves))
        save_text_but.pack(side = 'left')

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
    
    def comm_pgn_save(self):
        move_list = self.board.move_list
        moves_str = ''
        
        for move in move_list:
            if move.colour == self.board.colours[0]:
                moves_str = moves_str + str(move.number) + '. '
            moves_str = moves_str + move.pgn

            if move.colour != self.board.colours[-1]:
                moves_str = moves_str + ' .. '
            else:
                moves_str = moves_str + '\n'
        self.saving_moves = moves_str

    def load_game(self):
        win = tk.Toplevel()
        win.geometry('600x600')

        self.load_text = tk.Text(win)
        self.load_text.pack(side = 'top', fill = tk.Y, expand = 1)

        load_game_pgn_but = tk.Button(win, text = 'Load PGN4', 
                command = lambda: [self.comm_load_pgn(), win.destroy()])
        load_game_pgn_but.pack(side = 'bottom')

        load_game_fen_but = tk.Button(win, text = 'Load FEN4',
                command = lambda: [self.comm_load_fen(), win.destroy()])
        load_game_fen_but.pack(side = 'bottom')

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)

    def reset(self):
        self.board = Board()
        for obj_number in self.piece_loc.keys():
            self.board_canvas.delete(obj_number)
                
        for label_object in self.tool_frame.winfo_children():
            label_object.destroy()
        self.cap_update_all()
        for clr, score in self.board.scores.items():
            self.score_displays[clr]['text'] = score
        self.update_to_play()
        self.move_number = 0
        self.state_idx = -1
        self.game_over = False
        self.move_obj = []

    def comm_resign(self):
        resign_win = tk.Toplevel()
        
        resign_warning = tk.Label(resign_win, text = ('Are you sure '+
            'you want to resign ({})'.format(self.board.to_play)), 
                fg = self.board.to_play)
        resign_warning.pack(fill = 'x', side = 'top')

        resign = tk.Button(resign_win, text = 'Resign', 
                command = lambda: [self.resign(), resign_win.destroy()])
        resign.pack(side = 'left')

        resign_cancel = tk.Button(resign_win, text = 'Cancel',
                command = lambda: resign_win.destroy())
        resign_cancel.pack(side = 'right')        

    def comm_load_pgn(self):
        self.load_pgn(self.load_text.get('1.0', 'end-1c'))
        return

    def comm_load_fen(self):
        self.load_fen(self.load_text.get('1.0', 'end-1c'))
        self.board.fen_to_board(self.load_text.get('1.0', 'end-1c'))
        return

    def resign(self):
        clr = self.board.to_play
        for piece in self.board.piece_pos[clr]:
            if piece.loc != None:
                loc = piece.loc
            else:
                continue
            obj = list(self.piece_loc.keys())[list(
                    self.piece_loc.values()).index(loc)]
            if piece.name != 'King':
                self.board_canvas.itemconfig(obj, fill = 'black')
        self.board.resign_apply()

        self.res_king_move()

        self.resign_check()
        
    def res_king_move(self):
        king_start = self.board.move_list[-1].start
        king_end = self.board.move_list[-1].end

        for obj, loc in self.piece_loc.items():
            if king_start == loc:
                obj_king = obj
            elif king_end == loc:
                obj_del = obj
                self.piece_loc[obj_del] = False
                self.board_canvas.delete(obj_del)

        file_end, rank_end = move_to_rank_file(king_end)
        index_x = file_end
        index_y = self.board.nrows + 1 - rank_end
            
        pos_x = (index_x-0.5)*self.s_height
        pos_y = (index_y-0.5)*self.s_width

        self.board_canvas.coords(obj_king, (pos_x, pos_y))
            
        self.piece_loc[obj_king] = king_end

        self.move_populate(self.board.move_list)
        self.update_to_play()

    def resign_check(self):
        while self.board.to_play in self.board.resign_list and not self.game_over:
            king_loc = self.board.king_loc[self.board.to_play]
            king_col = self.board.square_find(king_loc).piece.colour
            if king_col in self.board.colours:
                self.board.king_random_move(king_loc)
                self.res_king_move()
        if len(self.board.colours) - len(self.board.resign_list) == 1:
            self.game_over = True
            self.game_over_apply()
        return

    def game_over_apply(self):
        game_over_win = tk.Toplevel()

        final_col = next(iter((set(self.board.colours) - 
                        set(self.board.resign_list))))
        self.board.scores[final_col] += len(self.board.resign_list)*20

        tk.Label(game_over_win, text = 'GAME OVER', font = (None, 35)).pack()

        for clr in COLOUR_INFO:
            tk.Label(game_over_win, text = '{}: {}'.format(clr, 
                self.board.scores[clr]), fg = clr).pack()

        for clr, score in self.board.scores.items():
            self.score_displays[clr]['text'] = score     

        self.resign_but.destroy()
        self.game_over = True
        self.board.game_over = True

    def rank_file_labels(self):
        file_labels = tk.Canvas(self.frame, width = self.board_width,
            height = 20, highlightthickness = 0)
        file_labels.grid(column = 2, row = 2)
        
        alphabet = string.ascii_uppercase
        files_ = list(alphabet[:self.board.ncols])
        for idx, file_ in enumerate(files_):
            file_labels.create_text((idx+0.5)*self.s_width, 5, text = file_)

        rank_labels = tk.Canvas(self.frame, width = 20,
            height = self.board_height, highlightthickness = 0)
        rank_labels.grid(column = 1, row = 1)
       
        for i in range(14, 0, -1):
            rank_labels.create_text(10, self.board_height - (i-0.5)*self.s_height,                  text = i)

    def board_init(self): 
        for i in range(self.board.nrows):
            for j in range(self.board.ncols):
                if (i + j)%2 == 0:
                    colour = 'lightgray'
                elif (i+j)%2 == 1:
                    colour = 'gray'
                if ((i < self.board.corner or 
                    i >= self.board.nrows - self.board.corner) and
                    (j < self.board.corner or 
                    j >= self.board.ncols - self.board.corner)):
                    colour = 'black'

                self.board_canvas.create_rectangle(i*self.s_width,
                        j*self.s_height, (i+1)*self.s_width,
                        (j+1)*self.s_height, fill = colour)
        
        #Checks if square has piece and if it does then plots it with 
        #respective symbol

        self.board_canvas.bind('<ButtonPress-1>', self.pick_up)
        self.board_canvas.bind('<B1-Motion>', self.drag)
        self.board_canvas.bind('<ButtonRelease-1>', self.drop) 

    def piece_init(self):
        piece_loc = {}
        for square in self.board.squares.ravel():
            if square.piece == None:
                continue
            else:
                piece = square.piece

            pos_x = (square.file_ - 0.5) * self.s_height
            pos_y = (self.board.nrows + 0.5 - square.rank) * self.s_width

            colour = piece.colour
            if piece.dead:
                colour = 'black'

            text = self.board_canvas.create_text(pos_x, pos_y,
                text = PIECE_INFO[piece.name]['unicode'], 
                fill = colour, font = (None, 35))

            piece_loc[text] = piece.loc

        self.piece_loc = piece_loc

    def pick_up(self, event):
        if self.game_over or self.board_review:
            return

        object_id = self.board_canvas.find_closest(event.x, event.y, halo=0)[0]

        if object_id in self.piece_loc.keys():
            self.drag_piece = object_id
            self.drag_x = event.x
            self.drag_y = event.y
        else:
            self.drag_piece = None

    def drag(self, event):
        if self.game_over or self.board_review:
            return
        if self.drag_piece == None:
            return

        delta_x = event.x - self.drag_x
        delta_y = event.y - self.drag_y

        self.board_canvas.move(self.drag_piece, delta_x, delta_y)

        self.drag_x = event.x
        self.drag_y = event.y

    def drop(self, event):
        if self.game_over or self.board_review:
            return
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

                self.board_canvas.delete(piece_delete)
                
                self.piece_loc[piece_delete] = False
            except ValueError:
                pass

            self.piece_loc[self.drag_piece] = move_end
            self.move_populate(self.board.move_list)

            self.special_move_apply(move_end)

            self.cap_update_all()

            for clr, score in self.board.scores.items():
                self.score_displays[clr]['text'] = score

            self.update_to_play()
            self.resign_check()

        else:
            pos_x = (index_init_x-0.5)*self.s_height
            pos_y = (index_init_y-0.5)*self.s_width

        self.board_canvas.coords(self.drag_piece, (pos_x, pos_y))

    def move_populate(self, move_list):
        if len(move_list) == 1:
            prev_move_num = 0
        else:
            prev_move_num = move_list[-2].number

        current_move = move_list[-1]
        move_number = current_move.number
        display_move = current_move.display
        clr = current_move.colour

        num_clrs = len(COLOUR_INFO)
        column = ((COLOUR_INFO.index(
                        move_list[-1].colour)) %num_clrs)+1
        
        if move_number > prev_move_num:
            tk.Label(self.tool_frame, text = move_number, width = 2, bg = 'grey',
                    ).grid(column = 0, row = move_number - 1)
        
        move_obj = tk.Label(self.tool_frame, text = display_move, bg = 'grey',
            width = 6, fg = clr)
        move_obj.grid(row = move_number - 1, column = column)
        
        self.move_obj.append(move_obj) 

        move_obj.bind('<ButtonPress-1>', lambda event, move_obj = move_obj:
                    self.board_change(move_obj))

        move_obj.config(bg = 'black')
        
        if len(self.move_obj) > 1:
            self.move_obj[-2].config(bg = 'grey')

        self.move_number = self.move_number + 1
        self.state_idx = self.state_idx + 1

    def board_change(self, move_obj):
        self.board_review = True

        idx_max = self.move_number - 1
        idx = self.state_idx
        idx_end = self.move_obj.index(move_obj)

        self.move_obj[idx].config(bg = 'grey')
        move_obj.config(bg = 'black')

        stop = False

        if idx > idx_end:
            step = -1
        elif idx < idx_end:
            step = 1
        elif idx == idx_end:
            stop = True
        while not stop:
            self.board_state(idx, step)
            if (step == 1 and idx == idx_end - 1 or 
                    step == -1 and idx == idx_end + 1):
                stop = True
            idx = idx + step

        self.state_idx = idx

        for obj_number in self.piece_loc.keys():
            self.board_canvas.delete(obj_number)
        
        self.piece_init()
        self.cap_update_all()
        self.update_to_play()
        
        for clr, score in self.board.scores.items():
            self.score_displays[clr]['text'] = score

        if idx == idx_max:
            self.board_review = False

    def board_state(self, idx, direction):

        if direction == 1:
            idx = idx + direction
        move = self.board.move_list[idx]
        self.board.temp_move_apply(move, direction)

    def special_move_apply(self, move_end):
        
        end_piece = self.board.square_find(move_end).piece
        if end_piece.name == 'Queen' and end_piece.promoted == True:
            self.board_canvas.itemconfig(self.drag_piece, 
                    text = PIECE_INFO['Queen']['unicode'])

        castle_check = self.board.move_list[-1].castling
        if castle_check:
            self.castle_move(castle_check, end_piece)

        if len(self.board.move_list[-1].mating) > 0:
            for col in self.board.move_list[-1].mating:
                for piece in self.board.piece_pos[col]:
                    if piece.loc != None:
                        loc = piece.loc
                    else:
                        continue
                    obj = list(self.piece_loc.keys())[list(
                            self.piece_loc.values()).index(loc)]
                    self.board_canvas.itemconfig(obj, fill = 'black')

        enpassant_loc = self.board.move_list[-1].enpassant_cap
        if enpassant_loc:
            obj = list(self.piece_loc.keys())[list(
                    self.piece_loc.values()).index(enpassant_loc)]

            self.board_canvas.delete(obj)            
            self.piece_loc[obj] = False

    def castle_move(self, castle_check, king_piece):
        rook_start_square, rook_end_square = king_piece.rook_square(castle_check)
                
        rook_obj = list(self.piece_loc.keys())[list(
            self.piece_loc.values()).index(rook_start_square)]
        
        file_end, rank_end = move_to_rank_file(rook_end_square)
        index_x = file_end
        index_y = self.board.nrows + 1 - rank_end
            
        pos_x = (index_x-0.5)*self.s_height
        pos_y = (index_y-0.5)*self.s_width

        print(index_x, index_y, pos_x, pos_y)

        self.board_canvas.coords(rook_obj, (pos_x, pos_y))
            
        self.piece_loc[rook_obj] = rook_end_square

    def update_to_play(self):
        clr = self.board.to_play
        self.to_move_label.config(text = '{} to play'.format(clr), fg = clr)

    def coords_to_index(self, x, y):
        index_x = np.ceil(x/self.s_width)
        index_y = np.ceil(y/self.s_height)
        return index_x, index_y

    def index_to_move(self, index_x, index_y):
        file_ = round(index_x)
        rank = round(self.board.nrows + 1 - index_y)
        move_code = alphabet[file_-1] + '{}'.format(rank)
        return move_code

    def pgn_to_moves(self, pgn):
        if len(pgn) == 1:
            return 0, 0
        if pgn == 'O-O' or pgn == 'O-O-O':
            if pgn == 'O-O':
                castle_type = 'King'
            else:
                castle_type = 'Queen'
            clr = self.board.to_play
            move_start = self.board.king_loc[clr]
            king_piece = self.board.square_find(move_start).piece
            move_end = king_piece.king_castle_square(castle_type)

        else:
            move_split = pgn.split('+')
            move_split = move_split[0].split('=D')
            move_split = move_split[0].split('#')
            move_split = move_split[0].split('x')

            if len(move_split) == 1:
                move_split = move_split[0].split('-')

            for idx, string in enumerate(move_split):
                if string[0].isupper():
                    move_split[idx] = string[1:]
            move_start = move_split[0]
            move_end = move_split[1]
        return move_start, move_end

    def load_pgn(self, pgn_code):
        move_text = pgn_code.split('\n1. ', 1)[1]
        move_num_split = move_text.split('\n')
        
        move_list = []

        self.reset()

        for idx, line in enumerate(move_num_split): 
            if line == '':
                continue
            if idx != 0:
                print(line)
                line = line.split(' ', 1)[1]
            move_number = idx + 1
            moves = line.split(' .. ')
            for pgn in moves:
                resign = False
                if pgn[-1] == 'R':
                    self.board.resign_apply(move = False)
                    pgn = pgn[:-1]
                    resign = True
                    if len(self.board.colours) - len(self.board.resign_list) == 1:
                        self.game_over = True
                        continue
                move_start, move_end = self.pgn_to_moves(pgn)
                self.board.move(move_start, move_end, resign)
                self.move_populate(self.board.move_list)
        
        for clr, score in self.board.scores.items():
            self.score_displays[clr]['text'] = score

        self.piece_init()
        self.cap_update_all()
        self.update_to_play()
        self.resign_check()

    def load_fen(self, fen_code):
        self.reset()
        self.board.fen_to_board(fen_code)
        self.piece_init()
        self.update_to_play()
        self.resign_check()

    def comm_fen_save(self):
        fen = ''

        fen = fen + self.board.to_play[0] + '-'
        
        in_game = []
        king_castle = []
        queen_castle = []
        score = []

        for clr in COLOUR_INFO:
            if clr in self.board.colours:
                in_game.append(str(0))
            else:
                in_game.append(str(1))
            king_castle.append(str(self.board.king_castle[clr]))
            queen_castle.append(str(self.board.queen_castle[clr]))
            score.append(str(self.board.scores[clr]))

        fen = (fen + ','.join(in_game) + '-' + ','.join(king_castle) + '-' +
                ','.join(queen_castle) + '-' + ','.join(score) + '-')

        fen = fen + str(self.board.half_moves) + '-\n' + self.board.board_pos_fen()
   
        print(fen)

        self.saving_moves = fen

def move_to_rank_file(move_name):
    file_letter = move_name[0]
    file_number = int(alphabet.find(file_letter))+1
    rank_number = int(move_name[1:])
    return file_number, rank_number

def rank_file_to_move(file_, rank):
    move_code = alphabet[file_-1] + '{}'.format(rank)
    return move_code

game = Display()
game.mainloop()


