#grid class and gridsquare class
import numpy
from numpy import zeros
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros

class Grid:
	def __init__(self, width, height,truePos,trueNeg):
		self.dimensions = (width, height)
		self.grid = zeros(self.dimensions)
		self.truePos = truePos + 30
		self.trueNeg = trueNeg + 30
		# print self.truePos
		# print self.trueNeg
		# print self.grid
		self.grid.fill(.1)
		# print self.grid
		
		# for x in grid:
		# 	s = ''
		# 	for y in range(0,height):
		# 		s+=str(x[y])
		# 	print s

	def updateGrid(self,pos,miniGrid):
		x0,y0 = pos
		x0+=self.dimensions[0]/2
		y0+=self.dimensions[1]/2
		x = x0
		y = y0
		for col in miniGrid:
			for row in col:
				prior = self.grid[x][y]

				if row == 1:
					occupied = self.truePos * prior
					unoccupied = (1 - self.trueNeg) * (1 - prior)
				else:
					occupied = (1 - self.truePos) * prior
					unoccupied = self.trueNeg * (1 - prior)
				
				self.grid[x][y] = occupied / (occupied + unoccupied)

				y+=1
			y=y0
			x+=1