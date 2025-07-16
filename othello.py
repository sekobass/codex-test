diff --git a//dev/null b/othello.py
index 0000000000000000000000000000000000000000..409a21f7bb303446a4e119b417cc46b3a0271cc0 100644
--- a//dev/null
+++ b/othello.py
@@ -0,0 +1,119 @@
+class Othello:
+    SIZE = 8
+
+    def __init__(self):
+        self.board = [["." for _ in range(self.SIZE)] for _ in range(self.SIZE)]
+        mid = self.SIZE // 2
+        # Initial four stones
+        self.board[mid-1][mid-1] = 'W'
+        self.board[mid-1][mid] = 'B'
+        self.board[mid][mid-1] = 'B'
+        self.board[mid][mid] = 'W'
+        self.current = 'B'
+
+    @staticmethod
+    def inside(x, y):
+        return 0 <= x < Othello.SIZE and 0 <= y < Othello.SIZE
+
+    def valid_moves(self, player=None):
+        if player is None:
+            player = self.current
+        opponent = 'W' if player == 'B' else 'B'
+        moves = []
+        for x in range(self.SIZE):
+            for y in range(self.SIZE):
+                if self.board[x][y] != '.':
+                    continue
+                if self._would_flip(x, y, player, opponent):
+                    moves.append((x, y))
+        return moves
+
+    def _would_flip(self, x, y, player, opponent):
+        directions = [(-1, -1), (-1, 0), (-1, 1),
+                      (0, -1),         (0, 1),
+                      (1, -1),  (1, 0),  (1, 1)]
+        for dx, dy in directions:
+            nx, ny = x + dx, y + dy
+            has_opponent_between = False
+            while self.inside(nx, ny) and self.board[nx][ny] == opponent:
+                nx += dx
+                ny += dy
+                has_opponent_between = True
+            if has_opponent_between and self.inside(nx, ny) and self.board[nx][ny] == player:
+                return True
+        return False
+
+    def apply_move(self, x, y, player=None):
+        if player is None:
+            player = self.current
+        if (x, y) not in self.valid_moves(player):
+            raise ValueError("Invalid move")
+        opponent = 'W' if player == 'B' else 'B'
+        self.board[x][y] = player
+        directions = [(-1, -1), (-1, 0), (-1, 1),
+                      (0, -1),         (0, 1),
+                      (1, -1),  (1, 0),  (1, 1)]
+        for dx, dy in directions:
+            nx, ny = x + dx, y + dy
+            cells_to_flip = []
+            while self.inside(nx, ny) and self.board[nx][ny] == opponent:
+                cells_to_flip.append((nx, ny))
+                nx += dx
+                ny += dy
+            if cells_to_flip and self.inside(nx, ny) and self.board[nx][ny] == player:
+                for cx, cy in cells_to_flip:
+                    self.board[cx][cy] = player
+        self.current = opponent
+
+    def is_game_over(self):
+        if self.valid_moves('B') or self.valid_moves('W'):
+            return False
+        return True
+
+    def count(self):
+        b = sum(row.count('B') for row in self.board)
+        w = sum(row.count('W') for row in self.board)
+        return {'B': b, 'W': w}
+
+    def display(self):
+        print("  " + " ".join(str(i) for i in range(self.SIZE)))
+        for i, row in enumerate(self.board):
+            print(str(i) + " " + " ".join(row))
+
+
+def main():
+    game = Othello()
+    while not game.is_game_over():
+        game.display()
+        moves = game.valid_moves()
+        if not moves:
+            print(f"{game.current} has no valid moves. Passing.")
+            game.current = 'W' if game.current == 'B' else 'B'
+            continue
+        print(f"Current player: {game.current}")
+        print("Valid moves:", moves)
+        try:
+            raw = input("Enter move as 'row col': ")
+        except EOFError:
+            break
+        if raw.lower() in ['q', 'quit', 'exit']:
+            print("Quitting game.")
+            return
+        try:
+            x, y = map(int, raw.split())
+            game.apply_move(x, y)
+        except Exception as e:
+            print("Invalid input:", e)
+    game.display()
+    counts = game.count()
+    print("Game over! Score: B={B}, W={W}".format(**counts))
+    if counts['B'] > counts['W']:
+        print("Black wins!")
+    elif counts['B'] < counts['W']:
+        print("White wins!")
+    else:
+        print("It's a draw!")
+
+
+if __name__ == '__main__':
+    main()
