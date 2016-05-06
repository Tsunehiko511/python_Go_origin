# -*- coding:utf-8 -*-
import random
import time
# データ
KOMI = 6.5
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11
BOARD_MAX  = WIDTH_SIZE * WIDTH_SIZE # 121
# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
STONE = ["・","🔴 ","⚪️ "]
# 石が打てたかどうか
SUCCESS = 0
KILL 	= 1
KO 		= 2
ME 		= 3
MISS 	= 4
PASS 	= 5

DIR4 = [-1,1,-WIDTH_SIZE,+WIDTH_SIZE]

# (x,y)を１次元配列表記に変換 ただしx,y:0〜8
def get_z(x,y):
	return (x+1) + (y+1)*WIDTH_SIZE
def get_y_x(z):
	return [z/WIDTH_SIZE,z%WIDTH_SIZE]
# 色の反転
def flip_color(color):
	return 3 - color

# zの連石の数とその呼吸点を取得
def count_stone_liberty(z,board,color):
	stone_liberty = [0,0]
	# 呼吸点　石の数のチェック表
	check_board = [0 for i in range(BOARD_MAX)]
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

def capture(z,board,color):
	board[z] = NONE
	for d in DIR4:
		around = z + d
		if board[around] == color:
			capture(around,board,color)

# 碁盤に石を打つ
def move(board,position,color,ko_z):
	if position == PASS:
		return PASS
	if board[position] != NONE: # 石がある
		return MISS

	# positionに対して4方向の　[呼吸点の数，連石の数，色]
	around = [
			[0,0,0],		# 左
			[0,0,0],		# 右
			[0,0,0],		# 下
			[0,0,0]			# 上
			]
	un_color = flip_color(color)

	space = 0 			# 4方向の空白の数
	wall = 0 			# 4方向の壁の数
	mikata_safe = 0 	# 呼吸点が2以上の味方の数
	take_sum = 0 		# 取れる石の合計
	pre_ko = 0 			# 劫の候補 ※シャレじゃない

	# 打つ前に4方向を調べる
	for i in range(4):
		z = position + DIR4[i]
		c = board[z]
		if c == NONE:
			space+=1
		if c == WALL:
			wall+=1
		if c==NONE or c==WALL:
			continue

		stone_liberty = count_stone_liberty(z,board,c)
		around[i][0] = stone_liberty[1]
		around[i][1] = stone_liberty[0]
		around[i][2] = c

		# 石が取れるなら，劫の可能性があるので保持
		if(c==un_color) and (stone_liberty[1]==1):
			take_sum += stone_liberty[0]
			pre_ko = z
		# 味方の石があって呼吸点が２つ以上あるなら眼の可能性
		if(c==color) and (stone_liberty[1]>=2):
			mikata_safe+=1

	# ルール違反の処理
	if(take_sum==0) and (space==0) and (mikata_safe==0):		# 味方の石以外で囲まれていて，石が取れないなら自殺手
		return KILL
	if position == ko_z[0]:	# 劫
		return KO
	if wall + mikata_safe == 4: # 眼 (ルール違反ではない)
		return ME

	# 石を取る処理
	for i in range(4):
		liberty = around[i][0]
		chain = around[i][1]
		col = around[i][2]
		tz = position+DIR4[i]
		if (col == un_color) and (liberty==1) and (board[tz]!=NONE):
			capture(tz,board,un_color)

	# 石を打つ
	board[position] = color

	stone_liberty = count_stone_liberty(position,board,color)
	if(take_sum==1) and (stone_liberty[0]==1) and (stone_liberty[1]==1):
		ko_z[0] = pre_ko
	else:
		ko_z[0] = 0
	
	return SUCCESS

def error_move(err):
	if err == KILL:
		print "自殺手"
	if err == KO:
		print "劫"
	if err == ME:
		print "眼"
	if err == MISS:
		print "すでに石がある"
	if err == PASS:
		print "パス"


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

# 違反とならない場所の配列を取得
def getSuccessPosition(board,ko_z,color):
	array = []

	for i in range(0,BOARD_MAX):
		board_copy = board[:]
		ko_z_copy = ko_z[:]
		err = move(board_copy,i,color,ko_z_copy)
		if err != SUCCESS:
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
	# 劫
	ko_z = [0]

	count_pass = 0

	# 対局開始
	while(1):
		# 空に石を打つ
		nonePosition = getSuccessPosition(board,ko_z,color)

		l = len(nonePosition)
		# 順番に打っていき　反則じゃないものを取得
		if l == 0:
			z = PASS
			count_pass +=1
		else:
			count_pass = 0
			z = nonePosition[random.randint(0,l-1)]
			# print STONE[color],get_y_x(z),"打つ予定"

		err = move(board,z,color,ko_z)
		if err != SUCCESS:
			print STONE[color],
			error_move(err)
			if err==PASS:
				color = flip_color(color)
			if count_pass == 2:
				print "対局終了"
				break
			# エラーの手を配列から削除
			continue
		print STONE[color],get_y_x(z),"に打つ"
		print_board(board)						# 盤上の描画
		# 交代
		color = flip_color(color)
		print ""
		time.sleep(0.1)

if __name__ == '__main__':
	main()








