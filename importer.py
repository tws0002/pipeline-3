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


class Importer(navigator.Navigator):

	def __init__(self, active_window, software):
		print("hi!")
		super(Importer, self).__init__(active_window, software)
		self.load_recents()
		self.setWindowTitle(self.software.capitalize() + " Importer") 
		self.debugMsg("Starting importer dodad...")
	

	def create_execute_button(self):
		execute_button = QtGuiWidgets.QPushButton("Import")
		execute_button.setEnabled(False)
		execute_button.clicked.connect(self.on_import_click)
		return execute_button

	def on_import_click(self):
		self.debugMsg("Trying to launch project")
		"""Called when the import button is clicked. Attempts to import file with child's 'import_file' function."""
		currentPath = self.configReader.getPath(self.template, self.get_token_dict())
		self.finalPath = os.path.join(currentPath, self.file_line_edit.text())

		# Check if file exists
		if not os.path.isfile(self.finalPath):
			QtGuiWidgets.QMessageBox.information(self, "File Doesn't Exist", "Please select an existing file")
		else:
			if self.import_file(self.finalPath):
				self.close()


	def import_file(self, file_path):
		"""Just a placeholder. Should be overridden by child."""
		self.debugMsg("Here we go!")
		return True

	def get_extensions(self):
		return []
# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Importer(app.activeWindow(), 'maya')
	app.exec_()
