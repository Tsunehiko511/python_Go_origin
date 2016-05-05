# -*- coding:utf-8 -*-
import random
# データ
KOMI = 6.5
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11
BOARD_MAX  = WIDTH_SIZE * WIDTH_SIZE # 121
# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
STONE = ["・","🔴 ","⚪️ "]
# 石が打てたかどうか
ERROR = -1
SUCCESS = 1

DIR4 = [-1,1,-WIDTH_SIZE,+WIDTH_SIZE]

# (x,y)を１次元配列表記に変換 ただしx,y:0〜8
def get_z(x,y):
	return (x+1) + (y+1)*WIDTH_SIZE
def get_y_x(z):
	return [z/WIDTH_SIZE,z%WIDTH_SIZE]
# 色の反転
def flip_color(color):
	return 3 - color

# zに打った時の連石の数とその呼吸点を取得
def count_stone_liberty(z,board,color,check_board):
	stone_liberty = [0,0]

	for i in range(BOARD_MAX):
		check_board[i] = 0
	count_stone_liberty_sub(z,board,color,check_board,stone_liberty)

	return stone_liberty

def count_stone_liberty_sub(z,board,color,check_board,stone_liberty):
	check_board[z] = 1
	stone_liberty[0] += 1
	for d in DIR4:
		zd = z + d
		if check_board[zd] == 1: # チェック済み
			continue
		if board[zd] == NONE:
			check_board[zd] = 1
			stone_liberty[1] += 1
		if board[zd] == color:
			count_stone_liberty_sub(zd,board,color,check_board,stone_liberty) 

# 碁盤に石を打つ
def move(board,position,color):
	# 空でなけれエラーを返す
	if board[position] != NONE:
		return ERROR
	# 石を打つ
	board[position] = color
	return SUCCESS

# 盤上の描画
def print_board(board):
	print " ",
	for x in range(1,BOARD_SIZE+1):
		print "%d " %x,
	print ""
	for y in range(0,BOARD_SIZE):
		print y+1,
		for x in range(0,BOARD_SIZE):
			print STONE[board[get_z(x,y)]],
		print ""

# 空の場所の配列を取得
def getNonePosition(board):
	array = []
	for i in range(0,BOARD_MAX):
		if board[i] != NONE:
			continue
		array.append(i)
	return array

def main():
	# 碁盤
	board = [0 for i in range(0,BOARD_MAX)]
	# 盤外の作成
	for i in range(0,WIDTH_SIZE):
		board[i] = WALL
		board[BOARD_MAX - WIDTH_SIZE + i] = WALL
	for i in range(1,WIDTH_SIZE):
		board[i*WIDTH_SIZE] = WALL
		board[i*WIDTH_SIZE+BOARD_SIZE+1] = WALL

	# 先手を黒
	color = 1

	# 呼吸点　石の数のチェック表
	check_board = [0 for i in range(BOARD_MAX)]

	# 試合開始
	while(1):
		# 空に石を打つ
		nonePosition = getNonePosition(board)
		l = len(nonePosition)
		if l == 0:
			break
		z = nonePosition[random.randint(0,l-1)]
		print STONE[color],get_y_x(z)
		print STONE[color],"[連石,呼吸点] = ",count_stone_liberty(z,board,color,check_board)
		'''
		for around in DIR4:
			around = z + around
			count_stone_liberty(z,board,3-color,check_board)
		'''
		move(board,z,color)
		print_board(board)						# 盤上の描画
		# 交代
		color = flip_color(color)
		print ""

if __name__ == '__main__':
	main()








