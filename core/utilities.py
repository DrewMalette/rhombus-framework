#

import os
import xml.etree.ElementTree as ET

import pygame

from . import mob
from . import filepaths
from . import tileset

def load_image(filename, colourkey=None):

	try:
		image = pygame.image.load(filename)
	except:
		print("failed to load image '{}' ".format(filename))
		return

	image = image.convert()
	if colourkey != None:
		if colourkey == -1:
			colourkey = image.get_at((0,0))
		image.set_colorkey(colourkey, pygame.RLEACCEL)

	return image

def load_mob(filename):

	image = pygame.image.load(filename)
	image.convert()
	image.set_colorkey((255,0,255), pygame.RLEACCEL)
	cell_w, cell_h = image.get_at((0, image.get_height()-1))[:2]
	rect = pygame.Rect((0,0)+image.get_at((1, image.get_height()-1))[:2])
	offsets = image.get_at((2, image.get_height()-1))[:2]
	cols = int(image.get_width() / cell_w)
	rows = int(image.get_height() / cell_h)

	cells = {}
	for row in range(rows):
		for col in range(cols):
			cells[row*cols+col] = image.subsurface((col*cell_w, row*cell_h, cell_w, cell_h))

	return { "cols": cols, "rows": rows, "cells": cells, "rect": rect, "offsets": offsets }

def load_tileset(filename, width, height, firstgid=1):

	image = load_image(filename)
	image.set_colorkey((255,0,255), pygame.RLEACCEL)
	
	gid = int(firstgid)
	textures = {}
	cols = int(image.get_width() / width)
	rows = int(image.get_height() / height)
	for row in range(rows):
		for col in range(cols):
			x = col * width
			y = row * height
			textures[str(gid)] = image.subsurface((x, y, width, height))
			gid += 1
	
	return textures
	
def load_tmx(filename, scene_obj):

	tree = ET.parse(filename)
	root = tree.getroot()
	
	scene_obj.cols = int(root.attrib["width"])
	scene_obj.rows = int(root.attrib["height"])
	
	scene_obj.tilewidth = int(root.attrib["tilewidth"])
	scene_obj.tileheight = int(root.attrib["tileheight"])
	scene_obj.tilesize = scene_obj.tilewidth # assumes a square tile
	
	scene_obj.tileset_obj = tileset.Tileset(scene_obj.tilewidth, scene_obj.tileheight)
	
	for tilesettag in root.iter("tileset"):
		filename = tilesettag.attrib["source"]
		tsxtree = ET.parse(os.path.join(filepaths.scene_path, filename))
		tsxroot = tsxtree.getroot()
		for tsx in tsxroot.iter("tileset"):
			for i in tsx.iter("image"):
				filename = i.attrib["source"]
				firstgid = tilesettag.attrib["firstgid"]
				scene_obj.tileset_obj.update(filename, firstgid)
				
	for layer in root.iter("layer"):
		for data in layer.iter("data"):
			name = layer.attrib['name']
			rawdata = data.text.split(",")
			cleandata = []
			for tile in rawdata:
				cleandata.append(tile.strip())
			scene_obj.layerdata[name] = cleandata
			
	for layer in root.iter("objectgroup"):
		for rect in layer.iter("object"):
			rectattribs = {}
			for v in rect.attrib.keys():
				rectattribs[v] = rect.attrib[v]
			for proptag in rect.iter("properties"):
				for propchild in proptag.iter("property"):
					index = propchild.attrib["name"]
					value = propchild.attrib["value"]
					rectattribs[index] = value
			
			uid = rectattribs["id"]
			col = int(float(rectattribs["x"]) / scene_obj.tilewidth)
			row = int(float(rectattribs["y"]) / scene_obj.tileheight)
			if rectattribs["type"] == "player":
				if scene_obj.game.player is None:
					print("player object is not defined")
					print("exiting")
					pygame.quit()
					exit()
				scene_obj.live_mobs["player"] = scene_obj.game.player
				scene_obj.live_mobs["player"].scene_obj = scene_obj
				scene_obj.live_mobs["player"].place(col, row)
			elif rectattribs["type"] == "switch":
				x = int(float(rectattribs["x"]) / scene_obj.tilewidth) * scene_obj.tilewidth
				y = int(float(rectattribs["y"]) / scene_obj.tileheight) * scene_obj.tileheight
				facing = rectattribs["facing"]
				try:
					c = int(rectattribs["col"])
					r = int(rectattribs["row"])
					scene_obj.switches[uid] = [pygame.Rect((x,y,scene_obj.tilewidth,scene_obj.tileheight)), rectattribs["Filename"], (c,r), facing]
				except:
					#print("defaulting to map defined placement position")
					scene_obj.switches[uid] = [pygame.Rect((x,y,scene_obj.tilewidth,scene_obj.tileheight)), rectattribs["Filename"], None, facing]
			elif rectattribs["type"] == "mob":
				scene_obj.live_mobs[uid] = mob.Mob("content/image/" + rectattribs["Filename"], rectattribs["name"])
				scene_obj.live_mobs[uid].scene_obj = scene_obj
				utilities.place(scene_obj.live_mobs[uid], col, row, scene_obj)
			#elif rectattribs["type"] == "static":
			#	filepath = "content/image/" + rectattribs["Filename"]
			#	name = rectattribs["name"]
			#	scene.sprites[uid] = sprite.Static(filepath, name)
			#	scene.sprites[uid].scene = scene
			#	scene.sprites[uid].place(col,row)
