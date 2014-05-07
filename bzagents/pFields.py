#!/usr/bin/python -tt

import math

class PField(object):

	def __init__(self, x, y, r, s, direction):
		self.x = x
		self.y = y
		self.r = r
		self.s = s
		self.direction = direction


	def calc_vector(self, tank_x, tank_y):
		# find the distance
		dist = math.sqrt((self.x - tank_x)**2 + (self.y - tank_y)**2)

		# find the angle
		angle = 0.0
		speed = 1.0
		if self.direction == 'attract':
			angle = math.atan2(self.y - tank_y, self.x - tank_x)
		elif self.direction == 'repel':
			angle = -math.atan2(self.y - tank_y, self.x - tank_x)

		if dist < self.r:
			speed = 0
		elif (dist >= self.r) and (dist <= self.s):
			speed = float(dist - self.r) / float(self.s - self.r)
		else:
			speed = 1


		#return speed and angle
		return (speed, angle)
