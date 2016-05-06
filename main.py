# -*- coding:utf-8 -*-
import random
import time
import copy
# 碁盤
BOARD_SIZE = 9				# 碁盤の大きさ

# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
VISUAL = ("・","🔴 ","⚪️ ", "　")
DIR4 = (-1,0),(1,0),(0,-1),(0,1)

SUCCESS = 0 		# 打てる
KILL 	= 1 		# 自殺手
KO 		= 2 		# 劫
ME 		= 3 		# 眼
MISS 	= 4 		# すでに石がある
PASS 	= 5 		# パス


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

class Count_Joined_Liberty(object):

	def __init__(self,board):
		self.board = board

	def count(self,position,stone):
		return self.count_sub(position,stone,[])

	def  count_sub(self,position,stone,checked,joined=0,liberty=0):
		checked.append(position)
		joined += 1
		y,x = position
		for dy,dx in DIR4:
			adjacent = (y+dy,x+dx)
			if adjacent in checked:
				continue
			if self.board.get(adjacent) == NONE:
				checked.append(adjacent)
				liberty+=1
			elif self.board.get(adjacent) == stone:
				joined, liberty = self.count_sub(adjacent,stone,checked,joined,liberty)
		return joined, liberty


class Board(object):
	# 碁盤作成
	def __init__(self,size):
		self.size = size + 2 	# 上下左右に外枠を含めた碁盤
		self.data = data = [[NONE]*self.size for i in range(self.size)]
		# 外枠の作成
		for i in range(self.size):
			data[0][i] = data[-1][i] = data[i][0] = data[i][-1] = WALL

	# 石を取る
	def capture(self,position,color):
		y,x = position
		self.data[y][x] = NONE
		for dy,dx in DIR4:
			around = (y+dy,x+dx)
			if self.get(around) == color:
				self.capture(around,color)

	def get(self,position):
		y,x = position
		return self.data[y][x]

	# 石を打つ
	def move(self,position,color,ko_z):
		joined_liberty = Count_Joined_Liberty(self)
		if position == PASS:
			return PASS
		if self.get(position) != NONE:
			return MISS

		# positionに対して4方向の　[呼吸点の数，連石の数，色]
		libertys = [0,0,0,0]
		joineds  = [0,0,0,0]
		colors   = [0,0,0,0]

		un_color = 3- color
		space = 0 			# 4方向の空白の数
		wall = 0 			# 4方向の壁の数
		mikata_safe = 0 	# 呼吸点が2以上の味方の数
		take_sum = 0 		# 取れる石の合計
		pre_ko = 0 			# 劫の候補 ※シャレじゃない

		# 打つ前に4方向を調べる
		y,x = position
		for i in range(4):
			(dy,dx) = DIR4[i]
			z = (y+dy,x+dx) 
			c = self.get(z)
			if c == NONE:
				space+=1
			if c == WALL:
				wall+=1
			if c==NONE or c==WALL:
				continue

			joineds[i],libertys[i] = joined_liberty.count(z,c)
			colors[i] = c

			# 石が取れるなら，劫の可能性があるので保持
			if(c==un_color) and (libertys[i]==1):
				take_sum += joineds[i]
				pre_ko = z
			# 味方の石があって呼吸点が２つ以上あるなら眼の可能性
			if(c==color) and (libertys[i]>=2):
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
			(dy,dx) = DIR4[i]
			tz = (y+dy,x+dx)
			if (colors[i] == un_color) and (libertys[i]==1) and (self.get(tz)!=NONE):
				self.capture(tz,un_color)

		# 石を打つ
		self.data[y][x] = color
		joined,liberty = joined_liberty.count(position,color)
		if(take_sum==1) and (joined==1) and (liberty==1):
			ko_z[0] = pre_ko
		else:
			ko_z[0] = 0
		
		return SUCCESS

	# 盤上の空の場所を配列で取得
	def getSuccessPositions(self,ko_z,color):
		array = []
		board_copy = copy.deepcopy(self.data)
		for y in range(1,self.size-1):
			for x in xrange(1,self.size-1):
				ko_z_copy = ko_z[:]
				err = self.move((y,x),color,ko_z_copy)
				if err != SUCCESS:
					continue
				array.append((y,x))
				self.data = copy.deepcopy(board_copy)
		return array

	# 碁盤描画
	def draw(self):
		print "  ", " ".join("%2d"%x for x in range(1,self.size-1))
		for y in range(1,self.size-1):
			print "%2d"%y, " ".join(VISUAL[data] for data in self.data[y][1:-1])

def main():
	# 碁盤
	board = Board(BOARD_SIZE)

	# 先手
	color = BLACK
	ko_z = [0]
	count_pass = 0

	# 対局開始
	while(1):
		positions = board.getSuccessPositions(ko_z,color)

		if len(positions) == 0:
			z = PASS
		else:
			count_pass = 0
			z = random.choice(positions)
		print z
		err = board.move(z,color,ko_z)
		print err
		if err != SUCCESS:
			print VISUAL[color],
			error_move(err)
			if err == PASS:
				color = 3-color
				count_pass+=1
			if count_pass == 2:
				print "対局終了"
				break
			continue
		print VISUAL[color], z
		board.draw()
		color = WHITE if color == BLACK else BLACK
		time.sleep(0.1)
		print ""

if __name__ == '__main__':
	main()