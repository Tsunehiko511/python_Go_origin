# -*- coding:utf-8 -*-
# データ構造
KOMI = 6.5
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11
BOARD_MAX  = WIDTH_SIZE * WIDTH_SIZE # 121

WALL = 3	# 盤外

# 碁盤
'''
board = [
		3,3,3,3,3,3,3,3,3,3,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,2,0,0,0,0,3,
		3,0,0,0,0,0,0,0,1,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,0,0,0,0,0,0,0,0,0,3,
		3,3,3,3,3,3,3,3,3,3,3,
		]
'''
board = [0 for i in range(0,BOARD_MAX)]
# 一行目を盤外にする
for i in range(0,WIDTH_SIZE):
	u_wall = i
	b_wall = BOARD_MAX - WIDTH_SIZE + i
	board[u_wall] = WALL
	board[b_wall] = WALL
for i in range(1,WIDTH_SIZE):
	l_wall = i*WIDTH_SIZE
	r_wall = l_wall+BOARD_SIZE+1
	board[l_wall] = WALL
	board[r_wall] = WALL


dir4 = {-1,1,+WIDTH_SIZE,-WIDTH_SIZE} # 右左上下への移動
hama = [0,0]
kifu = [0 for i in range(0,1000)]
ko_z = 0
all_playouts = 0

# (x,y)を１次元配列表記に変換 ただしx,y:0〜8
def get_z(x,y):
	return (x+1) + (y+1)*WIDTH_SIZE
# 上の逆
def get_x_y(z):
	return (z%WIDTH_SIZE,z/WIDTH_SIZE)

# 一次元配列を(x,y)に変換
def get81(z):
	if z==0:
		return 0
	y = z/WIDTH_SIZE
	x = z- y*WIDTH_SIZE
	return x*10+y

def flip_color(col):
	clo = 3 - col

storn = ["・","🔴 ","⚪️ "]
def print_board():
	print " ",
	for x in range(1,BOARD_SIZE+1):
		print "%d " %x,
	print ""
	for y in range(0,BOARD_SIZE):
		print y+1,
		for x in range(0,BOARD_SIZE):
			print storn[board[get_z(x,y)]],
		print ""

print_board()





