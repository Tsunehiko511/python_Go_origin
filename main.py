# -*- coding:utf-8 -*-
import random

# データ
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11

# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
STONE = ("・","🔴 ","⚪️ ")

# 碁盤描画
def draw(board):
	print " "," ".join("%2d"%x for x in range(1,BOARD_SIZE+1))
	for y in range(1,BOARD_SIZE+1):
		print "%2d"%y, " ".join(STONE[data] for data in board[y][1:-1])

#石を打つ
def move(board,z,color):
	board[z[0]][z[1]] = color

# 盤上の空の場所を配列で取得
def getNonePosition(board):
	array = []
	for y in range(1,BOARD_SIZE+1):
		for x in range(1,BOARD_SIZE+1):
			if board[y][x] == NONE:
				array.append([y,x])
	return array

def main():
	# 碁盤
	board = [[NONE]*WIDTH_SIZE for i in range(WIDTH_SIZE)]
	# 枠の作成
	for i in range(WIDTH_SIZE):
		board[0][i] = board[-1][i] = board[i][0] = board[i][-1] = WALL
	# 先手
	color = BLACK

	# ゲーム開始
	while(1):
		# 候補を探す
		preMove = getNonePosition(board)
		l = len(preMove)
		if l == 0:
			break
		z = preMove[random.randint(0,l-1)]	# ランダム打ち
		
		move(board,z,color)		# 打つ
		print STONE[color],z	# 描画
		draw(board)
		color = 3 - color		# 色を交代

if __name__ == '__main__':
	main()