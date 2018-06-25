# -*- coding: utf-8 -*-
# Adam Thompson 2018

import project_launcher
import hou

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

SOFTWARE = "houdini"

class HoudiniProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(HoudiniProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()
		self.debugMsg("Setting environment variables: ")
		for token in tokenDict:
			os.environ[token] = tokenDict[token]
			self.debugMsg(token + " = " + tokenDict[token])

		self.debugMsg("Here we go!")
		hou.allowEnvironmentToOverwriteVariable("JOB", True)
		hou.putenv("JOB", "COOL DUDE")
		forwardSlashPath = filePath.replace('\\', '/')
		hou.hipFile.load(forwardSlashPath)
		return True

	def debugMsg(self, msg):
		print(msg)