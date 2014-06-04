#grid class and gridsquare class
import numpy
from numpy import zeros
import math

class Grid:
	def __init__(self, width, height,truePos,trueNeg):
		self.dimensions = (width, height)
		self.grid = zeros(self.dimensions)
		self.truePos = truePos
		self.trueNeg = trueNeg
		# print self.truePos
		# print self.trueNeg
		# print self.grid
		self.grid.fill(0)
		# print self.grid
		
		# for x in grid:
		# 	s = ''
		# 	for y in range(0,height):
		# 		s+=str(x[y])
		# 	print s

	def updateGrid(self,pos,sigmaT):
		x0,y0 = pos
		x0+=self.dimensions[0]/2
		y0+=self.dimensions[1]/2
		self.grid[x0][y0] = 1

		xVariance = sigmaT[0][0]
		yVariance = sigmaT[3][3]
		original = xVariance
		oneTenth = xVariance/10
		shading = .1
		while xVariance > 0:
			for i in xrange(360):
				cosine = int(x0+math.cos(i*math.pi/180)*xVariance)
				sine = int(y0+math.sin(i*math.pi/180)*yVariance)
				if self.inGrid((cosine, sine)):
					self.grid[cosine][sine] = shading
			shading+=.1
			xVariance-=oneTenth
			yVariance-=oneTenth

	def inGrid(self, pos):
		x,y = pos
		isIn = True
		if x < 0:
			return False
		elif x > self.dimensions[0]:
			return False
		elif y < 0:
			return False
		elif y > self.dimensions[1]:
			return False
		else:
			return True