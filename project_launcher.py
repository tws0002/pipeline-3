# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys

import navigator
import project_creator
import software_tools

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


class ProjectLauncher(navigator.Navigator):

	def __init__(self, active_window, current_software_tools):
		super(ProjectLauncher, self).__init__(active_window, current_software_tools)
		self.extensions = self.configReader.getExtensions(current_software_tools.software)
		print(self.extensions)
		self.load_recents(read_local_config=True)
		self.setWindowTitle(self.software.capitalize() + " Project Launcher") 
		self.current_software_tools.debugMsg("Starting project launcher...")
	
	def launchProject(self, filePath):
		"""Just a placeholder. Should be overridden by child."""
		self.current_software_tools.debugMsg("Here we go!")
		return True

	def create_execute_button(self):
		execute_button = QtGuiWidgets.QPushButton("Launch")
		execute_button.setEnabled(False)
		execute_button.clicked.connect(self.on_launch_click)
		return execute_button

	def on_launch_click(self):
		"""Called when the launch button is clicked. Attempts to launch the project with child's 'launchProject' function"""
		currentPath = self.configReader.getPath(self.template, self.get_token_dict())
		self.finalPath = os.path.join(currentPath, self.file_line_edit.text())

		# If the file doesn't exist, create it with project_creator
		if not os.path.isfile(self.finalPath):
			self.current_software_tools.debugMsg("This file doesn't exist! Creating it here: " + self.finalPath)
			self.finalPath = project_creator.createProject(
				self.configReader, self.template, self.get_token_dict(), self.software, self.file_line_edit.text())

		if self.launchProject(self.finalPath):
			self.save_recents(write_local_config=True)
			self.close()

# Debugging -----------------------------------------------
if __name__== '__main__':
	import maya_tools
	soft_tools = maya_tools.MayaTools()
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = ProjectLauncher(app.activeWindow(), soft_tools)
	app.exec_()
