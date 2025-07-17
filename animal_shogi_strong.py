# coding: utf-8

import tkinter as tk
from tkinter import messagebox

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
        self.window.title('Animal Shogi (Strong AI)')
        # extra space at the bottom for player's hand
        self.hand_size = CELL_SIZE // 2
        height = ROWS * CELL_SIZE + self.hand_size
        # create the drawing canvas before calling pack
        self.canvas = tk.Canvas(self.window, width=COLS * CELL_SIZE, height=height)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_click)
        self.setup_board()
        self.draw()

    def ai_move(self):
        if self.turn != 1:
            return

        def piece_value(p: Piece) -> int:
            if p.name == 'lion':
                return 1000
            if p.name in ('elephant', 'giraffe'):
                return 5
            if p.name == 'chick':
                return 3 if p.promoted else 1
            return 0

        def evaluate(board, hands):
            lion0 = False
            lion1 = False
            total = 0
            for r in range(ROWS):
                for c in range(COLS):
                    p = board[r][c]
                    if p:
                        if p.name == 'lion':
                            if p.owner == 0:
                                lion0 = True
                            else:
                                lion1 = True
                        val = piece_value(p)
                        pos_bonus = 0
                        if p.name == 'chick' and not p.promoted:
                            pos_bonus = (ROWS - r) if p.owner == 0 else (r + 1)
                        val += pos_bonus
                        total += val if p.owner == 1 else -val
            if not lion0:
                return float('inf')
            if not lion1:
                return float('-inf')
            for owner, pieces in hands.items():
                for p in pieces:
                    val = piece_value(p)
                    pos_bonus = 0
                    if p.name == 'chick' and not p.promoted:
                        pos_bonus = ROWS if owner == 0 else 1
                    val += pos_bonus
                    total += val if owner == 1 else -val
            return total

        def clone_board(board):
            return [[Piece(p.name, p.owner, p.promoted) if p else None for p in row] for row in board]

        def clone_hands(hands):
            return {0: [Piece(p.name, p.owner, p.promoted) for p in hands[0]],
                    1: [Piece(p.name, p.owner, p.promoted) for p in hands[1]]}

        def legal_moves_board(board, r, c, piece):
            moves = []
            for dr, dc in piece.moves():
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    target = board[nr][nc]
                    if not target or target.owner != piece.owner:
                        moves.append((nr, nc))
            return moves

        def generate_moves(board, hands, player):
            moves = []
            for r in range(ROWS):
                for c in range(COLS):
                    piece = board[r][c]
                    if piece and piece.owner == player:
                        for nr, nc in legal_moves_board(board, r, c, piece):
                            moves.append(("move", r, c, nr, nc))
            for idx, piece in enumerate(hands[player]):
                for r in range(ROWS):
                    for c in range(COLS):
                        if board[r][c] is None:
                            moves.append(("drop", idx, r, c))
            return moves

        def apply_move(board, hands, move, player):
            if move[0] == "move":
                _, sr, sc, r, c = move
                piece = board[sr][sc]
                board[sr][sc] = None
                target = board[r][c]
                if target:
                    target.owner = player
                    target.promoted = False
                    hands[player].append(target)
                board[r][c] = Piece(piece.name, player, piece.promoted)
                if piece.name == 'chick' and not piece.promoted:
                    if (player == 0 and r == 0) or (player == 1 and r == ROWS - 1):
                        board[r][c].promoted = True
            else:
                _, idx, r, c = move
                piece = hands[player][idx]
                board[r][c] = Piece(piece.name, player, piece.promoted)
                del hands[player][idx]
            return board, hands

        def minimax(board, hands, depth, player, alpha, beta):
            if depth == 0:
                return evaluate(board, hands), None
            moves = generate_moves(board, hands, player)
            if not moves:
                return evaluate(board, hands), None
            if player == 1:
                best = float('-inf')
                best_move = None
                for mv in moves:
                    nb, nh = apply_move(clone_board(board), clone_hands(hands), mv, player)
                    score, _ = minimax(nb, nh, depth - 1, 0, alpha, beta)
                    if score > best:
                        best = score
                        best_move = mv
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
                return best, best_move
            else:
                best = float('inf')
                best_move = None
                for mv in moves:
                    nb, nh = apply_move(clone_board(board), clone_hands(hands), mv, player)
                    score, _ = minimax(nb, nh, depth - 1, 1, alpha, beta)
                    if score < best:
                        best = score
                        best_move = mv
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
                return best, best_move

        _, choice = minimax(clone_board(self.board), clone_hands(self.hands), 3, 1, float('-inf'), float('inf'))
        if choice is None:
            self.end_turn()
            return

        if choice[0] == "move":
            _, sr, sc, r, c = choice
            piece = self.board[sr][sc]
            target = self.board[r][c]
            self.board[r][c] = piece
            self.board[sr][sc] = None
            if target:
                target.owner = 1
                target.promoted = False
                self.hands[1].append(target)
                if target.name == 'lion':
                    messagebox.showinfo('Game Over', 'Computer wins!')
                    self.window.destroy()
                    return
            if piece.name == 'chick' and not piece.promoted and r == ROWS - 1:
                piece.promoted = True
        else:
            _, idx, r, c = choice
            piece = self.hands[1][idx]
            self.board[r][c] = Piece(piece.name, 1, piece.promoted)
            del self.hands[1][idx]

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
        # draw player's captured pieces at the bottom
        for i, piece in enumerate(self.hands[0]):
            x = i * self.hand_size + self.hand_size/2
            y = ROWS * CELL_SIZE + self.hand_size/2
            self.canvas.create_text(x, y, text=piece.display, font=('Arial', 20))

        if self.selected:
            if self.selected[0] == 'hand':
                i = self.selected[1]
                x1 = i * self.hand_size
                y1 = ROWS * CELL_SIZE
                x2 = x1 + self.hand_size
                y2 = y1 + self.hand_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=3)
            else:
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
        if self.turn != 0:
            return
        if event.y >= ROWS * CELL_SIZE:
            index = event.x // self.hand_size
            if index < len(self.hands[self.turn]):
                self.selected = ('hand', index)
                self.draw()
            return
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
                        target = self.board[r][c]
                        if target and target.owner == self.turn:
                            # do not allow capturing own piece
                            self.selected = None
                            self.draw()
                            return
                        self.board[r][c] = piece
                        self.board[sr][sc] = None
                        if target:
                            target.owner = self.turn
                            target.promoted = False
                            self.hands[self.turn].append(target)
                            if target.name == 'lion':
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
