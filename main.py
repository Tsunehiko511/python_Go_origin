# -*- coding:utf-8 -*-
# データ構造
KOMI = 6.5
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11

# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
STONE = ("・","🔴 ","⚪️ ")

PASS = 0
# 碁盤
board = [[NONE]*WIDTH_SIZE for i in range(WIDTH_SIZE)]

# 枠の作成
for i in range(WIDTH_SIZE):
	board[0][i] = board[-1][i] = board[i][0] = board[-1][i] = WALL

def print_board():
	print " "," ".join("%2d"%x for x in range(1,BOARD_SIZE+1))
	for y in range(1,BOARD_SIZE+1):
		print "%2d"%y, " ".join(STONE[data] for data in board[y][1:-1])

board[2][5] = WHITE
board[3][8] = BLACK
print_board()