# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
from collections import OrderedDict

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

import config_reader
import project_creator

# Global
def deleteItemsOfLayout(layout):
     if layout is not None:
         while layout.count():
             item = layout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                 widget.setParent(None)
             else:
                 deleteItemsOfLayout(item.layout())

DEFAULT_JOBS_DIR = "V:\\Jobs"
CONFIG_FILE_NAME = "config.yml"
LOCAL_CONFIG_PATH = os.path.expanduser('~/carbonLocalConfig.yml')

class ProjectLauncher(QtGuiWidgets.QDialog):

	def __init__(self, activeWindow, software):
		super(ProjectLauncher, self).__init__(activeWindow)
		self.software = software
		self.token_obj_dict = OrderedDict()
		self.jobs_dir = DEFAULT_JOBS_DIR
		self.current_job_path = ""
		self.extensions = []
		self.template = ""
		self.finalPath = ""

		self.configReader = None
		self.initUI()
		self.populate_jobs()
		self.show()

	def initUI(self):
		print("initializing...")

		element_list = ["spot", "shot", "step"]

		self.job_combo = QtGuiWidgets.QComboBox()
		self.job_combo.activated[str].connect(self.on_job_change)
		self.profile_combo = QtGuiWidgets.QComboBox()
		self.profile_combo.activated[str].connect(self.on_profile_change)

		form_layout = QtGuiWidgets.QFormLayout()
		form_layout.addRow("Job", self.job_combo)
		form_layout.addRow("Profile", self.profile_combo)
		form_widget = QtGuiWidgets.QWidget()
		form_widget.setLayout(form_layout)
		form_widget.setFixedWidth(300)

		self.token_grid = QtGuiWidgets.QGridLayout()

		self.file_label = QtGuiWidgets.QLabel("File")
		self.file_list_widget = QtGuiWidgets.QListWidget()
		self.file_list_widget.currentTextChanged.connect(self.on_file_change)
		self.file_line_edit = QtGuiWidgets.QLineEdit()
		self.file_line_edit.textEdited.connect(self.on_file_line_change)

		self.file_vbox = QtGuiWidgets.QVBoxLayout()
		self.file_vbox.addWidget(self.file_label)
		self.file_vbox.addWidget(self.file_list_widget)
		self.file_vbox.addWidget(self.file_line_edit)

		self.path_label = QtGuiWidgets.QLabel()

		# Launch and cancel buttons ------------------------------------------------------
		self.launchButton = QtGuiWidgets.QPushButton("Launch")
		self.launchButton.setEnabled(False)
		self.launchButton.clicked.connect(self.on_launch_click)

		cancelButton = QtGuiWidgets.QPushButton("Cancel")
		cancelButton.clicked.connect(self.close)

		hbox = QtGuiWidgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.launchButton)
		hbox.addWidget(cancelButton)

		vbox = QtGuiWidgets.QVBoxLayout()
		vbox.addWidget(form_widget)
		vbox.addLayout(self.token_grid)
		vbox.addWidget(self.path_label)
		vbox.addLayout(hbox)
		self.setLayout(vbox)


		self.resize(800,400)
		self.setWindowTitle(self.software.capitalize() + " Project Launcher") 

	def populate_jobs(self):
		"""Look in jobs folder for jobs that contain the config file at root"""
		jobsList = self.getDirList(self.jobs_dir)
		jobsList[:] = [job for job in jobsList if os.path.isfile(os.path.join(self.jobs_dir, job, CONFIG_FILE_NAME))]
		self.job_combo.clear()
		self.job_combo.addItems(jobsList)
		self.on_job_change(jobsList[0])

	def populate_profiles(self):
		profileList = self.configReader.getLauncherProfiles(self.software).keys()
		self.profile_combo.clear()
		self.profile_combo.addItems(profileList)
		profile = ""
		# Check if any profiles exist
		if len(profileList) > 0:
			profile = profileList[0]
		self.on_profile_change(profile)

	def on_job_change(self, job):
		self.current_job_path = os.path.join(self.jobs_dir, job)
		self.configReader = config_reader.ConfigReader(self.current_job_path)

		# check software support for current job
		if self.configReader.checkSoftwareSupport(self.software):
			self.extensions = self.configReader.getExtensions(self.software)
			self.populate_profiles()
		else:
			self.token_obj_dict.clear()
			self.profile_combo.clear()
			self.template = ""
			self.create_token_grid([])
			self.debugMsg("Project does not include support for this software")

		print("setting path_label to :" + self.current_job_path)
		self.path_label.setText(self.current_job_path)

	def on_profile_change(self, profile):
		self.template = self.configReader.getProfileTemplate(self.software, profile)
		token_list = self.configReader.getTokens(self.template)
		self.create_token_grid(token_list)
		print(profile)

	def create_token_grid(self, token_list):

		self.token_obj_dict.clear()
		self.populate_file()

		for token in token_list:
			token_obj = Token(self, token)
			index = token_list.index(token)
			self.token_obj_dict[token] = token_obj

		deleteItemsOfLayout(self.token_grid)

		for index, token in enumerate(token_list):
			token_obj = Token(self, token)
			self.token_obj_dict[token] = token_obj
			self.token_grid.addWidget(token_obj.label, 0, index)
			self.token_grid.addWidget(token_obj.list_widget, 1, index)
			self.token_grid.addWidget(token_obj.add_button, 2, index)

		self.token_grid.addWidget(self.file_label, 0, len(token_list))
		self.token_grid.addWidget(self.file_list_widget, 1, len(token_list))
		self.token_grid.addWidget(self.file_line_edit, 2, len(token_list))

		print("This is it: " + str(self.token_obj_dict.keys()))
		if len(self.token_obj_dict) > 0:
			self.populate_token(self.token_obj_dict.keys()[0])

	def launchProject(self, filePath):
		print("Oh, I get it...")
		self.close()

	def on_launch_click(self):

		currentPath = self.configReader.getPath(self.template, self.get_token_dict())
		self.finalPath = os.path.join(currentPath, self.file_line_edit.text())

		# If the file doesn't exist, create it with project_creator
		if not os.path.isfile(self.finalPath):
			print("This file doesn't exist! " + self.finalPath)
			project_creator.createProject(self.configReader, self.template, self.get_token_dict(), self.software, self.file_line_edit.text())

		self.launchProject(self.finalPath)			
		# self.saveRecents()

	def on_token_change(self, token, text):
		currentPath = self.configReader.getPath(self.template, self.get_token_dict(), token)
		self.path_label.setText(os.path.join(currentPath, self.token_obj_dict[token].get_current()))

		self.launchButton.setEnabled(False)

		print(token + " changed to " + text)

		index = self.token_obj_dict.keys().index(token)

		if (len(self.token_obj_dict) > index+1):
			next_token = self.token_obj_dict.keys()[index+1]
			self.populate_token(next_token)
			print(next_token)
		else:
			# self.populate_file()
			print("oops, last one")

		self.populate_file()


	def on_token_button(self, token):
		print(token + " clicked")
		new_token, ok = QtGuiWidgets.QInputDialog.getText(self, "Create Token", ("Create New " + token.capitalize()), QtGuiWidgets.QLineEdit.Normal, ("new_" + token))
		if ok and new_token:
			print("text = " + new_token)
		    # textLabel.setText(text)
			project_creator.createToken(self.configReader, self.template, self.get_token_dict(), token, new_token)
			self.populate_token(token)

	def debugMsg(self, msg):
		'''Override this to customize how each software prints debug reports.'''
		print(msg)


	def getDirList(self, directory, reverse=False):
		"""Returns a sorted list of directories in a given directory with an optional flag to reverse the order."""
		try:
			dirs = [name for name in os.listdir(directory)
					if os.path.isdir(os.path.join(directory, name))]
		except:
			return []
		return sorted(dirs, reverse=reverse)


	def getFileList(self, directory, extensions, reverse=False):
		"""Returns a sorted list of files with a given extension in a given directory with an optional flag to reverse the order."""
		try:
			files = [name for name in os.listdir(directory)
					if (not os.path.isdir(os.path.join(directory, name))) & name.lower().endswith(tuple(extensions))]
		except:
			return []
		return sorted(files, reverse=reverse)

	def populate_token(self, token):
		token_obj = self.token_obj_dict[token]
		token_dict = self.get_token_dict()
		print("Token dict: " + str(token_dict))
		populate_path = self.configReader.getPath(self.template, self.get_token_dict(), token)

		folderList = self.getDirList(populate_path)
		excludeList = self.configReader.getExcludes(token)

		# Remove any occurances of excludeList from folderList
		folderList = [x for x in folderList if x not in excludeList]

		# Remove template folder from list
		tokenFolder = "[" + token + "]"
		if tokenFolder in folderList:
			folderList.remove(tokenFolder)

		token_obj.set_list(folderList)


	def populate_file(self):
		self.file_list_widget.clear()

		try:
			token_dict = self.get_token_dict()
			populatePath = self.configReader.getPath(self.template, token_dict)
			file_list = self.getFileList(populatePath, self.extensions)
			print("IT STILL WORKED?????????????????????????")
		except:
			print("WHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
			file_list = []
		# self.debugMsg("Trying to pupulate file box at this location: " + str(populatePath))
		if len(file_list) > 0:
			for index, file in enumerate(file_list):
				current_item = QtGuiWidgets.QListWidgetItem(file, self.file_list_widget)
				# Set to latest version
				if (index+1 >= len(file_list)):
					print("IT IS THE OF OF")
					self.file_list_widget.setCurrentItem(current_item)
					self.on_file_change(file)
				else:
					self.on_file_change("")


	def on_file_change(self, file):
		self.file_line_edit.setText(file)
		self.on_file_line_change(file)

	def on_file_line_change(self, file):
		print("File = " + file)
		if file:
			currentPath = self.configReader.getPath(self.template, self.get_token_dict())
			self.finalPath = os.path.join(currentPath, self.file_line_edit.text())
			print(self.finalPath)
			self.path_label.setText(self.finalPath)

		if file: 
			self.launchButton.setEnabled(True)

	def get_token_dict(self):
		token_dict = dict()
		for token_obj in self.token_obj_dict:
			token_value = self.token_obj_dict[token_obj].get_current()
			if token_value is not None:
				token_dict[token_obj] = token_value
		return token_dict
			


class Token():

	def __init__(self, parent, token):
		self.parent = parent
		self.token = token
		self.current_text = None
		tokenString = token.lower().capitalize()
		self.label = QtGuiWidgets.QLabel(tokenString)
		self.list_widget = QtGuiWidgets.QListWidget()
		self.list_widget.currentTextChanged.connect(self.on_token_change)
		self.add_button = QtGuiWidgets.QPushButton("New " + tokenString)
		self.add_button.clicked.connect(self.on_token_button)


	def on_token_change(self, text):
		self.current_text = text
		self.parent.on_token_change(self.token, text)

	def on_token_button(self):
		self.parent.on_token_button(self.token)

	def set_list(self, options_list):
		self.list_widget.clear()
		for element in options_list:
			QtGuiWidgets.QListWidgetItem(element, self.list_widget)

	def get_current(self):
		return self.current_text


# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = ProjectLauncher(app.activeWindow(), 'houdini')
	app.exec_()