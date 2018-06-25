# -*- coding: utf-8 -*-
# Adam Thompson 2018

import project_launcher

import os

import MaxPlus

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

SOFTWARE = "max"
WORKSPACE_FILE = "maxWorkspace.mxp"
ROOT_TOKENS = ['asset', 'shot']

class MaxProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(MaxProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()
		self.debugMsg("Setting environment variables: ")
		for token in tokenDict:
			os.environ[token] = tokenDict[token]
			self.debugMsg(token + " = " + tokenDict[token])
		# nuke.scriptOpen(filePath)

		fm = MaxPlus.FileManager
		fm.Open(filePath)
		self.setEnvironment()
		return True

	def debugMsg(self, msg):
		print(msg)

	def setEnvironment(self):
		rootToken = ""
		for token in self.get_token_dict():
			if token in ROOT_TOKENS:
				rootToken = token

		self.debugMsg("The last token is: " + rootToken)
		path = os.path.join(self.configReader.getPath(self.template, self.get_token_dict(), rootToken), self.get_token_dict()[rootToken])
		filepath = os.path.join(path, WORKSPACE_FILE)
		filepath = filepath.replace(os.path.sep, '/')
		self.debugMsg("Trying to load this workspace: " + path)
		if os.path.isfile(filepath):
			self.debugMsg("Loading this workspace: " + path)
			# Create maxscript to run to load project workspace
			maxscript = ('pathConfig.load "' + filepath + '"')
			print("Maxscript to run: " + maxscript)
			MaxPlus.Core.EvalMAXScript(maxscript)
		else:
			self.debugMsg("That's not a file, dummy!")
