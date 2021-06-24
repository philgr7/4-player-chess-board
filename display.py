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

    def colour_init(self):
        self.col_1 = tk.Canvas(self.frame, background = 'white', height = 100,
            width = self.board_width, highlightthickness = 0)
        self.col_1.grid(column = 2, row = 3)
        self.col_2 = tk.Canvas(self.frame, background = 'white', width = 100,
            height = self.board_height, highlightthickness = 0)
        self.col_2.grid(column = 0, row = 1)
        self.col_3 = tk.Canvas(self.frame, background = 'white', height = 100,
            width = self.board_width, highlightthickness = 0)
        self.col_3.grid(column = 2, row =0)
        self.col_4 = tk.Canvas(self.frame, background = 'white', width = 100,
                height = self.board_height, highlightthickness = 0)
        self.col_4.grid(column = 3, row = 1)

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
            width = 300, height = 25, highlightthickness = 0)
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
                command = lambda: [self.reset(), self.piece_init()])
        game_reset.pack(side = 'left')

        game_reset_cancel = tk.Button(new_game_win, text = 'Cancel',
                command = lambda: new_game_win.destroy())
        game_reset_cancel.pack(side = 'right')
        

    def save_game(self):
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

        win = tk.Toplevel()
        win.geometry('600x600')

        save_text = tk.Text(win)
        save_text.grid(row = 0, column = 0, sticky = 'nsew')
        save_text.insert(tk.END, moves_str)

        save_text_but = tk.Button(win, text = 'Copy to clipboard',
                command = lambda: pyperclip.copy(moves_str))
        save_text_but.grid(row = 1, column = 0)

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)
    
    def load_game(self):
        win = tk.Toplevel()
        win.geometry('600x600')

        self.load_text = tk.Text(win)
        self.load_text.grid(row = 0, column = 0, sticky='nsew')

        load_game_but = tk.Button(win, text = 'Load game', 
                command = self.retrieve_load)
        load_game_but.grid(row = 1, column = 0)

        win.grid_columnconfigure(0, weight=1)
        win.grid_rowconfigure(0, weight=1)

    def reset(self):
        self.board = Board()
        for obj_number in self.piece_loc.keys():
            self.board_canvas.delete(obj_number)
                
        for label_object in self.tool_frame.winfo_children():
            print(label_object)
            label_object.destroy()

    def retrieve_load(self):
        self.load_pgn(self.load_text.get('1.0', 'end-1c'))
        return

    def rank_file_labels(self):
        self.file_labels = tk.Canvas(self.frame, width = self.board_width,
            height = 25, highlightthickness = 0)
        self.file_labels.grid(column = 2, row = 2)
        self.rank_labels = tk.Canvas(self.frame, width = 25,
            height = self.board_height, highlightthickness = 0)
        self.rank_labels.grid(column = 1, row = 1)

    def board_init(self):
        
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

            text = self.board_canvas.create_text(pos_x, pos_y,
                text = PIECE_INFO[piece.name]['unicode'], 
                fill = piece.colour, font = (None, 35))

            piece_loc[text] = piece.loc

        self.piece_loc = piece_loc

    def pick_up(self, event):
   
        object_id = self.board_canvas.find_closest(event.x, event.y, halo=0)[0]

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

        self.board_canvas.move(self.drag_piece, delta_x, delta_y)

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

                self.board_canvas.delete(piece_delete)
                
                self.piece_loc[piece_delete] = False
            except ValueError:
                pass

            self.piece_loc[self.drag_piece] = move_end
            self.move_populate(self.board.move_list)

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
        
        num_clrs = len(COLOUR_INFO)
        column = ((COLOUR_INFO.index(
                        move_list[-1].colour)) %num_clrs)+1
        
        if move_number > prev_move_num:
            tk.Label(self.tool_frame, text = move_number, width = 2).grid(
                    column = 0, row = move_number - 1)
        
        tk.Label(self.tool_frame, text = display_move, width = 6).grid(
                row = move_number - 1, column = column)

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
        move_split = pgn.split('+')
        move_split = move_split[0].split('x')

        if len(move_split) == 1:
            move_split = move_split[0].split('-')

        for idx, string in enumerate(move_split):
            if string[0].isupper():
                move_split[idx] = string[1:]
        return move_split[0], move_split[1]

    def load_pgn(self, pgn_code):
        move_text = pgn_code.split('\n1. ', 1)[1]
        move_num_split = move_text.split('\n')
        
        move_list = []

        self.reset()

        for idx, line in enumerate(move_num_split): 
            if idx != 0:
                print(line)
                line = line.split(' ', 1)[1]
            move_number = idx + 1
            moves = line.split(' .. ')
            for pgn in moves:
                move_start, move_end = self.pgn_to_moves(pgn)
                self.board.move(move_start, move_end)
                self.move_populate(self.board.move_list)

        self.piece_init()

    def fen_to_board(self):
        #colour-,,,-,,,-,,,-,,,--3, yR, yN, yB,
        print('non')    
    
    def board_to_fen(self):
        print('non')

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

