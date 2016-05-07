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
MONTE_CARLO = 2

ERROR_MESSAGE = {KILL:	"自殺手",
				 KO: 	"劫",
				 ME:	"眼",
				 MISS:	"すでに石がある",
				 PASS:	"パス",
				 }

'''
時間計測テンプレート
start = time.time()
elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time)) + "[sec]"
'''

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

	# 盤上の空の場所を配列で取得
	def getNonePositions(self):
		return [(y, x)
				for y in range(1, self.size-1)
				for x in range(1, self.size-1)
				if self.data[y][x] == SPACE]


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

	def __init__(self,color,tact):
		self.color = color
		self.un_color = WHITE if color == BLACK else BLACK
		self.tact = tact

	# 戦術を選択
	def tactics(self,board,positions):
		if self.tact == RANDOM:
			return random_choice(self,board,positions)
		if self.tact == MONTE_CARLO:
			return monte_carlo(self,board,positions)

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
		if position == (0,0):
			return PASS
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
				#if self.move(copy.deepcopy(board),(y,x)) == SUCCESS
				if board.get((y,x)) == SPACE
				and self.move(copy.deepcopy(board),(y,x)) == SUCCESS
				]
# turn_colorが打つところから終局まで打ち，勝敗を返す
def playout(color,board,positions):
	playout_start = time.time()

	turn_player = Player(color,RANDOM) 					# ターンプレイヤー
	wait_player = Player(turn_player.un_color,RANDOM)	# 待機プレイヤー
	turn  = {turn_player:wait_player, wait_player:turn_player}
	board_copy = copy.deepcopy(board) 					# 試し打ち用ボード
	start1 = time.time()

	# 空点取得　試し打ち候補
	positions_copy = copy.deepcopy(positions) 			
	# 先手
	player = turn_player
	# 対局開始
	passed = 0

	elapsed_time1 = time.time() - start1
	
	# print ("elapsed_time1:{0}".format(elapsed_time1)) + "[sec]"
	start2 = time.time()

	while passed < 2:
		while True:
			# 手がないならパス
			if len(positions_copy) == 0:
				result = PASS
			else:
				# 手があるなら取得する 
				position = random.choice(positions_copy)
				result = player.move(board_copy,position) 		# 石を打つ
			if result == SUCCESS:
				#print VISUAL[player.color],position
				passed = 0
				break
			elif result == PASS:
				#print VISUAL[player.color],ERROR_MESSAGE[result]
				passed += 1
				break
			else:
				positions_copy.remove(position) 			# 候補から外す
				#print VISUAL[player.color],ERROR_MESSAGE[result],position
		elapsed_time2 = time.time() - start2
		#board_copy.draw()
		# プレイヤー交代
		player = turn[player]
	# 終局
	#time.sleep(3)
	# 勝敗を返す
	score = score_counter(turn_player.color,board_copy)
	playout_elapsed_time = time.time() - playout_start
	#print ("playout_elapsed_time:{0}".format(playout_elapsed_time)) + "[sec]"
	#print ("elapsed_time2:{0}".format(elapsed_time2)) + "[sec]"
	# time.sleep(0)
	return score
def random_choice(player,board,positions):
	board_copy = copy.deepcopy(board)
	positions_copy = copy.deepcopy(positions)
	random.shuffle(positions_copy)
	position = (0,0)
	for p in positions_copy:
		result = player.move(board_copy,p) 	# 石を打つ
		if result == SUCCESS: 						# 違反したら次
			position = p
			break
	return position

def monte_carlo(player,board,positions):
	monte_start = time.time()
	playout_count = 0

	TRY_GAMES = 30
	best_value = -999
	board_copy = copy.deepcopy(board)
	positions_copy = copy.deepcopy(positions)

	best_position = (0,0)
	count = 0

	random.shuffle(positions_copy)
	# すべての手に対して1手打ってみる
	for position in positions_copy:
		win_sum = 0
		result = player.move(board_copy,position) 	# 石を打つ
		positions_copy.remove(position) 			# 候補から外す
		if result != SUCCESS: 						# 違反したら次
			continue

		# (相手の手から)playoutをTRY_GAMES回繰り返す
		for i in range(TRY_GAMES):
			win_sum -= playout(player.un_color,board_copy,positions_copy)
			count += 1

		# 勝率が最も高いものを選ぶ
		win_rate = win_sum/TRY_GAMES
		if win_rate > best_value:
			best_value = win_rate
			best_position = position
	
	monte_elapsed_time = time.time() - monte_start
	print count
	print ("monte_elapsed_time:{0}".format(monte_elapsed_time)) + "[sec]"
	#time.sleep(2)
	return best_position


# 終局のスコアを計算 1:黒の勝ち -1:白勝ち　　AIは空点があれば打つので空点の4方向を調べればよい
def score_counter(turn_color,board):
	score = 0
	# 盤上の[空点,黒石，白石]の数を取得
	kind = [0,0,0]
	for y in xrange(1,board.size-1):
		for x in xrange(1,board.size-1):
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
	main_start = time.time()

	# 碁盤
	board = Board(BOARD_SIZE)

	# プレイヤー
	black = Player(BLACK,MONTE_CARLO)
	white = Player(WHITE,RANDOM)
	turn  = {black:white, white:black}

	# 先手
	player = black

	# 対局開始
	passed = 0
	while passed < 2:
		# 盤上の空点を取得	
		positions = board.getNonePositions()
		if len(positions) == 0:		# 打てないならパス
			result = PASS
		elif player == black:
			# 原始モンテカルロで打つ場所を取得
			position = player.tactics(board,positions)
			result = player.move(board,position) 	# 打ってみる
		elif player == white:
			# ランダムに打つ場所を取得
			position = player.tactics(board,positions)
			result = player.move(board,position) 	# 打ってみる

		if result == SUCCESS: 			# 打てたら描画 選択終了
			passed = 0
			print VISUAL[player.color],position
			board.draw()
			print
		elif result == PASS:
			passed += 1
			print VISUAL[player.color],ERROR_MESSAGE[result]
		else: 							# 違反ならもう一度探す
			print VISUAL[player.color],ERROR_MESSAGE[result],position
			player = turn[player]
		# プレイヤー交代
		player = turn[player]
		#time.sleep(0)

	board.draw()
	print "対局終了"	
	judge(score_counter(BLACK,board))

	main_elapsed_time = time.time() - main_start
	print ("main_elapsed_time:{0}".format(main_elapsed_time)) + "[sec]"


if __name__ == '__main__':
	main()