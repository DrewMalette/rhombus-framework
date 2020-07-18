# entrypoint.py; rename to main.py

import os

import pygame
import core
from core import filepaths

def test_tmx_init(game_obj, filename):

	# eventually I want to replace this with a generic onion sprite
	pygame.display.set_caption(filename)
	game_obj.player = core.Player("Ark", game_obj, os.path.join(filepaths.image_path, "spr_ark2.png"))
	game_obj.load_scene(filename, os.path.join(filepaths.scene_path, filename))
	game_obj.camera.following = game_obj.player
	game_obj.debugging = 1
	
	game_obj.obj_stack = [ game_obj.scene_obj ]
	game_obj.scene_obj.paused = False
	game_obj.next_script = test_tmx_loop
	game_obj.fader.fade_in()
	
def test_tmx_loop(game_obj):

	if game_obj.controller.exit:
		game_obj.next_script = game_obj.exit
		game_obj.fader.fade_out()

def draw_wrapper(pane, surface):

	label = pane.parent.font.render(pane.parent.v_string, 0, (0xff,0xff,0xff))
	
	x = pane.x + ((pane.w - label.get_width()) / 2)
	y = pane.y + ((pane.h - label.get_height()) / 2)
	
	surface.blit(label, (x,y))
	
def draw_inventory(pane, surface): draw_wrapper(pane, surface)
def draw_status(pane, surface): draw_wrapper(pane, surface)
def draw_gear(pane, surface): draw_wrapper(pane, surface)
def draw_save(pane, surface): draw_wrapper(pane, surface)
def draw_quit(pane, surface): draw_wrapper(pane, surface)

def newgame_init(game_obj):

	game_obj.player = core.Player("Ark", game_obj, os.path.join(filepaths.image_path, "spr_ark2.png"))
	game_obj.load_scene("scene1", os.path.join(filepaths.scene_path, "scene_cottage.tmx"))
	game_obj.camera.following = game_obj.player
		
	game_obj.obj_stack = [ game_obj.scene_obj ]
	
	game_obj.next_script = gameplay_loop
	game_obj.fader.fade_in()

def playermenu_init(game_obj):

	game_obj.scene_obj.paused = True
	game_obj.obj_stack = [ game_obj.scene_obj, game_obj.ui["playermenu"] ]
	game_obj.ui["playermenu"].start()
	#game_obj.script = playermenu_loop
	game_obj.script = None

def gameplay_init(game_obj): # returning to gameplay

	game_obj.obj_stack = [ game_obj.scene_obj ]
	game_obj.script = gameplay_loop
	game_obj.scene_obj.paused = False
	
def gameplay_loop(game_obj): # game.script will still exist but only in a minor way
	
	if game_obj.controller.pressed_a:# and not game_obj.player.in_dialogue:
		dialogue = ["Greetings and welcome", "to a sample scene", "for the rhombus", "framework", " ", " "]
		dialogue_init(game_obj, dialogue)
	elif game_obj.controller.pressed_x:
		playermenu_init(game_obj)
		
def dialogue_init(game_obj, dialogue):

	game_obj.obj_stack = [ game_obj.scene_obj, game_obj.ui["dialoguebox"] ]
	game_obj.ui["dialoguebox"].text_list = dialogue
	game_obj.ui["dialoguebox"].start()
	game_obj.script = dialogue_loop
	
def dialogue_loop(game_obj): # I'll have to bind functions to dialogueboxes too

	if game_obj.ui["dialoguebox"]._returned:
		gameplay_init(game_obj)

def title_init(game_obj):

	game_obj.obj_stack = [ game_obj.title_card, game_obj.ui["titleselect"] ]
	
	game_obj.ui["titleselect"].start()
	
	game_obj.music_tracks["titletrack"].play(-1)
	game_obj.next_script = None
	game_obj.fader.fade_in()

def title_newgame(game_obj):

	game_obj.next_script = newgame_init
	game_obj.fader.fade_out()
	
def title_quit(game_obj):

	game_obj.music_tracks["titletrack"].fadeout(1000)
	game_obj.next_script = game_obj.exit
	game_obj.fader.fade_out()

def quit_init(game_obj):

	game_obj.obj_stack = [ game_obj.scene_obj, game_obj.ui["dialoguebox"], game_obj.ui["yesnobox"] ]
	game_obj.scene_obj.paused = True
	
	game_obj.ui["dialoguebox"].text_list = ["Quit to menu?", " ", " "]
	game_obj.ui["dialoguebox"].start(wait_for=game_obj.ui["yesnobox"])
	
	game_obj.script = None

def quit_no(game_obj):

	gameplay_init(game_obj)
	game_obj.ui["dialoguebox"].visible = False
	
def quit_yes(game_obj):

	game_obj.next_script = title_init
	game_obj.music_tracks["titletrack"].fadeout(1000)
	game_obj.fader.fade_out()
	game_obj.ui["dialoguebox"].visible = False
			
def start(filename=None):

	pygame.init()
	pygame.display.set_caption("rhombus 0.0.2 (Jul 12 2020, 18:29:46)")
	game_obj = core.Game()
	
	if filename == None:
		game_obj.title_card = pygame.image.load(os.path.join(filepaths.image_path, "titlecard.png"))
		game_obj.music_tracks["titletrack"] = pygame.mixer.Sound(os.path.join(filepaths.sound_path, "titlemusic.ogg"))
	
		game_obj.ui["dialoguebox"] = core.UI_Dialogue("dialoguebox", game_obj, (170,360,300,100))
		
		title_bindings = { "New Game": title_newgame, "Quit to Desktop": title_quit }
		game_obj.ui["titleselect"] = core.UI_Select("titleselect", game_obj, (245,300,150,54), title_bindings)
		
		quit_bindings = { "No": quit_no, "Yes": quit_yes }
		game_obj.ui["yesnobox"] = core.UI_Select("yesnobox", game_obj, (170,296,54,54), quit_bindings)
		
		menu_bindings = { "Inventory": draw_inventory, "Status": draw_status, "Gear": draw_gear, "Save": draw_save, "Quit": quit_init }
		game_obj.ui["playermenu"] = core.UI_PlayerMenu("playermenu", game_obj, (105,90,120,120), menu_bindings, gameplay_init)
		game_obj.ui["childpane"] = core.UI_SubMenuPane("childpane", game_obj.ui["playermenu"], (300,300))
		
		title_init(game_obj)
	else:
		test_tmx_init(game_obj, filename)

	game_obj.main()

