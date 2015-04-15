from tkinter import *
import tkinter.messagebox
import random

_font = 'Verdana 12'
_fg = 'black'

class Square(Button):

    _bg = 'light blue'
    f_fg = 'dark blue'
    m_fg = 'black'
    m_bg = 'red'
    r_fg = 'dark red'
    r_bg = 'gray'
    z_bg = 'white'

    def __init__(self, game, row, column):
        Button.__init__(self, game, fg=_fg, bg=self._bg, height=1,
                        width=3, font=_font, bd=1,
                        command=self.reveal)
        self.game, self.row, self.column = game, row, column
        self.mined = False
        self.bind('<3>', self.flag)

    @property
    def revealed(self):
        return not self.cget('bg') == self._bg

    @property
    def flagged(self):
        return self.cget('text') == '?'

    def flag(self, *args):
        if self.revealed:
            return
        if not self.flagged:
            self.config(text='?', fg=self.f_fg)
        else:
            self.config(text='', fg=_fg)
        u_counter = self.game.u_counter
        unflagged = str(self.game.unflagged)
        u_counter.config(text=unflagged)

    def make_mine(self):
        self.mined = True

    @property
    def adj_squares(self):
        ret = []
        for dr, dc in [(-1, 1),  (0, 1),  (1, 1),
                       (-1, 0),           (1, 0),
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

    naive_reveal_mined = lambda self: self.config(text='X', fg=self.m_fg,
                                                  bg=self.m_bg)
    def reveal(self):
        def first_turn():
            if self.mined: # mercy rule
                self.mined = False
                self.game.mercy_square.make_mine()
            self.game.started = True
            self.game.clock = self.after(0, self.game.start_timer)
        def reveal_mined():
            self.naive_reveal_mined()
            self.game.end('lose')
        def reveal_zero():
            self.config(bg=self.z_bg)
            for square in self.adj_squares: # adj_reveal
                square.reveal()
        def reveal_number():
            self.config(text=str(self.adj_mines), fg=self.r_fg,
                        bg=self.r_bg)
        if self.revealed or self.flagged:
            return
        if not self.game.started:
            first_turn()
        if self.mined:
            return reveal_mined()
        elif self.adj_mines == 0:
            reveal_zero()
        else:
            reveal_number()
        self.game.check()


class NullSquare:
    mined = False
    reveal = lambda self: None

null_square = NullSquare()


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
            self.squares = [Square(self, r, c) for r in range(self.rows)
                                            for c in range(self.columns)]
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
            self.u_counter = Label(self, text=str(self.mines), font=_font)
            self.u_counter.grid(row=0, column=0)
        def make_timer():
            self.timer = Label(self, text='0', font=_font)
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
        return null_square

    def end(self, result):
        def stop_timer():
            if self.clock is not None:
                self.after_cancel(self.clock)
        def reveal_mined():
            for square in self.squares:
                if square.mined:
                    square.naive_reveal_mined()
        def win():
            return tkinter.messagebox.askyesno('Victory!',
                            'Congratulations, you won!\nReplay?')
        def lose():
            return tkinter.messagebox.askyesno('Defeat',
                                            'You lost!\nReplay?')
        def same_grid():
            self.new_game(self.mode)
        def new_grid():
            self.prompt()
        stop_timer()
        reveal_mined()
        if eval(result)():
            same_grid()
        else:
            new_grid()

    def check(self):
        for square in self.squares:
            if not square.revealed and not square.mined:
                return
        self.end('win')


Game().mainloop()

