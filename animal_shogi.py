# coding: utf-8

import tkinter as tk
from tkinter import messagebox
import random

CELL_SIZE = 80
ROWS = 4
COLS = 3

EMOJIS = {
    'lion': '\U0001F981',  # 🦁
    'elephant': '\U0001F418',
    'giraffe': '\U0001F992',
    'chick': '\U0001F424',
    'hen': '\U0001F414',
}

class Piece:
    def __init__(self, name, owner, promoted=False):
        self.name = name
        self.owner = owner  # 0: bottom, 1: top
        self.promoted = promoted

    @property
    def display(self):
        if self.name == 'chick' and self.promoted:
            return EMOJIS['hen']
        return EMOJIS[self.name]

    def moves(self):
        forward = -1 if self.owner == 0 else 1
        if self.name == 'lion':
            return [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
        if self.name == 'giraffe':
            return [(1,0), (-1,0), (0,1), (0,-1)]
        if self.name == 'elephant':
            return [(1,1), (1,-1), (-1,1), (-1,-1)]
        if self.name == 'chick':
            if self.promoted:
                if self.owner == 0:
                    return [(-1,0), (-1,-1), (-1,1), (0,-1), (0,1), (1,0)]
                else:
                    return [(1,0), (1,-1), (1,1), (0,-1), (0,1), (-1,0)]
            else:
                return [(forward,0)]
        return []

class Game:
    def __init__(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.hands = {0: [], 1: []}
        self.turn = 0  # 0 bottom, 1 top
        self.selected = None  # (row,col) or ('hand', index)
        self.window = tk.Tk()
        self.window.title('Animal Shogi')
        self.canvas = tk.Canvas(self.window, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_click)
        self.setup_board()
        self.draw()

    def ai_move(self):
        if self.turn != 1:
            return
        moves = []
        def piece_value(p):
            if p is None:
                return 0
            if p.name == 'lion':
                return 1000
            if p.name in ('elephant', 'giraffe'):
                return 5
            if p.name == 'chick':
                return 2 if p.promoted else 1
            return 0
        # board moves
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece and piece.owner == self.turn:
                    for nr, nc in self.legal_moves(r, c, piece):
                        captured = self.board[nr][nc]
                        score = piece_value(captured)
                        moves.append(("move", r, c, nr, nc, score))
        # drop moves
        for idx, piece in enumerate(self.hands[self.turn]):
            for r in range(ROWS):
                for c in range(COLS):
                    if self.board[r][c] is None:
                        moves.append(("drop", idx, r, c, 0))
        if not moves:
            self.end_turn()
            return
        max_score = max(m[-1] for m in moves)
        best = [m for m in moves if m[-1] == max_score]
        choice = random.choice(best)
        if choice[0] == "move":
            _, sr, sc, r, c, _ = choice
            piece = self.board[sr][sc]
            captured = self.board[r][c]
            self.board[r][c] = piece
            self.board[sr][sc] = None
            if captured:
                captured.owner = self.turn
                captured.promoted = False
                self.hands[self.turn].append(captured)
                if captured.name == 'lion':
                    messagebox.showinfo('Game Over', 'Computer wins!')
                    self.window.destroy()
                    return
            if piece.name == 'chick' and not piece.promoted:
                if (piece.owner == 0 and r == 0) or (piece.owner == 1 and r == ROWS - 1):
                    piece.promoted = True
        else:
            _, idx, r, c, _ = choice
            piece = self.hands[self.turn][idx]
            self.board[r][c] = Piece(piece.name, self.turn)
            del self.hands[self.turn][idx]
        self.draw()
        self.end_turn()

    def setup_board(self):
        # Player 1 (bottom)
        self.board[3][0] = Piece('giraffe', 0)
        self.board[3][1] = Piece('lion', 0)
        self.board[3][2] = Piece('elephant', 0)
        self.board[2][1] = Piece('chick', 0)
        # Player 2 (top)
        self.board[0][0] = Piece('elephant', 1)
        self.board[0][1] = Piece('lion', 1)
        self.board[0][2] = Piece('giraffe', 1)
        self.board[1][1] = Piece('chick', 1)

    def draw(self):
        self.canvas.delete('all')
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = '#ffe0e0' if (r + c) % 2 == 0 else '#e0e0ff'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.board[r][c]
                if piece:
                    self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2,
                                             text=piece.display, font=('Arial', 30))
        if self.selected and self.selected[0] != 'hand':
            r, c = self.selected
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=3)

    def in_bounds(self, r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def legal_moves(self, r, c, piece):
        moves = []
        for dr, dc in piece.moves():
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                target = self.board[nr][nc]
                if not target or target.owner != piece.owner:
                    moves.append((nr, nc))
        return moves

    def on_click(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if not self.in_bounds(r, c):
            return
        if self.selected:
            if self.selected[0] == 'hand':
                index = self.selected[1]
                piece = self.hands[self.turn][index]
                if self.board[r][c] is None:
                    self.board[r][c] = Piece(piece.name, self.turn)
                    del self.hands[self.turn][index]
                    self.end_turn()
                self.selected = None
            else:
                sr, sc = self.selected
                piece = self.board[sr][sc]
                if piece and piece.owner == self.turn:
                    if (r, c) in self.legal_moves(sr, sc, piece):
                        captured = self.board[r][c]
                        self.board[r][c] = piece
                        self.board[sr][sc] = None
                        if captured:
                            captured.owner = self.turn
                            captured.promoted = False
                            self.hands[self.turn].append(captured)
                            if captured.name == 'lion':
                                messagebox.showinfo('Game Over', f'Player {self.turn+1} wins!')
                                self.window.destroy()
                                return
                        if piece.name == 'chick' and not piece.promoted:
                            if (piece.owner == 0 and r == 0) or (piece.owner == 1 and r == ROWS - 1):
                                piece.promoted = True
                        self.end_turn()
                self.selected = None
        else:
            piece = self.board[r][c]
            if piece and piece.owner == self.turn:
                self.selected = (r, c)
        self.draw()

    def end_turn(self):
        self.turn = 1 - self.turn
        self.draw()
        if self.turn == 1:
            self.window.after(500, self.ai_move)

    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    Game().run()
