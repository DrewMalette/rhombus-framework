#!/usr/bin/env python3

import sys
sys.path.append("./")
import importlib

try:
	_, filename = sys.argv
except:
	filename = None

main = importlib.import_module("scripts.main")
main.start(filename)

