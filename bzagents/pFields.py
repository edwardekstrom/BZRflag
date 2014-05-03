#!/usr/bin/python -tt



class PField(object):

	def __init__(x, y, r, s, direction):
		self.x = x
		self.y = y
		self.direction = direction


	def calc_vector(self, tank_x, tant_y):
		# find the distance
		dist = math.sqrt((self.x - tank_x)**2 + (self.y - tank_y)**2)

		# find the angle
		angle = math.atan2(self.y - tank_y, self.x - tank_x)

		# find the speed
		if dist < r:
			speed = 0
		elif (dist >= r) and (dist <= s):
			speed = float((r - s) / s) * float(1.0)
		else
			speed = 1

		#return speed and angle
		return (speed, angle)
