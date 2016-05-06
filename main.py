# -*- coding:utf-8 -*-
import random
import time
import copy
# データ
KOMI = 6.5
BOARD_SIZE = 9				# 碁盤の大きさ
WIDTH_SIZE = BOARD_SIZE + 2 # 盤外を含めた碁盤の横幅 11
BOARD_MAX  = WIDTH_SIZE * WIDTH_SIZE # 121
# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
STONE = ["・","🔴 ","⚪️ "]
# 石が打てたかどうか
SUCCESS = 0 		# 打てる
KILL 	= 1 		# 自殺手
KO 		= 2 		# 劫
ME 		= 3 		# 眼
MISS 	= 4 		# すでに石がある
PASS 	= 5 		# パス

DIR4 = [-1,1,-WIDTH_SIZE,+WIDTH_SIZE]

# (x,y)を１次元配列表記に変換 ただしx,y:0〜8
def get_z(x,y):
	return (x+1) + (y+1)*WIDTH_SIZE
def get_y_x(z):
	return [z/WIDTH_SIZE,z%WIDTH_SIZE]
# 色の反転
def flip_color(color):
	return 3 - color

class Joined_Liberty(object):

	def __init__(self,board):
		self.board = board

	# position周辺の連石と呼吸点を取得
	def count(self,position,stone):
		return self.count_sub(position,stone,[])

	def count_sub(self,position,stone,checked, joined=0,liberty=0):
		checked.append(position)
		joined += 1
		for d in DIR4:
			adjacent = position + d
			if adjacent in checked:
				continue
			if self.board.data[adjacent] == NONE:
				checked.append(adjacent)
				liberty += 1
			elif self.board.data[adjacent] == stone:
				joined, liberty = self.count_sub(adjacent,stone,checked,joined,liberty)
		return joined,liberty

# デバック用
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



class Board(object):
	# 基盤作成
	def __init__(self,size):
		self.size = size + 2
		self.data = data = [NONE for i in range(0,BOARD_MAX)]
		# 外枠の作成
		for i in range(0,WIDTH_SIZE):
			data[i] = WALL
			data[BOARD_MAX - WIDTH_SIZE + i] = WALL
		for i in range(1,WIDTH_SIZE):
			data[i*WIDTH_SIZE] = WALL
			data[i*WIDTH_SIZE+BOARD_SIZE+1] = WALL

	# 石を取る
	def capture(self,z,color):
		self.data[z] = NONE
		for d in DIR4:
			around = z + d
			if self.data[around] == color:
				self.capture(around,color)


	# 碁盤に石を打つ
	def move(self,position,color,ko_z):
		joined_liberty = Joined_Liberty(self)
		if position == PASS:
			return PASS
		if self.data[position] != NONE: # 石がある
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
			c = self.data[z]
			if c == NONE:
				space+=1
			if c == WALL:
				wall+=1
			if c==NONE or c==WALL:
				continue

			(joined1,liberty1) = joined_liberty.count(z,c)
			around[i][0] = liberty1
			around[i][1] = joined1
			around[i][2] = c

			# 石が取れるなら，劫の可能性があるので保持
			if(c==un_color) and (liberty1==1):
				take_sum += joined1
				pre_ko = z
			# 味方の石があって呼吸点が２つ以上あるなら眼の可能性
			if(c==color) and (liberty1>=2):
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
			liberty2 = around[i][0]
			chain = around[i][1]
			col = around[i][2]
			tz = position+DIR4[i]
			if (col == un_color) and (liberty2==1) and (self.data[tz]!=NONE):
				self.capture(tz,un_color)

		# 石を打つ
		self.data[position] = color
		(joined,liberty) = joined_liberty.count(position,color)
		if(take_sum==1) and (joined==1) and (liberty==1):
			ko_z[0] = pre_ko
		else:
			ko_z[0] = 0
		
		return SUCCESS


	# 違反とならない場所の配列を取得
	def getSuccessPosition(self,ko_z,color):
		array = []
		# 碁盤と劫をコピーし，違反とならない手を配列に入れていく
		board_copy = copy.deepcopy(self.data)
		for i in range(BOARD_MAX):
			ko_z_copy = ko_z[:]
			err = self.move(i,color,ko_z_copy)
			if err != SUCCESS:
				continue
			array.append(i)
			self.data = copy.deepcopy(board_copy)
		return array

	# 盤上の描画
	def draw(self):
		print " ",
		for x in range(1,BOARD_SIZE+1):
			print "%d " %x,
		print ""
		for y in range(0,BOARD_SIZE):
			print y+1,
			for x in range(0,BOARD_SIZE):
				print STONE[self.data[get_z(x,y)]],
			print ""
def main():
	board = Board(BOARD_SIZE)

	color = BLACK
	ko_z = [0] 			# 劫
	count_pass = 0

	# 対局開始
	while(1):
		# 順番に打っていき　反則じゃないものを取得
		positions = board.getSuccessPosition(ko_z,color)

		if len(positions) == 0:
			z = PASS
		else:
			count_pass = 0
			z = random.choice(positions) #　nonePosition[random.randint(0,l-1)]

		# 実際に打ってみる　　(人が打つ場合も想定しているので処理に重複がある)
		err = board.move(z,color,ko_z)
		if err != SUCCESS:
			print STONE[color],
			error_move(err)
			if err==PASS:
				color = flip_color(color)
				count_pass +=1
			if count_pass == 2:
				print "対局終了"
				break
			# エラーの手を配列から削除
			continue
		print STONE[color],get_y_x(z),"に打つ"
		board.draw()						# 盤上の描画
		# 交代
		color = flip_color(color)
		print ""
		time.sleep(0)

if __name__ == '__main__':
	main()








