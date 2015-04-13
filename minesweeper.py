from tkinter import *
import tkinter.messagebox
import random

_font = 'Verdana 12'
_fg = 'black'
_bg = 'light blue'
f_fg = 'dark blue'
m_fg = 'black'
m_bg = 'red'
r_fg = 'dark red'
r_bg = 'gray'

headers = ['-Mode-', '-Height-', '-Width-', '-Mines-']
select = [['Beginner',     '9',  '9',  '10'],
          ['Intermediate', '16', '16', '40'],
          ['Expert',       '16', '30', '99']]

class Square(Button):
    def __init__(self, game, row, column):
        Button.__init__(self, game, fg=_fg, bg=_bg, height=1, width=3,
                        font=_font, bd=1, command=self.reveal)
        self.game, self.row, self.column = game, row, column
        self.mined = False
        self.bind('<3>', self.flag)

    @property
    def revealed(self):
        return not self.cget('bg') == _bg

    @property
    def flagged(self):
        return self.cget('text') == '?'

    def flag(self, *args):
        if self.revealed:
            return
        if not self.flagged:
            self.config(text='?', fg=f_fg)
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
            square = self.game.get_square(self.row+dr, self.column+dc)
            ret.append(square)
        return ret

    @property
    def adj_mines(self):
        ret = 0
        for square in self.adj_squares:
            if square.mined:
                ret += 1
        return ret

    def reveal(self):
        def first_turn():
            if self.mined: # mercy rule
                self.mined = False
                self.game.mercy_square.make_mine()
            self.game.started = True
            self.game.clock = self.after(0, self.game.start_timer)
        def reveal_mined():
            self.config(text='X', fg=m_fg, bg=m_bg)
            self.game.end('lose')
        def reveal_zero():
            self.config(bg='white')
            for square in self.adj_squares: # adj_reveal
                square.reveal()
        def reveal_number():
            self.config(text=str(self.adj_mines), fg=r_fg, bg=r_bg)
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

    hard_reveal = lambda self: self.config(text='X', fg=m_fg, bg=m_bg)


class NullSquare:
    mined = False
    reveal = lambda self: None

null_square = NullSquare()


class Game(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title('Minesweeper')
        self.prompt()

    def prompt(self):
        def make_headers():
            for i in range(len(headers)):
                header = Label(self, text=headers[i], padx=5)
                header.grid(row=0, column=i)
        def make_select():
            for r in range(len(select)):
                name = select[r][0]
                radio = Radiobutton(self, text=name, variable=mode,
                                                value=r+1, padx=10)
                radio.grid(row=r+1, sticky=W)
                for c in range(1, len(select[r])):
                    stat = Label(self, text=select[r][c], padx=10)
                    stat.grid(row=r+1, column=c, sticky=W)
        def make_custom():
            c_radio = Radiobutton(self, text='Custom', variable=mode,
                                                     value=0, padx=10)
            c_radio.grid(row=len(select)+1, sticky=W)
            entries = [Entry(self, width=5, justify=CENTER)
                            for _ in range(len(select[0])-1)]
            for i in range(len(entries)):
                entries[i].grid(row=len(select)+1, column=i+1, sticky=W)
            return entries
        def make_ok():
            ok = Button(self, text='OK', width=7)
            ok.grid(row=len(select)+2, column=len(select[0])-1, sticky=NW)
            # command=process
        def process():
            if mode.get() == 0:
                pass
                # f = lambda x: int(entry[x].get())
            else:
                pass
                # i = mode.get()
                # f = lambda x: int(select[i][x])
            # new_game(f(0), f(1), f(2))
        mode = IntVar()
        make_headers()
        make_select()
        entries = make_custom()
        mode.set(1)
        make_ok()
        # self.new_game(16, 30, 99)
        # hook up entries, OK

    def new_game(self, rows, columns, mines):
        def make_squares():
            self.squares = [Square(self, r, c) for r in range(rows)
                                               for c in range(columns)]
            for square in self.squares:
                        square.grid(row=square.row+1,
                                    column=square.column)
        def make_mercy():
            r = random.randrange(self.rows)
            c = random.randrange(self.columns)
            self.mercy_square = self.get_square(r, c)
        def make_mines():
            for _ in range(mines):
                square = random.choice(self.squares)
                while square.mined or square is self.mercy_square:
                    square = random.choice(self.squares)
                square.make_mine()
        def make_unflagged_counter():
            self.u_counter = Label(self, text=str(self.mines), fg=_fg,
                                   font=_font)
            self.u_counter.grid(row=0, column=0)
        def make_timer():
            self.timer = Label(self, text='0', fg=_fg, font=_font)
            self.timer.grid(row=0, column=columns-1)
        self.rows, self.columns, self.mines = rows, columns, mines
        self.time, self.clock, self.started = -1, None, False
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
                    square.hard_reveal()
        def same_grid():
            for widget in self.winfo_children():
                widget.destroy()
            self.prompt()
        def win():
            return tkinter.messagebox.askyesno('Victory!',
                            'Congratulations, you won!\nPlay again?')
        def lose():
            return tkinter.messagebox.askyesno('Defeat',
                                            'You lost!\nPlay again?')
        stop_timer()
        reveal_mined()
        if eval(result)():
            same_grid()
        else:
            self.destroy()

    def check(self):
        for square in self.squares:
            if not square.revealed and not square.mined:
                return
        self.end('win')


Game().mainloop()