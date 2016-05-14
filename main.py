# -*- coding:utf-8 -*-
import random
import time
import copy
 
# 盤上の種類
SPACE, BLACK, WHITE, WALL = 0, 1, 2, 3
VISUAL = {SPACE: "・", BLACK: "🔴 ", WHITE: "⚪️ ", WALL: "　"}
 
# 石を打ったときの処理
SUCCESS = 0     # 打てる
KILL = "自殺手"
KO = "劫"
ME = "眼"
MISS = "すでに石がある"
PASS = "パス"
 
# 戦略
RANDOM = 1
MONTE_CARLO = 2
 
'''
時間計測テンプレート
start = time.time()
elapsed_time = time.time() - start
print ("elapsed_time:{0}[sec]".format(elapsed_time))
'''
 
# 碁盤　
class Board(object):
 
    # 碁盤作成
    def __init__(self, size, data=None, ko=None):
        self.width = size + 2   # 上下左右に外枠を含めた碁盤
        if data == None:
            width = self.width
            data = [SPACE] * width * width
            # 外枠の作成
            for i in xrange(self.width):
                data[+i] = WALL                 # 上壁
                data[-i - 1] = WALL             # 下壁
                data[+i * width] = WALL         # 左壁
                data[-i * width - 1] = WALL     # 右壁
        self.data = data
        # 劫の位置 (直後には取り返せない)
        self.ko = ko
 
    # コピー作成
    def copy(self):
        return Board(self.width - 2, self.data[:], self.ko)
 
    # 碁盤描画
    def draw(self):
        width = self.width
        data = self.data
        print "  ", " ".join("%2d" % x for x in xrange(1, width - 1))
        for y in xrange(1, width - 1):
            x = y * width
            print "%2d" % y, " ".join(VISUAL[d] for d in data[x + 1:x + width - 1])
 
    # 表示部分の位置を列挙
    def positions(self):
        return (y * self.width + x
                for y in xrange(1, self.width - 1)
                for x in xrange(1, self.width - 1))
 
    # 盤上の空の場所を配列で取得
    def getSpacePositions(self):
        return [position
                for position in self.positions()
                if self.data[position] == SPACE]
 
    # 指定位置からの上下左右の座標を返す
    def neighbors(self, position):
        return (position - self.width,      # 上
                position + self.width,      # 下
                position - 1,               # 左
                position + 1)               # 右
 
    # 指定位置からの「連石の数」と「呼吸点の数」を返す
    def count_chains_liberties(self, position, color):
        count = [0, 0]      # [連石の数, 呼吸点の数]
        data = self.data
        width = self.width
        checked = [0] * len(data)
        def count_around(center):
            checked[center] = 1
            count[0] += 1
            for neighbor in center - width, center + width, center - 1, center + 1:
                if checked[neighbor] == 1:
                    continue
                stone = data[neighbor]
                if stone == SPACE:
                    checked[neighbor] = 1
                    count[1] += 1
                elif stone == color:
                    count_around(neighbor)
        count_around(position)
        return count
 
class Player(object):
 
    def __init__(self, color, strategy):
        self.color = color
        self.un_color = WHITE if color == BLACK else BLACK
        self.tactics = tactics(strategy)
 
    # 一手打つ
    def play(self, board):
        return self.tactics(self, board)
 
    # 相手の石を取る
    def capture(self, board, position):
        data = board.data
        data[position] = SPACE
        un_color = self.un_color
        for neighbor in board.neighbors(position):
            if data[neighbor] == un_color:
                self.capture(board, neighbor)
 
    # 石を打つ
    def move(self, board, position):
        # すでに石がある場合
        data = board.data
        if data[position] != SPACE:
            return MISS
 
        # positionに対して4方向の[連石の数，呼吸点の数，色]
        chains = [0, 0, 0, 0]
        liberties = [0, 0, 0, 0]
        colors = [0, 0, 0, 0]
 
        space = 0           # 4方向の空白の数
        wall = 0            # 4方向の壁の数
        mikata_safe = 0     # 呼吸点が2以上の味方の数
        take_sum = 0        # 取れる石の合計
        ko = None           # 劫の候補
 
        # 打つ前に4方向を調べる
        color = self.color
        un_color = self.un_color
        count_chains_liberties = board.count_chains_liberties
        for i, neighbor in enumerate(board.neighbors(position)):  # enumerate:インデックスとともにループ
            c = data[neighbor]
            if c == SPACE:
                space += 1
                continue
            if c == WALL:
                wall += 1
                continue
            colors[i] = c
 
            # 連石と呼吸点の数を数える
            chains[i], liberties[i] = count_chains_liberties(neighbor, c)
            # 相手の石が取れるなら，劫の可能性があるので保持
            if c == un_color and liberties[i] == 1:
                take_sum += chains[i]
                ko = neighbor
            # 味方の石があって呼吸点が2つ以上あるなら眼の可能性
            if c == color and liberties[i] >= 2:
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
        capture = self.capture
        for i, neighbor in enumerate(board.neighbors(position)):
            if colors[i] == un_color and liberties[i] == 1:
                capture(board, neighbor)
 
        # 石を打つ
        data[position] = color
 
        # 劫を取った直後は相手が取り返せないようにする
        chains, liberties = count_chains_liberties(position, color)
        if take_sum == 1 and chains == 1 and liberties == 1:
            board.ko = ko       # 碁盤に劫の目印をつけておく
        else:
            board.ko = None     # 劫の目印を消す
 
        return SUCCESS
 
    # 置ける場所を配列で取得
    def getSuccessPositions(self, board):
        # 石を置ける場所を探すために，コピーした碁盤に石を置いて確認する
        return [position
                for position in board.getSpacePositions()
                if self.move(board.copy(), position) == SUCCESS]
 
# 戦術を取得
def tactics(strategy):
 
    # 対戦相手が打つところから終局まで打ち，勝敗を返す
    def playout(color, board):
        player1 = Player(color, RANDOM)
        player2 = Player(player1.un_color, RANDOM)
        turn = {player1: player2, player2: player1}
        player = player1
        passed = 0
        while passed < 2:
            result = player.play(board)
            passed = 0 if result == SUCCESS else passed + 1
            player = turn[player]
        return scoring(board)
 
    def monte_carlo(player, board):
        monte_start = time.time()
 
        TRY_GAMES = 10
        try_total = 0
        best_winner = -1
 
        # すべての手に対して1手打ってみる
        thinking_board = None
        spaces = board.getSpacePositions()
        random.shuffle(spaces)
        board_copy = board.copy
        player_move = player.move
        color = player.color
        un_color = player.un_color
        for i, position in enumerate(spaces):
            if thinking_board == None:
                thinking_board = board_copy()
            result = player_move(thinking_board, position)  # 石を打ってみる
            if result != SUCCESS:                           # 違反したら次
                continue
 
            # (相手の手から)playoutをTRY_GAMES回繰り返す
            win_count = 0
            for n in xrange(TRY_GAMES):
                score = playout(un_color, thinking_board.copy())
                if score[color] > score[un_color]:
                    win_count += 1
 
            thinking_board = None
            try_total += TRY_GAMES
 
            # 勝率(勝った回数)が最も高いものを選ぶ
            if win_count > best_winner:
                best_winner = win_count
                best_position = position
 
        monte_elapsed_time = time.time() - monte_start
        print try_total
        print "monte_elapsed_time:{0}[sec]".format(monte_elapsed_time)
        if best_winner >= 0:
            player.position = best_position
            return player.move(board, best_position)
        return PASS
 
    def random_choice(player, board):
        spaces = board.getSpacePositions()
        while len(spaces) > 0:
            position = random.choice(spaces)
            result = player.move(board, position)  # 石を打つ
            if result == SUCCESS:
                player.position = position
                return SUCCESS
            spaces.remove(position)
        return PASS
 
    # 戦略に対する戦術を選択する
    if strategy == RANDOM:
        return random_choice
    if strategy == MONTE_CARLO:
        return monte_carlo
    return random_choice
 
 
# 終局の石を列挙する。AIは空点ひとつになるまで打つので空点は4方向を調べて決定。
def stones(board):
    data = board.data
    neighbors = board.neighbors
    for position in board.positions():
        stone = data[position]
        if stone == BLACK or stone == WHITE:
            yield stone
        elif stone == SPACE:
            # 空点は4方向の石の種類を調べる
            around = [0, 0, 0, 0]
            for neighbor in neighbors(position):
                around[data[neighbor]] += 1
            # 黒だけに囲まれていれば黒地
            if around[BLACK] > 0 and around[WHITE] == 0:
                yield BLACK
            # 白だけに囲まれていれば白地
            if around[WHITE] > 0 and around[BLACK] == 0:
                yield WHITE
 
# 盤上の[黒石，白石]の数を取得
def counting(board):
    count = {BLACK: 0, WHITE: 0}
    for stone in stones(board):
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
    BOARD_SIZE = 9              # 碁盤の大きさ
    board = Board(BOARD_SIZE)
 
    # プレイヤー
    black = Player(BLACK, MONTE_CARLO)
    white = Player(WHITE, RANDOM)
    turn = {black: white, white: black}
 
    # 先手
    player = black
    # 対局開始
    passed = 0
    while passed < 2:
        result = player.play(board)
        if result == SUCCESS:           # 打てたら描画 選択終了
            print VISUAL[player.color], player.position
            board.draw()
            print
            passed = 0
        else:
            print VISUAL[player.color], result
            passed += 1
 
        # プレイヤー交代
        player = turn[player]
        # time.sleep(0)
 
    board.draw()
    print "対局終了"
    judge(scoring(board))
 
    main_elapsed_time = time.time() - main_start
    print "main_elapsed_time:{0}[sec]".format(main_elapsed_time)
 
 
if __name__ == '__main__':
    main()