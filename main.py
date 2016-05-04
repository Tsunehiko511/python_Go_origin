# -*- coding:utf-8 -*-
# データ構造
BOARD_SIZE = 9             # 碁盤の大きさ
DATA_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11

# 盤上データ
NONE, BLACK, WHITE, WALL = 0, 1, 2, 3    # WALLは盤外

# 碁盤
board = [[NONE] * DATA_SIZE for i in range(DATA_SIZE)]
# 周囲を盤外にする
for i in range(DATA_SIZE):
    board[0][i] = board[-1][i] = board[i][0] = board[i][-1] = WALL

print board

STONE = ("・", "● ", "○ ")
def print_board():
    print "  ", " ".join("%2d"%x for x in range(1,BOARD_SIZE+1))
    for y in range(1,BOARD_SIZE+1):
        print "%2d"%y, " ".join(STONE[data] for data in board[y][1:-1])

# 表示テストのため石を置いて表示してみる
board[2][5] = WHITE
board[3][8] = BLACK
print_board()