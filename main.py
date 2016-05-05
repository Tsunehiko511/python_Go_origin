# -*- coding:utf-8 -*-
import random

# 碁盤
BOARD_SIZE = 9				# 碁盤の大きさ

# 盤上の種類
NONE,BLACK,WHITE,WALL = 0,1,2,3
VISUAL = ("・","🔴 ","⚪️ ", "　")

class Board(object):
	# 碁盤作成
	def __init__(self,size):
		self.size = size + 2 	# 上下左右に外枠を含めた碁盤
		self.data = data = [[NONE]*self.size for i in range(self.size)]
		# 外枠の作成
		for i in range(self.size):
			data[0][i] = data[-1][i] = data[i][0] = data[i][-1] = WALL

	# 石を打つ
	def move(self,position,stone):
		y,x = position
		self.data[y][x] = stone

	# 盤上の空の場所を配列で取得
	def getNonePositions(self):
		return [(y,x)
				for y in range(1,self.size-1)
				for x in range(1,self.size-1)
				if self.data[y][x] == NONE]

	# 碁盤描画
	def draw(self):
		print " ", " ".join("%2d"%x for x in range(1,self.size-1))
		for y in range(1,self.size-1):
			print "%2d"%y, " ".join(VISUAL[data] for data in self.data[y][1:-1])

def main():
	# 碁盤
	board = Board(BOARD_SIZE)

	# 先手
	color = BLACK

	# ゲーム開始
	positions = board.getNonePositions()
	random.shuffle(positions)
	for position in positions:
		board.move(position,color)
		print VISUAL[color], position
		board.draw()
		color = WHITE if color == BLACK else BLACK

if __name__ == '__main__':
	main()