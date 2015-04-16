from tkinter import *
import tkinter.messagebox
import random

FONT = 'Verdana 12'
FG = 'black'
BG = 'light blue'
F_FG = 'dark blue'
M_FG = 'black'
M_BG = 'red'
R_FG = 'dark red'
R_BG = 'gray'
Z_BG = 'white'

class Square(Button):
    class null:
        mined = False
        reveal = lambda self: None

    null = null()

    def __init__(self, game, row, column):
        Button.__init__(self, game, fg=FG, bg=BG, height=1, width=3,
                        font=FONT, bd=1, command=self.click)
        self.game, self.row, self.column = game, row, column
        self.mined = False
        self.bind('<3>', self.flag)

    def make_mine(self):
        self.mined = True

    def unmake_mine(self):
        self.mined = False

    @property
    def revealed(self):
        return self.cget('bg') != BG

    @property
    def flagged(self):
        return self.cget('text') == '?'

    def flag(self, *args):
        if not self.flagged:
            self.config(text='?', fg=F_FG)
        else:
            self.config(text='', fg=FG)
        u_counter = self.game.u_counter
        unflagged = str(self.game.unflagged)
        u_counter.config(text=unflagged)

    @property
    def adj_squares(self):
        ret = []
        for dr, dc in [(-1,  1), (0,  1), (1,  1),
                       (-1,  0),          (1,  0),
                       (-1, -1), (0, -1), (1, -1)]:
            adj_square = self.game.get_square(self.row+dr, self.column+dc)
            ret.append(adj_square)
        return ret

    @property
    def adj_mines(self):
        ret = 0
        for square in self.adj_squares:
            if square.mined:
                ret += 1
        return ret

    def reveal(self):
        def reveal_first():
            if self.mined: # mercy rule
                self.unmake_mine()
                self.game.mercy_square.make_mine()
            self.game.started = True
            self.game.clock = self.after(0, self.game.start_timer)
        def reveal_mined():
            self.config(text='X', fg=M_FG, bg=M_BG)
        def reveal_zero():
            self.config(bg=Z_BG)
            for square in self.adj_squares: # adj_reveal
                square.reveal()
        def reveal_number():
            self.config(text=str(self.adj_mines), fg=R_FG, bg=R_BG)
        if self.revealed:
            return
        if self.flagged:
            self.flag()
        if not self.game.started:
            reveal_first()
        if self.mined:
            reveal_mined()
        elif self.adj_mines == 0:
            reveal_zero()
        else:
            reveal_number()

    def click(self):
        if self.flagged:
            return
        self.reveal()
        self.game.check()


class Mode:    
    attrs = ['height', 'width', 'mines']
    headers = ['-Mode-', '-Height-', '-Width-', '-Mines-']

    def __init__(self, height, width, mines, name=None):
        self.height, self.width, self.mines = height, width, mines
        self.name = name

Mode.beginner =     Mode(9,  9,  10, 'Beginner')
Mode.intermediate = Mode(16, 16, 40, 'Intermediate')
Mode.expert =       Mode(16, 30, 99, 'Expert')
Mode.defaults = [Mode.beginner, Mode.intermediate, Mode.expert]


class Game(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Minesweeper')
        self.prompt()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def prompt(self):
        def make_headers():
            for c in range(len(Mode.headers)):
                header = Label(self, text=Mode.headers[c], padx=8)
                header.grid(row=0, column=c)
        def make_modes():
            for r in range(len(Mode.defaults)):
                mode = Mode.defaults[r]
                radio = Radiobutton(self, text=mode.name,
                                    variable=self.choice,
                                    value=mode.name, padx=10)
                radio.grid(row=r+1, sticky=W)
                for c in range(len(Mode.attrs)):
                    mode_attr = eval('mode.'+Mode.attrs[c])
                    attr = Label(self, text=mode_attr)
                    attr.grid(row=r+1, column=c+1)
        def make_custom():
            c_radio = Radiobutton(self, text='Custom',
                                  variable=self.choice,
                                  value='Custom', padx=10)
            c_radio.grid(row=len(Mode.defaults)+1, sticky=W)
            entries = [Entry(self, width=5, justify=CENTER)
                           for _ in range(len(Mode.attrs))]
            for c in range(len(entries)):
                entries[c].grid(row=len(Mode.defaults)+1, column=c+1)
            return entries
        def make_ok():
            ok = Button(self, text='OK', width=7, command=process)
            ok.grid(row=len(Mode.defaults)+2, column=len(Mode.attrs))
        def process():
            choice = self.choice.get().lower()
            if choice == 'custom':
                h = int(entries[0].get())
                w = int(entries[1].get())
                m = int(entries[2].get())
                mode = Mode(h, w, m)
            else:
                mode = eval('Mode.'+choice)
            self.new_game(mode)
        self.clear()
        self.choice = StringVar()
        self.choice.set('Beginner')
        make_headers()
        make_modes()
        entries = make_custom()
        make_ok()

    def new_game(self, mode):
        def make_squares():
            self.squares = [Square(self, r, c)
                            for c in range(self.columns)
                            for r in range(self.rows)]
            for square in self.squares:
                square.grid(row=square.row+1, column=square.column)
        def make_mercy():
            r = random.randrange(self.rows)
            c = random.randrange(self.columns)
            self.mercy_square = self.get_square(r, c)
        def make_mines():
            for _ in range(self.mines):
                square = random.choice(self.squares)
                while square.mined or square is self.mercy_square:
                    square = random.choice(self.squares)
                square.make_mine()
        def make_unflagged_counter():
            self.u_counter = Label(self, text=str(self.mines), font=FONT)
            self.u_counter.grid(row=0, column=0)
        def make_timer():
            self.timer = Label(self, text='0', font=FONT)
            self.timer.grid(row=0, column=self.columns-1)
        self.mode, self.mines = mode, mode.mines
        self.rows, self.columns = mode.height, mode.width
        self.time, self.clock, self.started = -1, None, False
        self.clear()
        make_squares()
        make_mercy()
        make_mines()
        make_unflagged_counter()
        make_timer()

    @property
    def unflagged(self):
        ret = self.mines
        for square in self.squares:
            if square.flagged:
                ret -= 1
        return ret

    def start_timer(self):
        self.time += 1
        self.timer.config(text=str(self.time))
        self.clock = self.after(1000, self.start_timer)

    def get_square(self, row, column):
        for square in self.squares:
            if square.row == row and square.column == column:
                return square
        return Square.null

    def end(self, result):
        def stop_timer():
            if self.clock is not None:
                self.after_cancel(self.clock)
        def reveal_all_mined():
            for square in self.squares:
                if square.mined:
                    square.reveal()
        def win():
            return tkinter.messagebox.askyesno('Victory!',
                            'Congratulations, you won!\nReplay?')
        def lose():
            return tkinter.messagebox.askyesno('Defeat',
                                            'You lost!\nReplay?')
        stop_timer()
        reveal_all_mined()
        if eval(result)():
            self.new_game(self.mode)
        else:
            self.prompt()

    def check(self):
        win = True
        for square in self.squares:
            if square.mined and square.revealed:
                self.end('lose')
            if not square.mined and not square.revealed:
                win = False
        if win:
            self.end('win')


Game().mainloop()

