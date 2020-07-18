#

class UI:

	def __init__(self, uid, game_obj):
	
		self.uid = uid
		self.game = game_obj
		
		self.dlgs = {}
		self.hud = {}
		
		self.active_dlg = None
		
		self.stack = []
		
	def set_stack(self, *dlgs):
	
		
