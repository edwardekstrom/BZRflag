#!/usr/bin/python -tt

import math
import random

class PField(object):

	def __init__(self, x, y, r, s, direction):
		self.x = x
		self.y = y
		self.r = r
		self.s = s
		self.direction = direction


	def calc_vector(self, tank_x, tank_y):
		# find the distance
		dist = (self.x - tank_x)**2 + (self.y - tank_y)**2

		# find the angle
		angle = 0.0
		if self.direction == 'attract':
			angle = math.atan2(self.y - tank_y, self.x - tank_x)

		elif self.direction == 'repel':
			# if dist < self.s:
			angle = math.atan2(tank_y - self.y, tank_x - self.x)

		elif self.direction == 'tangent':
			# print dist
			# print str(dist) + ' , ' + str(self.s)
			# if dist < self.s:
			angle = math.atan2(math.cos(self.x - tank_x), -math.sin(self.y - tank_y))


		# find the speed for attraction/repelling
		speedmod = 1.0
		if self.direction == 'attract':
			# inside radius
			if dist < self.r:
				speedmod = 0.0
			# inside sphere
			elif (dist >= self.r) and (dist <= self.s):
				speedmod = float(dist - self.r) / float(self.s - self.r)
			else:
				speedmod = 1.0
		#elif self.direction == 'repel':
			

		#return speed and angle
		return (speedmod, angle)
