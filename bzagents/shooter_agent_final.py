#!/usr/bin/python -tt

# An incredibly simple agent.  All we do is find the closest enemy tank, drive
# towards it, and shoot.  Note that if friendly fire is allowed, you will very
# often kill your own tanks with this code.

#################################################################
# NOTE TO STUDENTS
# This is a starting point for you.  You will need to greatly
# modify this code if you want to do anything useful.  But this
# should help you to know how to interact with BZRC in order to
# get the information you need.
#
# After starting the bzrflag server, this is one way to start
# this code:
# python agent0.py [hostname] [port]
#
# Often this translates to something like the following (with the
# port name being printed out by the bzrflag server):
# python agent0.py localhost 49857
#################################################################

import sys
import math
import time
import random

from bzrc import BZRC, Command
from pFields import PField
from grid import Grid
from kalman import Kalman

import numpy
from numpy import *
from numpy.linalg import *
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from numpy import zeros


grid = None

def draw_grid():
	# This assumes you are using a numpy array for your grid
	width, height = grid.shape
	glRasterPos2f(-1, -1)
	glDrawPixels(width, height, GL_LUMINANCE, GL_FLOAT, grid)
	glFlush()
	glutSwapBuffers()

def update_grid(new_grid):
	global grid
	grid = new_grid



def init_window(width, height):
	global window
	global grid
	grid = zeros((width, height))
	glutInit(())
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
	glutInitWindowSize(width, height)
	glutInitWindowPosition(0, 0)
	window = glutCreateWindow("Grid filter")
	glutDisplayFunc(draw_grid)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	#glutMainLoop()

class KAgent(object):
	"""Class handles all command and control logic for a teams tanks."""
	initialGridConstant = 0

	def __init__(self, bzrc, tank_index):
		#print tank_index
		self.agent_index = tank_index
		self._kalman = Kalman()
		self.aliveTime = time.time()
		self.bzrc = bzrc
		self.constants = self.bzrc.get_constants()
		
		self.mytanks = self.bzrc.get_mytanks()
		self.targetTank,self.targ = self.closest_enemy(self.mytanks[self.agent_index], self.bzrc.get_othertanks())
		self._kalman.resetArrays(self.targetTank.x, self.targetTank.y)
		
		# print self.constants
		self.commands = []
		self.potentialFields = []
		self.updates = []
		self.flag_sphere = 400
		self.obstacle_sphere = 1000
		self.enemy_sphere = 100
		self.explore_sphere = 50

		self.prev_x = {}
		self.prev_y = {}
		self.stuck_ticks = {}
		for x in xrange(20):
			self.prev_x[x] = 0
			self.prev_y[x] = 0
			self.stuck_ticks[x] = 0

		self.path_fields = []
		self.grid = Grid(int(self.constants['worldsize']),
			int(self.constants['worldsize']),
			self.initialGridConstant,
			self.initialGridConstant)



	def tick(self, time_diff):
		"""Some time has passed; decide what to do next."""
		# don't need to know where the flags or shots are when exploring.  Enemies are included in the 'othertanks' call
		# pos,partialGrid = self.bzrc.get_occgrid()
		# self.grid.updateGrid(pos,partialGrid)
		self._kalman.setDT(time_diff)
		self.mytanks = self.bzrc.get_mytanks()
		# self.othertanks = self.bzrc.get_othertanks()
		self.targetTank = self.bzrc.get_othertanks()[self.targ]
		self.commands = []
		if self.targetTank.status == 'alive':
			self.lock_on(self.targetTank)
		else:
			self.targetTank,self.targ = self.closest_enemy(self.mytanks[self.agent_index], self.bzrc.get_othertanks())
			# self.targ = self.targetTank.index
			self.aliveTime = time.time()
			#stopMoving = Command(self.agent_index,0,0,False)
			#self.commands.append(stopMoving)
			#self.bzrc.do_commands(self.commands)
			self._kalman.resetArrays(self.targetTank.x, self.targetTank.y)

	def lock_on(self, targetTank):
		agentTank = self.mytanks[self.agent_index]
		print str(targetTank.x) + ' ' + str(targetTank.y)
		# print str(targetTank)
		Zt = array([[targetTank.x],
						  [targetTank.y]])
		self._kalman.updateKalmanFilter(Zt)

		est = self._kalman.H.dot(self._kalman.mu)

		self.updates.append(((int(est[0][0]), int(est[1][0])),self._kalman.sigmaT))
		aimAngle,distance = self.take_aim((agentTank.x,agentTank.y), agentTank.angle)
		command = Command(0,0,aimAngle*2,True)
		if aimAngle < 1 and aimAngle > -1:
			if distance < 350:
				# print 'shooting'
				command = Command(self.agent_index,0,aimAngle*2,True)
			else:
				# print 'not shooting distance'
				command = Command(self.agent_index,0,aimAngle*2,False)
		else:
			# print 'not shooting aimAngle'
			command = Command(self.agent_index,0,aimAngle*2,False)
		self.commands.append(command)
		self.bzrc.do_commands(self.commands)

	def take_aim(self, tankPosition, tankAngle):
		xPos = self._kalman.mu[0][0]
		xVel = self._kalman.mu[1][0]
		xAcc = self._kalman.mu[2][0]
		yPos = self._kalman.mu[3][0]
		yVel = self._kalman.mu[4][0]
		yAcc = self._kalman.mu[5][0]

		tankX, tankY = tankPosition

		velocity = math.sqrt(xVel**2 + yVel**2)
		acceleration = math.sqrt(xAcc**2 + yAcc**2)

		distance = self.dist(tankX,tankY,xPos,yPos)
		timeToEnemy = 0

		r = (100-velocity)**2 - 4*(acceleration/2)*distance*-1
		# I'm getting a division by zero error here with the acceleration variable,
		#  probably because I reset the arrays to soon?
		plusRoot = (-(100-velocity) + math.sqrt(r))
		minusRoot = (-(100-velocity) - math.sqrt(r))
		if acceleration != 0:
			plusRoot/=acceleration
			minusRoot/=acceleration
		if plusRoot > minusRoot:
			timeToEnemy = plusRoot
		else:
			timeToEnemy = minusRoot

			
		self._kalman.setDT(timeToEnemy)
		projectionMatrix = self._kalman.projectPosition()
		projectedX = projectionMatrix[0][0]
		projectedY = projectionMatrix[3][0]

		distance = self.dist(tankX,tankY,projectedX,projectedY)
		angel = math.atan2(projectedY - tankY, projectedX - tankX)
		return (self.normalize_angle(angel - tankAngle), distance)

	def closest_enemy(self, tank, enemies):
		best_d = (2 * float(self.constants['worldsize']))**2

		best_e = None
		index = 0
		i = 0
		for e in enemies:
			# print str(e.x)
			# print str(e.y)
			d = self.dist(e.x, e.y, tank.x, tank.y)
			if d < best_d:
				best_d = d
				# closest_x = e.x
				# closest_y = e.y
				best_e = e
				# print str(e)
				index = i
			i+=1

		return (best_e, index)

	def doUpdate(self):
		# print len(self.updates)
		for update in self.updates:
			pos,partialGrid = update
			self.grid.updateGrid(pos,partialGrid)
		self.updates = []

	def dist(self, x1, y1, x2, y2):
		dist_result = math.sqrt((float(x1) - float(x2))**2 + (float(y1) - float(y2))**2)
		#print dist_result
		return dist_result

	def normalize_angle(self, angle):
		"""Make any angle be between +/- pi."""
		angle -= 2 * math.pi * int (angle / (2 * math.pi))
		if angle <= -math.pi:
			angle += 2 * math.pi
		elif angle > math.pi:
			angle -= 2 * math.pi
		return angle


def main():
	# Process CLI arguments.
	try:
		execname, host, port = sys.argv
	except ValueError:
		execname = sys.argv[0]
		print >>sys.stderr, '%s: incorrect number of arguments' % execname
		print >>sys.stderr, 'usage: %s hostname port' % sys.argv[0]
		sys.exit(-1)

	# Connect.
	#bzrc = BZRC(host, int(port), debug=True)
	bzrc = BZRC(host, int(port))


	agent = KAgent(bzrc)

	init_window(int(agent.constants['worldsize']),int(agent.constants['worldsize']))
	# print 'init complete'
	prev_time = time.time()

	# Run the agent
	try:
		global tic
		tic = 0
		while True:
			t = time.time()
			time_diff = t - prev_time
			prev_time = t
			agent.tick(time_diff)
			agent.doUpdate()
			if(tic == 10):
				if (time.time() - agent.aliveTime) > 60:
					agent._kalman.resetSigmaT()
					agent.aliveTime = time.time()
					print 'reset sigmaT'
				update_grid(numpy.array(zip(*agent.grid.grid)))
				draw_grid()
				tic = 0
			tic+=1
	except KeyboardInterrupt:
		print "Exiting due to keyboard interrupt."
		bzrc.close()


if __name__ == '__main__':
	main()

# vim: et sw=4 sts=4












