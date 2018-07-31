# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import re
import importlib
import imp
import publisher
import environment

from shutil import copyfile

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
		raise NotImplementedError

	def increment_version(self, path):
		""" Attempts to increment all the instances of a version number in the provided path. """
		try:
			version = self.get_version_str(path)
		except:
			raise
		increment_ver = str(int(version) + 1).zfill(len(version))
		new_path = re.sub(REG_VERSION_PATTERN, increment_ver, path)

		return new_path

	def create_pub_name(self, name):
		# Make a list of tuples for all instances of the reg_version_pattern
		ver_index_list = [m.span() for m in re.finditer(REG_VERSION_PATTERN, name)]
		if len(ver_index_list) < 1:
			new_name, ext = os.path.splitext(name)
			new_name = new_name + '_PUBLISH' + ext
		elif len(ver_index_list) == 1:
			first_index, last_index = ver_index_list[0]
			# decrement first_index to account for 'v' in version
			first_index = first_index-1
			new_name = name[:first_index] + 'PUBLISH' + name[last_index:]
		else:
			raise ValueError

		return new_name

	def get_version_str(self, path, padded=True):
		""" Attemps to return the version number of the path as a string. 
		By default it is padded in its original format. 
		"""
		# Find all instances of v###*
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
		""" Given a path this will version up the file and return the incremented path if the 
		file doesn't already exist, or if the user chooses to overwrite the existing file. 
		"""
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

		if self.save_project_as(path):
			return path
		else:
			return ''

	def save_project_as(self, path):
		""" If the file already exists it asks the user if it can be replaced. Returns true 
		if it can be replaced. 
		"""
		if os.path.isfile(path):
			ok_button = QtGuiWidgets.QMessageBox.Ok
			cancel_button = QtGuiWidgets.QMessageBox.Cancel

			msgBox = QtGuiWidgets.QMessageBox()
			msgBox.setText("File Already Exists")
			msgBox.setInformativeText("This file already exists. Are you sure you want to"
										" overwrite it?\n\n" + path)
			msgBox.setIcon(QtGuiWidgets.QMessageBox.Warning)
			msgBox.setStandardButtons(ok_button | cancel_button)
			msgBox.setDefaultButton(ok_button)
			ret = msgBox.exec_()

			if ret == ok_button:
				return self._save_as(path)
			else:
				return False
		else:
			return self._save_as(path)

	def save_project(self):
		return self._save()
	
	def file_not_saved_dlg(self):
		""" Open this dialog if the file has unsaved changes.
		Returns true or false if the user wants to save. 
		"""
		save_button = QtGuiWidgets.QMessageBox.Save
		cancel_button = QtGuiWidgets.QMessageBox.Cancel

		msgBox = QtGuiWidgets.QMessageBox()
		msgBox.setText("File has unsaved changes")
		msgBox.setInformativeText("Cannot continue with unsaved changes. Would you like"
									" to save the current file?")
		msgBox.setIcon(QtGuiWidgets.QMessageBox.Warning)
		msgBox.setStandardButtons(save_button | cancel_button)
		msgBox.setDefaultButton(save_button)
		ret = msgBox.exec_()

		if ret == save_button:
			return True
		else:
			return False

	def publish(self):
		# Check that the environment is valid
		if environment.is_valid(software=self.get_software()):
			# Check if the file has been modified
			if self.is_project_modified():
				if self.file_not_saved_dlg():
					self.save_project()
				else:
					return False
			
			# Define directories
			proj_dir = os.path.dirname(self.get_project_path())
			self.debugMsg("project basename = " + os.path.basename(self.get_project_path()))
			archive_dir = os.path.join(proj_dir, 'archive')
			publish_dir = os.path.join(proj_dir, 'publish')

			# Create archive directory if it doesn't exist
			try:
				os.makedirs(archive_dir)
			except OSError:
				if not os.path.isdir(archive_dir):
					raise

			# Append 'PUBLISH' to file before archiving it
			archive_name, ext = os.path.splitext(os.path.basename(self.get_project_path()))
			archive_name = archive_name + '_PUBLISH'
			archive_name = archive_name + ext

			copyfile(self.get_project_path(), os.path.join(archive_dir, archive_name))

			# Create publish name
			pub_name = self.create_pub_name(os.path.basename(self.get_project_path()))

			publisher_dlg = publisher.Publisher(publish_dir, pub_name)
			if publisher_dlg.exec_():
				# Create publish folder if it doesn't exist
				try:
					os.makedirs(publish_dir)
				except OSError:
					if not os.path.isdir(publish_dir):
						raise

				pub_name = publisher_dlg.get_name()
				# If a valid name comes back from the dialog, copy it to the publish directory
				if pub_name:
					copyfile(self.get_project_path(), os.path.join(publish_dir, pub_name))
		else:
			self.debugMsg("Environment is not valid!")

	def get_project_path(self):
		raise NotImplementedError

	def get_software(self):
		raise NotImplementedError

	def is_project_modified(self):
		raise NotImplementedError

	def _save(self):
		raise NotImplementedError

	def _save_as(self, path):
		raise NotImplementedError

	def set_environment(self, config_reader, template, token_dict):
		pass

	def open_project(self, path):
		raise NotImplementedError

# DEBUGGING------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	path = 'V:/Jobs/182276_Essilor_Out_of_Focus/Design/Production/TVC60/Assets/Environments/Gym/model/esof_gym_model_V05.ma'
	app = QtGuiWidgets.QApplication(sys.argv)
	print(SoftwareTools().version_up(path))
	# print(get_version_str(path, False))
	# print(get_version_int(path))
