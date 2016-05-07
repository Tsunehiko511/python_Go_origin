# -*- coding:utf-8 -*-
import random
import time
import copy
# 碁盤
BOARD_SIZE = 9				# 碁盤の大きさ

KOMI = 6.5

# 盤上の種類
SPACE,BLACK,WHITE,WALL = 0,1,2,3
VISUAL = ("・","🔴 ","⚪️ ", "　")
DIR4 = (-1,0),(1,0),(0,-1),(0,1)
# 石を打ったときの処理
SUCCESS = 0 		# 打てる
KILL 	= 1 		# 自殺手
KO 		= 2 		# 劫
ME 		= 3 		# 眼
MISS 	= 4 		# すでに石がある
PASS 	= 5 		# パス

# 戦略
RANDOM = 1


ERROR_MESSAGE = {KILL:	"自殺手",
				 KO: 	"劫",
				 ME:	"眼",
				 MISS:	"すでに石がある",
				 PASS:	"パス",
				 }

# 碁盤　
class Board(object):
	# 碁盤作成
	def __init__(self,size):
		self.size = size + 2 	# 上下左右に外枠を含めた碁盤
		self.data = data = [[SPACE]*self.size for i in range(self.size)]
		# 外枠の作成
		for i in range(self.size):
			data[0][i] = data[-1][i] = data[i][0] = data[i][-1] = WALL
		# 直前に取った劫の位置
		self.ko = None

	def get(self,position):
		y,x = position
		return self.data[y][x]

	def set(self,position,stone):
		y,x = position
		self.data[y][x] = stone
	# 石を取り除く
	def remove(self,position):
		self.set(position,SPACE)

	# 碁盤描画
	def draw(self):
		print "  ", " ".join("%2d"%x for x in range(1,self.size-1))
		for y in range(1,self.size-1):
			print "%2d"%y, " ".join(VISUAL[data] for data in self.data[y][1:-1])

class JoinedLibertyCounter(object):
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
			if self.board.get(adjacent) == SPACE:
				checked.append(adjacent)
				liberty+=1
			elif self.board.get(adjacent) == stone:
				joined, liberty = self.count_sub(adjacent,stone,checked,joined,liberty)
		return joined, liberty

class Player(object):

	def __init__(self,color):
		self.color = color
		self.un_color = WHITE if color == BLACK else BLACK

	# 戦術を選択
	def tactics(self,choice,positions):
		if choice == RANDOM:
			return random.choice(positions)


	# 相手の石を取る
	def capture(self,board, position):
		board.remove(position)
		y,x = position
		for dy,dx in DIR4:
			around = (y+dy,x+dx)
			if board.get(around) == self.un_color:
				self.capture(board,around)
	# 石を打つ
	def move(self,board,position):
		# すでに石がある場合
		if board.get(position) != SPACE:
			return MISS

		# positionに対して4方向の[連石の数，呼吸点の数，色]
		joineds	 = [0]*4
		libertys = [0]*4
		colors 	 = [0]*4

		space = 0 		# 4方向の空白の数
		wall  = 0 		# 4方向の壁の数
		mikata_safe = 0 # 呼吸点が2以上の味方の数
		take_sum = 0 	# 取れる石の合計
		ko = None 		# 劫の候補

		# 打つ前に4方向を調べる
		joined_liberty = JoinedLibertyCounter(board)
		y,x = position
		for i, (dy,dx) in enumerate(DIR4): 	# enumerate:インデックスとともにループ
			around = (y+dy,x+dx)
			colors[i] = c = board.get(around)
			if c == SPACE:
				space += 1
				continue
			if c == WALL:
				wall += 1
				continue

			# 連石と呼吸点の数を数える
			joineds[i],libertys[i] = joined_liberty.count(around,c)
			# 相手の石が取れるなら，劫の可能性があるので保持
			if c == self.un_color and libertys[i] == 1:
				take_sum += joineds[i]
				ko = around
			# 味方の石があって呼吸点が2つ以上あるなら眼の可能性
			if c == self.color and libertys[i] >= 2:
				mikata_safe += 1

		# ルール違反の処理
		# 敵の石に４方を囲まれている
		if take_sum == 0 and space == 0 and mikata_safe == 0:
			return KILL
		# 劫
		if position == board.ko:
			return KO
		# 眼には置かない (ルール違反ではない)
		if wall + mikata_safe == 4:
			return ME

		# 石を取る
		for i, (dy,dx) in enumerate(DIR4):
			if colors[i] == self.un_color and libertys[i] == 1:
				self.capture(board,(y+dy,x+dx))

		# 石を打つ
		board.set(position,self.color)

		# 劫を取った直後は相手が取り返せないようにする
		joined,liberty = joined_liberty.count(position,self.color)
		if take_sum == 1 and joined == 1 and liberty == 1:
			board.ko = ko 		# 碁盤に劫の目印をつけておく
		else:
			board.ko = None 	# 劫の目印を消す

		return SUCCESS

	# 置ける場所を配列で取得
	def getSuccessPositions(self,board):
		# 石を置ける場所を探すために，deepcopyした碁盤に石を置いて確認する
		return [(y,x)
				for y in xrange(1,board.size-1)
				for x in xrange(1,board.size-1)
				if board.get((y,x)) == SPACE
				and self.move(copy.deepcopy(board),(y,x)) == SUCCESS
				]


# 終局のスコアを計算 1:黒の勝ち -1:白勝ち　　AIは空点があれば打つので空点の4方向を調べればよい
def score_counter(turn_color,board):
	score = 0
	# 盤上の[空点,黒石，白石]の数を取得
	kind = [0,0,0]
	for y in xrange(1,BOARD_SIZE+1):
		for x in xrange(1,BOARD_SIZE+1):
			col = board.data[y][x]
			kind[col] += 1
			# 空点は4方向の石の種類を調べる
			if col != SPACE:
				continue
			# mk[0] 空，[1] 黒，[2] 白，[3] 盤外
			mk = [0]*4
			for (dy,dx) in DIR4:
				mk[board.data[y+dy][x+dx]]+=1
			# 黒だけに囲まれていれば黒地
			if mk[1] > 0 and mk[2] == 0:
				score += 1
			# 白だけに囲まれていれば白地
			if mk[2] > 0 and mk[1] == 0:
				score -= 1
	# 地+盤上の石数
	score += kind[1] - kind[2]

	# コミを考慮した結果
	final_score = score - KOMI
	win = 0
	# turn_colorが黒で黒が勝っていれば1　負けていれば0
	if final_score > 0 :
		win = 1
	# turn_colorが白で白が勝っていれば0　負けていれば-1
	if turn_color == WHITE:
		win = -1
	return win

def judge(score):
	if score == 1:
		print VISUAL[BLACK],"勝ち"
	else:
		print VISUAL[WHITE],"勝ち"


def main():
	# 碁盤
	board = Board(BOARD_SIZE)

	# プレイヤー
	black = Player(BLACK)
	white = Player(WHITE)
	turn  = {black:white, white:black}

	# 先手
	player = black

	# 対局開始
	passed = 0
	while passed < 2:
		positions = player.getSuccessPositions(board)

		if len(positions) == 0:
			retult = PASS
			passed += 1
		else:
			position = player.tactics(RANDOM,positions)
			retult = player.move(board,position)
			passed = 0

		if retult == SUCCESS:
			print VISUAL[player.color],position
			board.draw()
			print
		else:
			print VISUAL[player.color],ERROR_MESSAGE[retult]

		# プレイヤー交代
		player = turn[player]
		time.sleep(0.1)
	print "対局終了"
	judge(score_counter(BLACK,board))

if __name__ == '__main__':
	main()