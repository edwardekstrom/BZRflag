#!/usr/bin/python -tt



class PField(object):

	def __init__(x, y, direction, attachedTo):
		self.x = x
		self.y = y
		self.direction = direction
		self.attachedTo = attachedTo


	def motd(self):
		print "Message of the Day: I am a FIELD!!!"
