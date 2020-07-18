#

from . import filepaths
from . import utilities

class Scene:

	def __init__(self, uid, game_obj, filename):

		self.uid = uid
		self.game = game_obj
		
		self.mobs = {}
		self.live_mobs = {}
		self.buildings = {}
		self.furniture = {}
		self.loot = {}
		self.loot_count = 0
		self.switches = {}
		self.layerdata = { "bottom": None, "middle": None, "top": None, "collide": None }
		self.tileset_obj = None
		
		self.filename = filename
		utilities.load_tmx(self.filename, self)
		
		self.paused = False
		
	def add_loot(self, filename, x, y):
	
		uid = self.loot_count
		px = x
		py = y - 20
		self.loot[self.loot_count] = sprite.Loot(self, uid, filename, (px,py))
		self.loot_count = (self.loot_count + 1) % 256
		
	def add_mob(self, mob_obj):
	
		self.mobs[mob.name] = mob_obj
	
	def get_tile(self, layername, col, row):
	
		index = int((row % self.rows) * self.cols + (col % self.cols))
		return self.layerdata[layername][index]
			
	def update(self):
		
		if not self.game.fader.fading and not self.paused:
			for mob in self.live_mobs.values():
				mob.update()
			self.game.camera.update()
		
	def render(self):
	
		self.game.camera.render()

