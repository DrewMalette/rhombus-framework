#

class Armour:

	def __init__(self, uid, armour_type, defence, special=None):
	
		self.uid = uid
		self._type = armour_type
		self.defence = defence
		self.special = special

class Equipment:

	def __init__(self, mob_obj):
	
		self.mob_obj = mob_obj
	
		self.slots = { 0: None, 1: None, 2: None, 3: None }
	
	def equip(self, piece, slot):

		self.slots[slot] = piece

		for s in range(len(self.slots)):
			if s != slot and self.slots[s] != None:
				if self.slots[s]._type == piece._type:
					self.slots[s] = None
				
	def print_equip(self):

		for s in range(len(self.slots)):
			if self.slots[s] != None:
				print("Slot "+str(s), self.slots[s].uid, self.slots[s]._type, 
				self.slots[s].defence, self.slots[s].special)
			else:
				print("Slot "+str(s), None)

if __name__ == "__main__":

	blk_shirt = Armour("blk_shirt", "shirt", 1)
	wht_shirt = Armour("wht_shirt", "shirt", 1)
	flak_jacket = Armour("flak_jacket", "chest", 3)

	equip = Equipment(None)
								
	equip.equip(blk_shirt, 1)
	equip.equip(flak_jacket, 3)
	equip.equip(wht_shirt, 2)
	equip.equip(blk_shirt, 0)

	equip.print_equip()
