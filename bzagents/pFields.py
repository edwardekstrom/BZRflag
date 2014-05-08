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
		dist = math.sqrt((self.x - tank_x)**2 + (self.y - tank_y)**2)

		# find the angle
		angle = 0.0
		if self.direction == 'attract':
			angle = math.atan2(self.y - tank_y, self.x - tank_x)

		elif self.direction == 'repel':
			if dist < self.s:
				r_int = random.randint(1, 100)
				if(r_int < 50):
					angle = math.atan2(self.y - tank_y, self.x - tank_x) - (math.pi / 8.0)
				else:
					angle = math.atan2(self.y - tank_y, self.x - tank_x) + (math.pi / 8.0)

		elif self.direction == 'tangent':
			if dist < self.s:
				angle = math.atan2(self.y - tank_y, self.x - tank_x) + ((5 * math.pi) / 9.0)
			else:
				angle = math.atan2(self.y - tank_y, self.x - tank_x)


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
