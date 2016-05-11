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
RANDOM_ORIGIN = 3

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

# (y,x) の周辺４方向の座標を返す
def neighbors((y,x)):
	return (y-1,x), (y+1,x), (y,x-1), (y,x+1)

# position周辺の味方の連石とその呼吸点の数を返す　呼吸点=0になれば石が取られる
def count_joined_liberty(board,  position,  color):
	checked = [[False]*board.size for i in board.data]
	def count_around(center, joined=0, liberty=0):
		y, x = center
		checked[y][x] = True
		joined += 1
		for neighbor in neighbors(center):
			y, x = neighbor
			if checked[y][x]:
				continue
			data = board.data[y][x]
			if data == SPACE:
				checked[y][x] = True
				liberty += 1
			elif data == color:
				joined, liberty = count_around(neighbor, joined, liberty)
		return joined, liberty
	return count_around(position)
'''
# 再帰なし
def count_joined_liberty(board, position, color):
    joined = 0
    liberty = 0
    # チェック表を作る
    checked = [[0]*board.size for i in board.data]
    checking = [position]
    pop = checking.pop
    append = checking.append
    # checkingが空になるまで調べる
    while checking:
    	# checkingの要素を取り出す
        y, x = center = checking.pop()
        # 取り出した場所にチェックをつける
        checked[y][x] = 1
        joined += 1
        # 取り出した場所の4方向を調べる
        for neighbor in neighbors(center):
            y, x = neighbor
            # チェック済みなら次
            if checked[y][x] != 0:
                continue
            data = board.data[y][x]
            # 空白ならチェック済みとして呼吸点を+1
            if data == SPACE:
                checked[y][x] = 1
                liberty += 1
            # 同じ色ならcheckリストに加える
            elif data == color:
                append(neighbor)
    return joined, liberty
'''

# 碁盤　
class Board(object):
	# 碁盤作成
	def __init__(self, size):
		self.size = size + 2 	# 上下左右に外枠を含めた碁盤
		self.data = data = [[SPACE]*self.size for i in xrange(self.size)]
		# 外枠の作成
		for i in xrange(self.size):
			data[0][i] = data[-1][i] = data[i][0] = data[i][-1] = WALL
		# 直前に取った劫の位置
		self.ko = None

	def get(self, position):
		y, x = position
		return self.data[y][x]

	def set(self, position, stone):
		y, x = position
		self.data[y][x] = stone
	# 石を取り除く
	def remove(self, position):
		self.set(position, SPACE)

	# 碁盤描画
	def draw(self):
		print "  ", " ".join("%2d"%x for x in xrange(1, self.size-1))
		for y in xrange(1, self.size-1):
			print "%2d"%y, " ".join(VISUAL[data] for data in self.data[y][1:-1])

	# 盤上の空の場所を配列で取得
	def getSpacePositions(self):
		return [(y,x)
				for y in xrange(1, self.size-1)
				for x in xrange(1, self.size-1)
				if self.data[y][x] == SPACE]


# 戦術を選択
def tactics(strategy):
	
	def playout(color, board):

		player1 = Player(color, RANDOM)
		player2 = Player(player1.un_color, RANDOM)
		turn = {player1:player2, player2:player1}
		player = player1
		passed = 0

		while passed < 2:
			result = player.play(board)
			passed = 0 if result == SUCCESS else passed + 1
			player = turn[player]

		return scoring(board)

	# 原始モンテカルロ囲碁
	def monte_carlo(player, board):
		monte_start = time.time()

		TRY_GAMES = 1
		try_total = 0
		best_winner = -1
		best_position = None

		# すべての手に対して１手打ってみる
		thinking_board = None
		spaces = board.getSpacePositions()
		random.shuffle(spaces)
		for i, position in enumerate(spaces):
			if thinking_board == None:
				thinking_board = copy.deepcopy(board)
			result = player.move(thinking_board, position)
			if result != SUCCESS:
				continue
			win_count = 0
			for n in xrange(TRY_GAMES):
				score = playout(player.un_color, copy.deepcopy(thinking_board))

				if score[player.color] > score[player.un_color]:
					win_count += 1

			thinking_board = None
			try_total += TRY_GAMES

			# 勝数が多い高いものを選ぶ
			if win_count > best_winner:
				best_winner = win_count
				best_position = position
		print try_total,
		monte_elapsed_time = time.time() - monte_start
		print ("monte_elapsed_time:{0}".format(monte_elapsed_time)) + "[sec]"
		print try_total/monte_elapsed_time,
		print "playout/sec"

		if best_position:
			player.position = best_position
			return player.move(board, best_position)

		return PASS

	# 違反しない手をランダム選択
	def random_choice(player, board):
		spaces = board.getSpacePositions()
		random.shuffle(spaces)
		for position in spaces:
#		while  len(spaces) > 0:
#			position = random.choice(spaces)
			result = player.move(board, position) # moveは違反場所に打たないので盤面は崩れない

			if result == SUCCESS:
				player.position = position
				return SUCCESS
#			spaces.remove(position)
		return PASS

	if strategy == RANDOM:
		return random_choice
	if strategy == MONTE_CARLO:
		return monte_carlo
	return random_choice


class Player(object):

	def __init__(self, color, strategy):
		self.color = color
		self.un_color = WHITE if color == BLACK else BLACK
		self.tactics = tactics(strategy)

	# selfが戦術に従い今の盤面で１手打った結果を返す
	def play(self, board):
		return self.tactics(self, board)

	# 相手の石を取る
	def capture(self, board,  position):
		board.remove(position)
		for neighbor in neighbors(position):
			if board.get(neighbor) == self.un_color:
				self.capture(board, neighbor)
	# 石を打つ
	def move(self, board, position):
		if position == (0, 0):
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
		for i, neighbor in enumerate(neighbors(position)):
			colors[i] = c = board.get(neighbor)
			if c == SPACE:
				space += 1
				continue
			if c == WALL:
				wall += 1
				continue

			# 連石と呼吸点の数を数える
			joineds[i], libertys[i] = count_joined_liberty(board, neighbor, c)
			# 相手の石が取れるなら，劫の可能性があるので保持
			if c == self.un_color and libertys[i] == 1:
				take_sum += joineds[i]
				ko = neighbor
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
		for i, neighbor in enumerate(neighbors(position)):
			if colors[i] == self.un_color and libertys[i] == 1:
				self.capture(board, neighbor)

		# 石を打つ
		board.set(position, self.color)

		# 劫を取った直後は相手が取り返せないようにする
		joined, liberty = count_joined_liberty(board, position, self.color)
		if take_sum == 1 and joined == 1 and liberty == 1:
			board.ko = ko 		# 碁盤に劫の目印をつけておく
		else:
			board.ko = None 	# 劫の目印を消す

		return SUCCESS

# 盤上の[黒石，白石]の数を取得
def counting(board):

	def stones():
		for y in xrange(1, board.size-1):
			for x in xrange(1, board.size-1):
				data = board.get((y,x))
				if data == BLACK or data == WHITE:
					yield data
				elif data == SPACE:
					# 空点は4方向の石の種類を調べる
					around = [0]*4
					for neighbor in neighbors((y,x)):
						around[board.get(neighbor)] += 1
					# 黒だけに囲まれていれば黒地
					if around[BLACK] > 0 and around[WHITE] == 0:
						yield BLACK
					# 白だけに囲まれていれば白地
					if around[WHITE] > 0 and around[BLACK] == 0:
						yield WHITE
	count = {BLACK:0, WHITE:0}
	for stone in stones():
		count[stone] += 1
	return count


# コミを考慮した結果
def scoring(board):
	KOMI = 6.5
	count = counting(board)
	return {BLACK: count[BLACK] - KOMI, WHITE: count[WHITE]}

def judge(score):
	black, white = score[BLACK], score[WHITE]
	print VISUAL[BLACK], black
	print VISUAL[WHITE], white
	print VISUAL[BLACK if black > white else WHITE], "勝ち"

def main():
	main_start = time.time()
	
	# 碁盤
	BOARD_SIZE = 9
	board = Board(BOARD_SIZE)

	# プレイヤー
	black = Player(BLACK, MONTE_CARLO)
	white = Player(WHITE, RANDOM)
	turn  = {black:white, white:black}

	# 先手
	player = black

	# 対局開始
	passed = 0
	while passed < 2:
		# 打った結果を取得
		result = player.play(board)
		if result == SUCCESS:
			# 成功したら描画
			print VISUAL[player.color], player.position
			board.draw()
			print
			passed = 0
		else:
			# 失敗したら失敗表示
			print VISUAL[player.color], ERROR_MESSAGE[result]
			passed += 1

		player = turn[player]

	board.draw()
	print "対局終了"
	judge(scoring(board))

	main_elapsed_time = time.time() - main_start
	print ("main_elapsed_time:{0}".format(main_elapsed_time)) + "[sec]"


if __name__ == '__main__':
	main()