from random import random as rnd

dice = lambda d: int(rnd() * d) + 1

class StatBlock:

	def __init__(self, bod, mnd, spi, level=1):
	
		self.level = level
		self.body = bod
		self.mind = mnd
		self.spirit = spi
		
		self.fortitude = int((self.body+self.spirit) / 2)
		self.reflex = int((self.mind+self.body) / 2)
		self.will = int((self.spirit+self.mind) / 2)
		
		self.evade = 10 + self.reflex + int(self.level / 3)
		
		self.max_hp = self.body * self.spirit + 3 # absolute
		self.cur_hp = self.max_hp
		
		self.exp = 0
		self.next = 500
		
	def melee_hit(self, target):
	
		roll = dice(20)
		return roll + self.fortitude + int(self.level / 2) >= target.evade
	
	def ranged_hit(self, target):
	
		return roll + self.reflex + int(self.level / 2) >= target.evade
		
	def level_up(self):
	
		self.level += 1
		
		# can you take a stat boost?
		if self.level % 3 == 0:
			print("Which stat would you like to boost?")
		if self.level % 4 == 0:
			print("Which new special skill would you like?")
				
		self.fortitude = int((self.body+self.spirit) / 2)
		self.reflex = int((self.mind+self.body) / 2)
		self.will = int((self.spirit+self.mind) / 2)
		
		self.max_hp += int(self.fortitude / 2) + dice(4) # body
		self.cur_hp = self.max_hp
		self.evade = 10 + self.reflex + int(self.level / 3)
		
		self.exp = 0
		self.next = self.level * 500
		
	def add_exp(self, amount):
	
		self.exp += amount
		
		if self.exp >= self.next: self.level_up()

if __name__ == "__main__":

	player = StatBlock(4,3,3)
	wolf = StatBlock(4,4,6)

	hit = 0
	miss = 0

	for i in range(100):
		result = wolf.hit(player)
		if result == True:
			hit += 1
		else:
			miss += 1
		print(result)
	print(hit)
	print(miss)
