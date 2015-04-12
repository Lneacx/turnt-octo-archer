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

settings = [('Beginner', 1),
            ('Intermediate', 2),
            ('Expert', 3),
            ('Custom', 0)]

class Square(Button):
    def __init__(self, game, row, column):
        Button.__init__(self, game, fg=_fg, bg=_bg, height=1, width=3,
                        font=_font, command=self.reveal)
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
        def adj_reveal():
            for square in self.adj_squares:
                square.reveal()
        if self.revealed or self.flagged:
            return
        elif not self.game.started:
            if self.mined:
                self.mined = False
                self.game.mercy_square.make_mine()
            self.game.started = True
            self.game.clock = self.after(0, self.game.start_timer)
        if self.mined:
            self.config(text='X', fg=m_fg, bg=m_bg)
            return self.game.end('lose')
        elif self.adj_mines == 0:
            self.config(bg='white')
            adj_reveal()
        else:
            self.config(text=str(self.adj_mines), fg=r_fg, bg=r_bg)
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
        self.new_trigger = None
        self.prompt()

    def prompt(self):
        # v = IntVar()
        # v.set(0)
        # labels = [Label(self, text=setting) for setting in settings]
        # for i in range(len(labels)):
        #     Radiobutton(self, value=str(labels[i][1]), variable=v)\
        #                                      .grid(row=i, column=0)
        # for i in range(len(labels)):
        #     labels[i].grid(row=i, column=1)
        # e = Entry(self).grid(row=len(labels)-1, column=2)
        self.new_game(16, 30, 99)

    def new_game(self, rows, columns, mines):
        # def remove_trigger():
        #     if self.new_trigger is not None:
        #         self.unbind('<1>', self.new_trigger)
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
        self.over = False
        # remove_trigger()
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

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def end(self, result):
        def stop_timer():
            if self.clock is not None:
                self.after_cancel(self.clock)
        def reveal_mined():
            for square in self.squares:
                if square.mined:
                    square.hard_reveal()
        def same_grid():
            self.clear()
            self.new_game(self.rows, self.columns, self.mines)
        def new_grid():
            self.clear()
            self.prompt()
        def win():
            return tkinter.messagebox.askyesno('Victory!',
                    'Congratulations, you won!\nPlay again on same grid?')
        def lose():
            return tkinter.messagebox.askyesno('Defeat',
                                    'You lost!\nPlay again on same grid?')
            # self.new_trigger = self.bind('<1>', lambda _: reset())
        self.over = True
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