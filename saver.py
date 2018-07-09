# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys

import navigator

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


class Saver(navigator.Navigator):

	def __init__(self, active_window, software):
		super(Saver, self).__init__(active_window, software)
		self.setWindowTitle(self.software.capitalize() + " Saver") 
		self.debugMsg("Starting saver...")
	
	def create_execute_button(self):
		execute_button = QtGuiWidgets.QPushButton("Save")
		execute_button.setEnabled(False)
		execute_button.clicked.connect(self.on_save_click)
		return execute_button

	def on_save_click(self):
		self.debugMsg("Trying to save project")
		"""Called when the save button is clicked. Attempts to save file with child's 'save_file' function."""
		currentPath = self.configReader.getPath(self.template, self.get_token_dict())
		self.finalPath = os.path.join(currentPath, self.file_line_edit.text())


		# Check if file exists
		if os.path.isfile(self.finalPath):
			ok_button = QtGuiWidgets.QMessageBox.Ok
			cancel_button = QtGuiWidgets.QMessageBox.Cancel
			ret = QtGuiWidgets.QMessageBox.information(self, "File Already Exists", "This file already exists. Are you sure you want to overwrite it?", ok_button, cancel_button)

			if ret == ok_button:
				if self.save_file(self.finalPath):
					self.close()

		else:
			if self.save_file(self.finalPath):
				self.close()


	def save_file(self, file_path):
		"""Just a placeholder. Should be overridden by child."""
		self.debugMsg("Saving!")
		return True

	def get_extensions(self):
		return []

# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Saver(app.activeWindow(), 'maya')
	app.exec_()
