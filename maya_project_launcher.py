# -*- coding: utf-8 -*-
# Adam Thompson 2018

import project_launcher

import maya.cmds as cmds

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

SOFTWARE = "maya"
WORKSPACE_FILE = "workspace.mel"
ROOT_TOKENS = ['asset', 'shot']

class MayaProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(MayaProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		self.debugMsg("Starting local maya project launcher...")

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()
		self.debugMsg("Setting environment variables: ")
		for token in tokenDict:
			os.environ[token] = tokenDict[token]
			self.debugMsg(token + " = " + tokenDict[token])

		try: 
			cmds.file(filePath, o=True)
			self.setEnvironment()
			return True
		except RuntimeError:
			self.debugMsg("Hey, this is cool")
			ret = self.fileNotSavedDlg()
			if ret == QtGuiWidgets.QMessageBox.Save:
				cmds.file(save=True)
				cmds.file(filePath, o=True)
				self.setEnvironment()
				return True
			elif ret == QtGuiWidgets.QMessageBox.Discard:
			    cmds.file(new=True, force=True) 
			    cmds.file(filePath, open=True)
			    self.setEnvironment()
			    return True
			elif ret == QtGuiWidgets.QMessageBox.Cancel:
				self.debugMsg("Nevermind...")
				return False

	def debugMsg(self, msg):
		print(msg)

	def fileNotSavedDlg(self):
		msgBox = QtGuiWidgets.QMessageBox()
		msgBox.setText("The document has been modified.")
		msgBox.setInformativeText("Do you want to save your changes?")
		msgBox.setStandardButtons(QtGuiWidgets.QMessageBox.Save | QtGuiWidgets.QMessageBox.Discard | QtGuiWidgets.QMessageBox.Cancel)
		msgBox.setDefaultButton(QtGuiWidgets.QMessageBox.Save)
		ret = msgBox.exec_()
		return ret

	def setEnvironment(self):

		rootToken = ""
		for token in self.get_token_dict():
			if token in ROOT_TOKENS:
				rootToken = token

		self.debugMsg("The last token is: " + rootToken)
		path = os.path.join(self.configReader.getPath(self.template, self.get_token_dict(), rootToken), self.get_token_dict()[rootToken])
		filepath = os.path.join(path, WORKSPACE_FILE)
		self.debugMsg("Trying to load this workspace: " + path)
		if os.path.isfile(filepath):
			self.debugMsg("Loading this workspace: " + path)
			cmds.workspace(path, openWorkspace=True)
		else:
			self.debugMsg("That's not a file, dummy!")
