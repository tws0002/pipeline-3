# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import re

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


REG_VERSION_PATTERN = r'(?<=_v)\d+'

def increment_version(path):
	""" Attempts to increment all the instances of a version number in the provided path.  """
	try:
		version = get_version_str(path)
	except:
		raise
	increment_ver = str(int(version) + 1).zfill(len(version))
	new_path = re.sub(REG_VERSION_PATTERN, increment_ver, path)
	
	return new_path


def get_version_str(path, padded=True):
	""" Attemps to return the version number of the path as a string. By default it is padded in its original format. """
	# Find all instances of v###
	reg_pattern = r'(?<=_v)\d+'
	ver_list = re.findall(REG_VERSION_PATTERN, path)

	# Check that there are no conflicting versions in the path
	if all(x==ver_list[0] for x in ver_list) and len(ver_list) > 0:
		version = ver_list[0]
		if padded:
			return version
		else:
			return version.lstrip('0')
	else:
		raise ValueError("There are conflicting version numbers in this path or none at all: " + path)

def get_version_int(path):
	try:
		return int(get_version_str(path))
	except:
		raise

def save_file(path):
	""" If the file exists it promps the user with a dialog box asking if they would like to replace it. Returns true if they accept, or the file didn't exist in the first place. """
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
	

def version_up(path, only_filename=False):
	""" Given a path this will version up the file and return the incremented path if the file doesn't already exist, or if the user chooses to overwrite the existing file. """
	directory = os.path.dirname(path)
	if only_filename:
		path = os.path.basename(path)

	# Attempt to version up the file
	try:
		path = increment_version(path)
	except:
		raise

	# If we previously stripped of the filename, add the path back to the beginning
	if only_filename and directory:
		path = os.path.join(directory, path)

	if save_file(path):
		return path
	else:
		return ''
		


if __name__ == '__main__':
	path = 'V:/Jobs/182276_Essilor_Out_of_Focus/Design/Production/TVC60/Assets/Environments/Gym/model/esof_gym_model_v02.ma'
	app = QtGuiWidgets.QApplication(sys.argv)
	print(version_up(path))
	# print(get_version_str(path, False))
	# print(get_version_int(path))