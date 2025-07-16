class Othello:
    SIZE = 8

    def __init__(self):
        self.board = [["." for _ in range(self.SIZE)] for _ in range(self.SIZE)]
        mid = self.SIZE // 2
        self.board[mid-1][mid-1] = 'W'
        self.board[mid][mid] = 'W'
        self.board[mid-1][mid] = 'B'
        self.board[mid][mid-1] = 'B'
        self.current = 'B'

    def print_board(self):
        for row in self.board:
            print(" ".join(row))

def main():
    game = Othello()
    print("初期盤面：")
    game.print_board()

if __name__ == "__main__":
    main()
