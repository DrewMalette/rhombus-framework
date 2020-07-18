#

import operator

import pygame

from . import mob
from . import scene
from . import utilities

class Game:

	fps = 60
	display_size = (640,480)

	def __init__(self):
	
		self.display = pygame.display.set_mode(self.display_size)
		self.fader = Fader(self, self.display.get_size())
		self.camera = Camera("camera", self)
		
		self.controller = Gamepad(self)
				
		self.clock = pygame.time.Clock()
		self.tick = 0
		
		self.obj_stack = [] # list containing Surfaces or objects with render method
		
		self.last_script = None # unimplemented
		self.script = None
		self.next_script = None # will it ever be used internally?
		self.player = None
		self.scene_obj = None # TODO rename to self.scene; usage: self.scene = scene_obj
		
		self.mob_orphans = [] # unimplemented
		
		self.ui = {}
		self.ui_font = pygame.font.Font(None, 24)
		self.title_card = None
		self.music_tracks = {}
		
		self.debug_info_on = -1
		self.debug_font = pygame.font.Font(None, 20)

	def load_scene(self, uid, filename):
		
		self.scene_obj = scene.Scene(uid, self, filename)
		self.camera.scene_obj = self.scene_obj
		self.camera.following = self.player
		# assumes the tile is square
		self.camera.tilesize = self.scene_obj.tilewidth
		self.camera.cols = int(self.camera.w / self.scene_obj.tilesize + 2)
		self.camera.rows = int(self.camera.h / self.scene_obj.tilesize + 2)
		self.camera.blank = pygame.Surface((self.scene_obj.tilesize,self.scene_obj.tilesize)).convert()
		self.camera.blank.fill((0,0,0))
		
		#self.controller.flush()
		self.player.moving = False
		#self.sprites["player"].facing = "south" TODO put this somewhere else (like in a gamestate)
		self.camera.update()		
	
	def main(self):
	
		self.running = True
		
		while self.running:
			self.update()
			self.render()

	def exit(self, _):
			
		pygame.quit()
		exit()

	def fade_loop(self, _):
	
		if self.fader.faded_out or self.fader.faded_in:
			self.script = self.next_script

	def draw_debug_info(self):
	
		labels = []
		c = r = 0
		
		if self.scene_obj:
			labels.append(self.debug_font.render("Scene: "+self.scene_obj.filename, 0, (0xff,0xff,0xff)))
			c = int(self.player.x / self.scene_obj.tilesize)
			r = int(self.player.y / self.scene_obj.tilesize)
		else:
			labels.append(self.debug_font.render("no scene is loaded", 0, (0xff,0xff,0xff)))
			
		labels.append(self.debug_font.render("Script: "+self.script.__name__, 0, (0xff,0xff,0xff)))
		
		if self.player:
			labels.append(self.debug_font.render("player.in_dialogue: "+str(self.player.in_dialogue), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("player.x (pixel): "+str(self.player.x), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("player.y (pixel): "+str(self.player.y), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("player.c (tile): "+str(c), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("player.r (tile): "+str(r), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("action.x: "+str(self.player.action.x), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("action.y: "+str(self.player.action.y), 0, (0xff,0xff,0xff)))
			labels.append(self.debug_font.render("facing: "+self.player.facing, 0, (0xff,0xff,0xff)))
			
		labels.append(self.debug_font.render("pressed_a: "+str(self.controller.pressed_a), 0, (0xff,0xff,0xff)))
		labels.append(self.debug_font.render("held_a: "+str(self.controller.held_a), 0, (0xff,0xff,0xff)))
		labels.append(self.debug_font.render("pressed_b: "+str(self.controller.pressed_b), 0, (0xff,0xff,0xff)))
		labels.append(self.debug_font.render("held_b: "+str(self.controller.held_b), 0, (0xff,0xff,0xff)))
		labels.append(self.debug_font.render("pressed_x: "+str(self.controller.pressed_x), 0, (0xff,0xff,0xff)))
		labels.append(self.debug_font.render("held_x: "+str(self.controller.held_x), 0, (0xff,0xff,0xff)))
		
		for i, label in enumerate(labels):
			label.set_alpha(160)
			self.display.blit(label, (10, 10 + (i * self.debug_font.get_height()))) 

	def update(self):
	
		self.clock.tick(self.fps)
		self.tick = (self.tick + 1) % 4294967296
		
		pygame.event.pump()
		self.controller.update()
		
		for obj in self.obj_stack:
			if getattr(obj, "update", None): obj.update()
		
		if self.script:
			self.script(self) # script
		
		self.fader.update()
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_F1: self.debug_info_on = -self.debug_info_on

	def render(self):
	
		for obj in self.obj_stack:
			if getattr(obj, "render", None):
				obj.render()
			else:
				self.display.blit(obj, (0,0))
				
		self.fader.render()
		
		if self.debug_info_on == 1: self.draw_debug_info()
		
		pygame.display.flip()
					
class Controller:

	buttons = ["a", "b", "x"] # ["a","b","x","y"]

	def __init__(self, game):
	
		self.game = game
		
		self.x_axis = self.y_axis = 0
		self.x_repeat = self.y_repeat = False
		self.x_pressed = self.y_pressed = False # USE THESE!!! Yes but actually no
		self.x_tick = self.y_tick = 0
		
		self.y_axis_sr = 0 # special repeat; delayed repeat
		self.y_axis_phase1 = 0 # for the first, and longer, delay
		self.y_axis_phase2 = 0 # for the constant and shorter delay
		
		# buttons: A, B, X, Y
		self.pressed_a_held = False
		self.pressed_a = 0
		self.held_a = 0
		
		self.pressed_b_held = False
		self.pressed_b = 0
		self.held_b = 0
		
		self.pressed_x_held = False
		self.pressed_x = 0
		self.held_x = 0
		
		self.exit = 0
		
		self.pressed_f1 = False
		
	def press(self, button):
	
		#print("pressing "+button)
	
		attribute = "pressed_"+button
		setattr(self, attribute, 1)
		setattr(self, attribute+"_held", True)

	def flush(self):
		
		for button in self.buttons: setattr(self, "pressed_"+button, 0)
		self.exit = 0
		self.y_axis_sr = 0
		
	def base_update(self):
	
		if self.x_axis != 0 and not self.x_pressed:
			self.x_tick = pygame.time.get_ticks()
			self.x_pressed = True
		elif self.x_axis == 0 and self.x_pressed:
			self.x_pressed = False
		self.x_repeat = self.x_pressed and (pygame.time.get_ticks() - self.x_tick >= 800)
		
		if self.y_axis != 0 and not self.y_pressed:
			self.y_pressed = True
			self.y_tick = pygame.time.get_ticks()
			self.y_axis_sr = 1 # special repeat
			self.y_axis_phase1 = 1
		
		if self.y_pressed:
			if self.y_axis_phase1:
				if pygame.time.get_ticks() - self.y_tick >= 800:
					self.y_axis_phase2 = 1
					self.y_axis_phase1 = 0
					self.y_tick = pygame.time.get_ticks()
			elif self.y_axis_phase2:
				if pygame.time.get_ticks() - self.y_tick >= 100:
					self.y_axis_sr = 1
					self.y_tick = pygame.time.get_ticks()
				
		if self.y_axis == 0 and self.y_pressed:
			self.y_pressed = False

	def y_ax_sr(self):
	
		return self.y_axis_sr * self.y_axis

class Gamepad(Controller):

	def __init__(self, game_obj):
	
		Controller.__init__(self, game_obj)
		
		self.interface = pygame.joystick.Joystick(0)
		self.interface.init()
		
	def update(self):
	
		self.x_axis = round(self.interface.get_axis(0))
		self.y_axis = round(self.interface.get_axis(1))
		
		self.flush()
		
		self.held_a = self.interface.get_button(1)
		self.held_b = self.interface.get_button(2)
		self.held_x = self.interface.get_button(0)

		if self.interface.get_button(1) and not self.pressed_a_held:
			self.press("a")
		elif not self.interface.get_button(1) and self.pressed_a_held:
			self.pressed_a_held = False
		if self.interface.get_button(2) and not self.pressed_b_held:
			self.press("b")
		elif not self.interface.get_button(2) and self.pressed_b_held:
			self.pressed_b_held = False
		if self.interface.get_button(0) and not self.pressed_x_held:
			self.press("x")
		elif not self.interface.get_button(0) and self.pressed_x_held:
			self.pressed_x_held = False
			
		if self.interface.get_button(4) and self.interface.get_button(5): self.exit = 1
		
		self.base_update()

class Keyboard(Controller):

	def __init__(self, game):
	
		Controller.__init__(self, game)
			
	def update(self):
		
		keys = pygame.key.get_pressed()
		
		self.x_axis = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT] 
		self.y_axis = keys[pygame.K_DOWN] - keys[pygame.K_UP]
		
		self.flush()
			
		#self.pressed_a = 0
		self.held_a = keys[pygame.K_RCTRL]
		self.held_b = keys[pygame.K_RSHIFT]
		self.held_x = keys[pygame.K_RETURN]
		
		if keys[pygame.K_RCTRL] == 1 and not self.pressed_a_held:
			self.press("a")
		elif keys[pygame.K_RCTRL] == 0 and self.pressed_a_held:
			self.pressed_a_held = False
		if keys[pygame.K_RSHIFT] == 1 and not self.pressed_b_held:
			self.press("b")
		elif keys[pygame.K_RSHIFT] == 0 and self.pressed_b_held:
			self.pressed_b_held = False
		if keys[pygame.K_RETURN] == 1 and not self.pressed_x_held:
			self.press("x")
		elif keys[pygame.K_RETURN] == 0 and self.pressed_x_held:
			self.pressed_x_held = False
					
		if keys[pygame.K_ESCAPE] == 1: self.exit = 1
			
		self.base_update()
		
class Camera(pygame.Rect):

	def __init__(self, uid, game, x=0, y=0):
	
		self.uid = uid
		self.game = game
		w,h = self.game.display.get_size()
		pygame.Rect.__init__(self, (x,y,w,h))
		
		self.tilesize = 0 # TODO where does this get set?
		self.cols = 0
		self.rows = 0
		self.blank = None
		self.following = None
		
		self.scene_obj = None
		
	def tile_prep(self, layer, col, row):

		x_offset = self.x % self.tilesize
		y_offset = self.y % self.tilesize

		c_index = int(self.x / self.tilesize + col)
		r_index = int(self.y / self.tilesize + row)
	
		index = self.scene_obj.get_tile(layer, c_index, r_index)

		x = col * self.tilesize - x_offset
		y = row * self.tilesize - y_offset
		
		if index != "0":
			tile = self.scene_obj.tileset_obj[index]
			return (tile, x, y)
		else:			
			return ("0", x, y)
	
	def y_sort(self): return sorted(self.game.scene_obj.live_mobs.values(), key=operator.attrgetter('y'))
			
	def update(self):
	
		x,y = self.following.center
		
		if x > self.w / 2:
			self.x = x - self.w / 2
		elif x <= self.w / 2:
			self.x = 0
		
		if y > self.h / 2:
			self.y = y - self.h / 2
		elif y <= self.h / 2:
			self.y = 0
	
		if self.x + self.w > self.game.scene_obj.cols * self.tilesize:
			self.x = self.game.scene_obj.cols * self.tilesize - self.w
		elif self.x < 0:
			self.x = 0
			
		if self.y + self.h > self.game.scene_obj.rows * self.tilesize:
			self.y = self.game.scene_obj.rows * self.tilesize - self.h
		elif self.y < 0:
			self.y = 0

	def render(self):
	
		for row in range(self.rows): # draw the bottom and middle tile layers
			for col in range(self.cols):
				x_offset = self.x % self.tilesize
				y_offset = self.y % self.tilesize

				c_index = int(self.x / self.tilesize + col)
				r_index = int(self.y / self.tilesize + row)
		
				bottom_i = self.scene_obj.get_tile("bottom", c_index, r_index)
				middle_i = self.scene_obj.get_tile("middle", c_index, r_index)

				c = col * self.tilesize - x_offset
				r = row * self.tilesize - y_offset
				
				if bottom_i != "0":
					bottom_t = self.scene_obj.tileset_obj[bottom_i]
					self.game.display.blit(bottom_t, (c,r))
				elif bottom_i == "0":
					self.game.display.blit(self.blank, (c,r))

				if middle_i != "0":
					middle_t = self.scene_obj.tileset_obj[middle_i]
					self.game.display.blit(middle_t, (c,r))

		#if self.scene_obj.loot: # TODO merge this with sprites for the y_sort
		#	for loot in self.scene_obj.loot.values():
		#		loot.render(self.game.display, x_offset = -self.x, y_offset = -self.y)

		if self.game.scene_obj.live_mobs: # draw the sprites
			#for sprite in self.scene_obj.sprites.values():
			for sprite in self.y_sort():
				sprite.render(self.game.display, x_offset = -self.x, y_offset = -self.y)
		
		for row in range(self.rows): # draw the top layer
			for col in range(self.cols):
				tile, x, y = self.tile_prep("top", col, row)
				if tile != "0": self.game.display.blit(tile, (x, y))
		
		if self.game.debug_info_on == 1:
			r = (self.game.player.action.x - self.x, self.game.player.action.y - self.y, self.game.player.action.w, self.game.player.action.h)
			pygame.draw.rect(self.game.display, (0xff,0,0), r, 1)
				
class Fader: # TODO make a white version

	def __init__(self, game, size):
	
		self.game = game
		self.curtain = pygame.Surface(size)
		self.curtain.fill((0,0,0))
		self.opacity = 0
		self.curtain.set_alpha(self.opacity)
		
		self.speed = 0
		self.velocity = -self.speed
		self.faded_in = False # as in a cycle
		self.faded_out = False
		self.fading = False
	
	def fade_out(self, speed=6):
	
		self.speed = speed
		self.opacity = 0
		self.curtain.set_alpha(self.opacity)
		self.fading = True
		self.velocity = self.speed
		self.game.script = self.game.fade_loop
		
	def fade_in(self, speed=6):
		
		self.speed = speed
		self.opacity = 255
		self.curtain.set_alpha(self.opacity)
		self.fading = True
		self.velocity = -self.speed
		self.game.script = self.game.fade_loop
		
	def update(self):
	
		if self.faded_in:
			self.faded_in = False
		if self.faded_out:
			self.faded_out = False
		
		if self.fading:		
			self.opacity += self.velocity
			
			if self.opacity <= 0:
				self.opacity = 0
				self.faded_in = True
			elif self.opacity >= 255:
				self.opacity = 255
				self.faded_out = True
			
			self.curtain.set_alpha(self.opacity)

			if self.faded_in or self.faded_out:
				self.fading = False
				
	def render(self):
	
		self.game.display.blit(self.curtain,(0,0))

