

import pygame

pygame.init()

class Timer:

	def __init__(self, time):
	
		self.time = time
		
		self.tick = 0		
		self.trig = False
	
	def start(self):
	
		self.tick = pygame.time.get_ticks()
		self.trig = False
		
	def update(self):
	
		if pygame.time.get_ticks() - self.tick == self.time and not self.trig:
			self.trig = True
			print("done")
			self.start() # this doesn't need to be here

if __name__ == "__main__":

	focustime = 12 * 100		
	timer = Timer(1500-focustime)
	timer.start()

	while 1:
		timer.update()
