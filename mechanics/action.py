#

import pygame

class Action(pygame.Rect):

	def __init__(self):
	
		pygame.Rect.__init__(self, (0,0,12,12)) # defaults to basic interaction rect
		
	def interact(self, mob_obj):

		if mob_obj.facing == "north":
			x = (mob_obj.x + mob_obj.w / 2) - (mob_obj.w / 2) + 1
			y = mob_obj.y - self.h - 7
		elif mob_obj.facing == "south":
			x = (mob_obj.x + mob_obj.w / 2) - (self.w / 2) + 1
			y = mob_obj.y + mob_obj.h
		elif mob_obj.facing == "west":
			x = mob_obj.x - self.w
			y = (mob_obj.y + mob_obj.h / 2) - (self.h / 2) - 3
		elif mob_obj.facing == "east":
			x = mob_obj.x + mob_obj.w + 2
			y = (mob_obj.y + mob_obj.h / 2) - (self.h / 2) - 3
			
		self.x = x
		self.y = y
		self.w = 12
		self.h = 12
		
	def attack(self, mob_obj, target):
	
		# self.w, self.h = mob_obj.weapon.get_size()
		pass
