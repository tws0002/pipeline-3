# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import re
import importlib
import imp

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


REG_VERSION_PATTERN = r'(?<=(?i)_v)\d+'

class SoftwareTools(object):

	def debugMsg(self, msg):
		print('woohoo!' + msg)

	def increment_version(self, path):
		""" Attempts to increment all the instances of a version number in the provided path.  """
		try:
			version = self.get_version_str(path)
		except:
			raise
		increment_ver = str(int(version) + 1).zfill(len(version))
		new_path = re.sub(REG_VERSION_PATTERN, increment_ver, path)

		return new_path

	def get_version_str(self, path, padded=True):
		""" Attemps to return the version number of the path as a string. By default it is padded in its original format. """
		# Find all instances of v###
		reg_pattern = r'(?<=_v)\d+'
		ver_list = re.findall(REG_VERSION_PATTERN, path)

		# Check that there are no conflicting versions in the path
		if all(x == ver_list[0] for x in ver_list) and len(ver_list) > 0:
			version = ver_list[0]
			if padded:
				return version
			else:
				return version.lstrip('0')
		else:
			raise ValueError(
				"There are conflicting version numbers in this path or none at all: " + path)

	def get_version_int(self, path):
		try:
			return int(self.get_version_str(path))
		except:
			raise

	def version_up(self, path, only_filename=False):
		""" Given a path this will version up the file and return the incremented path if the file doesn't already exist, or if the user chooses to overwrite the existing file. """
		directory = os.path.dirname(path)
		if only_filename:
			path = os.path.basename(path)

		# Attempt to version up the file
		try:
			path = self.increment_version(path)
		except:
			raise

		# If we previously stripped of the filename, add the path back to the beginning
		if only_filename and directory:
			path = os.path.join(directory, path)

		if self.save_file(path):
			return path
		else:
			return ''

	def save_file(self, path):
		""" If the file already exists it asks the user if it can be replaced. Returns true if it can be replaced. """
		if os.path.isfile(path):
			ok_button = QtGuiWidgets.QMessageBox.Ok
			cancel_button = QtGuiWidgets.QMessageBox.Cancel

			msgBox = QtGuiWidgets.QMessageBox()
			msgBox.setText("File Already Exists")
			msgBox.setInformativeText("This file already exists. Are you sure you want to overwrite it?\n\n" + path)
			msgBox.setIcon(QtGuiWidgets.QMessageBox.Warning)
			msgBox.setStandardButtons(ok_button | cancel_button)
			msgBox.setDefaultButton(ok_button)
			ret = msgBox.exec_()

			if ret == ok_button:
				return True
			else:
				return False
		else:
			return True
		
	
	def file_not_saved_dlg(self):
		""" Open this dialog if the file has unsaved changes. Returns true or false if the user wants to save. """
		save_button = QtGuiWidgets.QMessageBox.Save
		cancel_button = QtGuiWidgets.QMessageBox.Cancel

		msgBox = QtGuiWidgets.QMessageBox()
		msgBox.setText("File has unsaved changes")
		msgBox.setInformativeText("Cannot continue with unsaved changes. Would you like to save the current file?")
		msgBox.setIcon(QtGuiWidgets.QMessageBox.Warning)
		msgBox.setStandardButtons(ok_button | cancel_button)
		msgBox.setDefaultButton(ok_button)
		ret = msgBox.exec_()

		if ret == ok_button:
			return True
		else:
			return False


# DEBUGGING------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	path = 'V:/Jobs/182276_Essilor_Out_of_Focus/Design/Production/TVC60/Assets/Environments/Gym/model/esof_gym_model_V05.ma'
	app = QtGuiWidgets.QApplication(sys.argv)
	print(SoftwareTools().version_up(path))
	# print(get_version_str(path, False))
	# print(get_version_int(path))
