# -*- coding: utf-8 -*-
# Adam Thompson 2018

import project_launcher

import nuke
import nukescripts

import os

try:
	# < Nuke 11
	import PySide.QtCore as QtCore
	import PySide.QtGui as QtGui
	import PySide.QtGui as QtGuiWidgets
	import PySide.QtUiTools as QtUiTools
except:
	# >= Nuke 11
	import PySide2.QtCore as QtCore
	import PySide2.QtGui as QtGui
	import PySide2.QtWidgets as QtGuiWidgets
	import PySide2.QtUiTools as QtUiTools

SOFTWARE = "nuke"

class NukeProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(NukeProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		nuke.tprint(self.configReader.sayHello())

	def launchProject(self, filePath):
		nuke.tprint("Yeah, it's kinda working")
		tokenDict = self.get_token_dict()
		self.debugMsg("Setting environment variables: ")
		for token in tokenDict:
			os.environ[token] = tokenDict[token]
			self.debugMsg(token + " = " + tokenDict[token])
		nuke.scriptOpen(filePath)
		return True

	def debugMsg(self, msg):
		nuke.tprint(msg)