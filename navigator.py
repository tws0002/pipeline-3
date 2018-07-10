# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import time
from collections import OrderedDict
import yaml
import ast

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
LOCAL_CONFIG_PATH = os.path.expanduser('~/pipeline_local_config.yml')

class DeselectableTreeWidget(QtGuiWidgets.QTreeWidget):
    def mousePressEvent(self, event):
		self.clearSelection()
		QtGuiWidgets.QTreeView.mousePressEvent(self, event)


class Navigator(QtGuiWidgets.QDialog):

	def __init__(self, activeWindow, software):
		super(Navigator, self).__init__(activeWindow)
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
		self.jobs_dir_label = QtGuiWidgets.QLabel(self.jobs_dir)
		self.jobs_dir_label.setStyleSheet('text-decoration: underline')
		self.jobs_dir_label.mousePressEvent = self.jobs_dir_label_click

		self.job_combo = QtGuiWidgets.QComboBox()
		self.job_combo.activated[str].connect(self.on_job_change)
		self.profile_combo = QtGuiWidgets.QComboBox()
		self.profile_combo.activated[str].connect(self.on_profile_change)

		form_layout = QtGuiWidgets.QFormLayout()
		form_layout.addRow("Jobs Dir: ", self.jobs_dir_label)
		form_layout.addRow("Job: ", self.job_combo)
		form_layout.addRow("Profile: ", self.profile_combo)
		form_widget = QtGuiWidgets.QWidget()
		form_widget.setLayout(form_layout)
		form_widget.setFixedWidth(400)

		self.token_grid = QtGuiWidgets.QGridLayout()

		self.file_label = QtGuiWidgets.QLabel("File")
		self.file_tree_widget = DeselectableTreeWidget()
		self.file_tree_widget.setSortingEnabled(True)
		self.file_tree_widget.setHeaderLabels(["Name", "Date"])
		# self.file_tree_widget.setColumnWidth(0, 230)
		self.file_tree_widget.header().setStretchLastSection(False)
		try:
			self.file_tree_widget.header().setResizeMode(0, QtGuiWidgets.QHeaderView.Stretch)
			self.file_tree_widget.header().setResizeMode(1, QtGuiWidgets.QHeaderView.ResizeToContents)
		except:
			self.file_tree_widget.header().setSectionResizeMode(0, QtGuiWidgets.QHeaderView.Stretch)
			self.file_tree_widget.header().setSectionResizeMode(1, QtGuiWidgets.QHeaderView.ResizeToContents)
		self.file_tree_widget.currentItemChanged.connect(self.on_file_change)
		self.file_tree_widget.itemExpanded.connect(self.on_file_expand)
		self.file_line_edit = QtGuiWidgets.QLineEdit()
		self.file_line_edit.textEdited.connect(self.on_file_line_change)

		self.file_vbox = QtGuiWidgets.QVBoxLayout()
		self.file_vbox.addWidget(self.file_label)
		self.file_vbox.addWidget(self.file_tree_widget)
		self.file_vbox.addWidget(self.file_line_edit)

		self.file_widgets = [self.file_label, self.file_tree_widget, self.file_line_edit]

		self.path_label = QtGuiWidgets.QLabel()

		# Launch and cancel buttons ------------------------------------------------------
		self.execute_button = self.create_execute_button()


		cancelButton = QtGuiWidgets.QPushButton("Cancel")
		cancelButton.clicked.connect(self.close)

		self.hbox = QtGuiWidgets.QHBoxLayout()
		self.hbox.addStretch(1)
		self.hbox.addWidget(self.execute_button)
		self.hbox.addWidget(cancelButton)

		self.vbox = QtGuiWidgets.QVBoxLayout()
		self.vbox.addWidget(form_widget)
		self.vbox.addLayout(self.token_grid)
		self.vbox.addWidget(self.path_label)
		self.vbox.addLayout(self.hbox)
		self.setLayout(self.vbox)

		self.resize(1000,500)



	def create_execute_button(self):
		execute_button = QtGuiWidgets.QPushButton("Execute")
		execute_button.setEnabled(False)

		return execute_button


	def jobs_dir_label_click(self, click_event):
		"""Opens folder browser when jobs_dir_label is clicked"""
		selected_directory = QtGuiWidgets.QFileDialog.getExistingDirectory(dir=os.path.expanduser('~'))
		if selected_directory:
			self.jobs_dir = selected_directory
			self.jobs_dir_label.setText(self.jobs_dir)
			self.populate_jobs()

	def populate_jobs(self):
		"""Look in jobs folder for jobs that contain the config file at root"""
		jobsList = self.getDirList(self.jobs_dir)
		jobsList[:] = [job for job in jobsList if os.path.isfile(os.path.join(self.jobs_dir, job, CONFIG_FILE_NAME))]
		self.job_combo.clear()
		self.job_combo.addItems(jobsList)
		if len(jobsList) > 0:
			self.on_job_change(jobsList[0])
		else:
			self.on_job_change(None)

	def populate_profiles(self):
		"""Fill in the profiles combo box with options from the project config"""
		profileList = self.configReader.getLauncherProfiles(self.software).keys()
		self.profile_combo.clear()
		self.profile_combo.addItems(profileList)
		profile = ""
		# Check if any profiles exist
		if len(profileList) > 0:
			profile = profileList[0]
		self.on_profile_change(profile)

	def on_job_change(self, job):
		"""Called whenever the job combo box is changed"""
		if job is not None:
			self.current_job_path = os.path.join(self.jobs_dir, job)
			self.configReader = config_reader.ConfigReader(self.current_job_path)
			self.path_label.setText(self.current_job_path)

			# check software support for current job
			if self.configReader.checkSoftwareSupport(self.software):
				self.extensions = self.get_extensions()
				self.populate_profiles()
			else:
				self.clear_window()
				self.debugMsg("Project does not include support for this software")
		else:
			self.clear_window()
			self.debugMsg("No jobs in this directory")

	def get_extensions(self):
		return self.configReader.getExtensions(self.software)

	def clear_window(self):
		self.token_obj_dict.clear()
		self.profile_combo.clear()
		self.template = ""
		self.create_token_grid([])

	def on_profile_change(self, profile):
		"""Called whnever the profile combo box is changed"""
		self.template = self.configReader.getProfileTemplate(self.software, profile)
		token_list = self.configReader.getTokens(self.template)
		self.create_token_grid(token_list)

	def create_token_grid(self, token_list):
		"""Create the grid layout of tokens plus the file list that makes the body of the window"""
		self.token_obj_dict.clear()
		self.populate_file()

		for token in token_list:
			token_obj = Token(self, token)
			index = token_list.index(token)
			self.token_obj_dict[token] = token_obj

		deleteItemsOfLayout(self.token_grid)

		self.token_grid = QtGuiWidgets.QGridLayout()
		self.vbox.insertLayout(2, self.token_grid)
		
		for index, token in enumerate(token_list):
			token_obj = Token(self, token)
			self.token_obj_dict[token] = token_obj
			self.token_grid.addWidget(token_obj.label, 0, index)
			self.token_grid.addWidget(token_obj.list_widget, 1, index)
			self.token_grid.addWidget(token_obj.add_button, 2, index)
			self.token_grid.setColumnStretch(index, 1)

		self.token_grid.addWidget(self.file_label, 0, len(token_list))
		self.token_grid.addWidget(self.file_tree_widget, 1, len(token_list))
		self.token_grid.addWidget(self.file_line_edit, 2, len(token_list))
		# print("Column count:" + str(self.token_grid.columnCount()))
		self.token_grid.setColumnStretch(len(token_list), 2)

		if len(self.token_obj_dict) > 0:
			self.populate_token(self.token_obj_dict.keys()[0])

	def on_token_change(self, token, text):
		"""Called whenever a token's list widget is changed."""

		if text:
			currentPath = self.configReader.getPath(self.template, self.get_token_dict(), token)
			self.path_label.setText(os.path.join(currentPath, self.token_obj_dict[token].get_current()))

		self.execute_button.setEnabled(False)
		index = self.token_obj_dict.keys().index(token)

		if (len(self.token_obj_dict) > index+1):
			next_token = self.token_obj_dict.keys()[index+1]
			self.populate_token(next_token)


		# for i, token in enumerate(self.token_obj_dict, start=index+2):
		# 	# print(str(self.token_obj_dict[token]))
			# self.token_obj_dict[token].clear()
			# for token, thing in enumerate(self.token_obj_dict, start=index+2):
			# 	print("token: " + token)
			# 	print("thing: " + thing)
				# token.clear()


		# else:
			# self.populate_file()

		self.populate_file()

	def on_token_button(self, token):
		"""Called when a token object's 'new' button is clicked."""
		new_token, ok = QtGuiWidgets.QInputDialog.getText(self, "Create Token", ("Create New " + token.capitalize()), QtGuiWidgets.QLineEdit.Normal, ("new_" + token))
		if ok and new_token:
			project_creator.createToken(self.configReader, self.template, self.get_token_dict(), token, new_token)
			self.populate_token(token)

	def debugMsg(self, msg):
		"""Override this to customize how each software prints debug reports."""
		print(msg)


	def getDirList(self, directory, reverse=False):
		"""Returns a sorted list of directories in a given directory with an optional flag to reverse the order."""
		try:
			dirs = [name for name in os.listdir(directory)
					if os.path.isdir(os.path.join(directory, name))]
		except:
			return []
		return sorted(dirs, reverse=reverse)


	def getFileList(self, directory, extensions=[], reverse=False):
		"""Returns a sorted list of files with a given extension in a given directory with an optional flag to reverse the order."""
		try:
			if extensions:
				files = [name for name in os.listdir(directory)
						if (not os.path.isdir(os.path.join(directory, name))) & name.lower().endswith(tuple(extensions))]
			else:
				files = [name for name in os.listdir(directory)
						if (not os.path.isdir(os.path.join(directory, name)))]

		except:
			return []
		return sorted(files, reverse=reverse)

	def populate_token(self, token):
		"""Populates a token's list widget."""
		previous_token_index = self.token_obj_dict.keys().index(token)-1
		previous_token_obj = self.token_obj_dict.values()[previous_token_index]
		token_obj = self.token_obj_dict[token]

		# Populate the next token if the previous one has a selection or it's the first one
		if previous_token_obj.get_current() or previous_token_index <= 0:
			token_dict = self.get_token_dict()
			populate_path = self.configReader.getPath(self.template, self.get_token_dict(), token)

			folderList = self.getDirList(populate_path)
			excludeList = self.configReader.getExcludes(token)

			# Remove any occurances of excludeList from folderList
			folderList = [x for x in folderList if x not in excludeList]

			# Remove template folder from list
			tokenFolder = ".[" + token + "]"
			if tokenFolder in folderList:
				folderList.remove(tokenFolder)

			token_obj.set_list(folderList)
		else:
			token_obj.clear()


	def populate_file(self):
		"""Populates the file list widget based on the previous tokens."""

		self.file_tree_widget.clear()
		# print("Let's build this!")
		try:
			token_dict = self.get_token_dict()
			populate_path = self.configReader.getPath(self.template, token_dict)
			self.build_file_tree(populate_path, self.file_tree_widget)
		except:
			pass

		# self.file_list_widget.clear()
		# try:
		# 	token_dict = self.get_token_dict()
		# 	populatePath = self.configReader.getPath(self.template, token_dict)
		# 	file_list = self.getFileList(populatePath, self.extensions)
		# except:
		# 	file_list = []
		# # self.debugMsg("Trying to pupulate file box at this location: " + str(populatePath))
		# if len(file_list) > 0:
		# 	for index, file in enumerate(file_list):
		# 		current_item = QtGuiWidgets.QListWidgetItem(file, self.file_list_widget)
		# 		# Set to latest version
		# 		if (index+1 >= len(file_list)):
		# 			self.file_list_widget.setCurrentItem(current_item)
		# 			self.on_file_change(file)
		# 		else:
		# 			self.on_file_change("")

	def on_file_expand(self, item):
		for i in reversed(range(item.childCount())):
			item.removeChild(item.child(i))
		path = item.text(2)
		self.build_file_tree(path, item)


	def build_file_tree(self, path, tree):
		list_dir = os.listdir(path)
		for element in list_dir:
			path_info = os.path.join(path, element)
			date = time.strftime('%m/%d/%y %H:%M',  time.gmtime(os.path.getmtime(path_info)))
			parent_itm = QtGuiWidgets.QTreeWidgetItem(tree, [os.path.basename(element),date])
			parent_itm.setData(2, QtCore.Qt.EditRole, path_info)
			if os.path.isdir(path_info):
				parent_itm.setChildIndicatorPolicy(QtGuiWidgets.QTreeWidgetItem.ShowIndicator)
				# self.build_file_tree(path_info, parent_itm)
			else:
				fileInfo = QtCore.QFileInfo(path_info)
				iconProvider = QtGuiWidgets.QFileIconProvider()
				icon = iconProvider.icon(fileInfo)
				parent_itm.setIcon(0, icon)


	def on_file_change(self, item):
		"""Called when the file tree widget is changed."""

		self.file_line_edit.clear()
		if item:
			item.setSelected(True)
			path = item.text(2)
			file_name = os.path.basename(path)
			token_path = self.configReader.getPath(self.template, self.get_token_dict())
			rel_path = os.path.relpath(path, token_path)
			# rel_path = path.replace(token_path, '')
			# print("rel path: " + rel_path)
			if os.path.isdir(path):
				rel_path = os.path.join(rel_path, '')
			self.file_line_edit.setText(rel_path)
			self.on_file_line_change(rel_path)
			# if not os.path.isdir(path):
			# 	self.file_line_edit.setText(rel_path)
			# 	self.on_file_line_change(rel_path)
			# else:
			# 	self.file_line_edit.setText('')
			# 	self.on_file_line_change(file_name)

	def on_file_line_change(self, file):
		"""Called when the file line is changed."""

		if file:
			currentPath = self.configReader.getPath(self.template, self.get_token_dict())

			# extended_path=''

			# try:
			# 	extended_path = self.file_tree_widget.currentItem().text(2)
			# selected = self.file_tree_widget.currentItem().isSelected()
			# print("extended path: " + extended_path + str(selected))
			self.finalPath = os.path.join(currentPath, self.file_line_edit.text())
			self.path_label.setText(self.finalPath)
			if not os.path.isdir(self.finalPath):
				self.execute_button.setEnabled(True)
			else:
				self.execute_button.setEnabled(False)


	def get_token_dict(self):
		"""Get a dictionary of tokens from the dictionary of token objects."""
		token_dict = dict()
		for token_obj in self.token_obj_dict:
			token_value = self.token_obj_dict[token_obj].get_current()
			if token_value is not None:
				token_dict[token_obj] = token_value
		return token_dict
	
	def set_list_widget(self, list_widget, item_name):
		for i in range(list_widget.count()):
			item = list_widget.item(i)
			if item.text() == item_name:
				list_widget.setCurrentItem(item)
				return True
		return False

	def setComboBox(self, comboBox, value):
		index = comboBox.findText(value)
		if index >= 0:
			comboBox.setCurrentIndex(index)

	def read_local_config(self):
		"""Read the local config and return it."""
		localConfig = None
		try:
			with open(LOCAL_CONFIG_PATH, 'r') as stream:
				localConfig = yaml.safe_load(stream) or {}
		except IOError:
			open(LOCAL_CONFIG_PATH, 'w')
			localConfig = {}
		return localConfig

	def load_recents(self, read_local_config=False):
		"""Tries to load the project from the environment variables and falls back on local config unless read_local_config is explicitly set"""
		# print("Nevermind")
		localConfig = self.read_local_config()
		softwareRecents = dict()
		if read_local_config and localConfig and self.software in localConfig:
			softwareRecents = localConfig[self.software]

		else:
			try:
				softwareRecents["jobs_dir"] = os.environ["jobs_dir"]
				softwareRecents["job"] = os.environ["job"]
				softwareRecents["profile"] = os.environ["profile"]
				softwareRecents["tokens"] = ast.literal_eval(os.environ["tokens"])
			except:
				debugmsg("No current environment")

		if softwareRecents:
			self.jobs_dir = softwareRecents["jobs_dir"]
			self.jobs_dir_label.setText(self.jobs_dir)
			self.populate_jobs()
			self.setComboBox(self.job_combo, softwareRecents["job"])
			self.on_job_change(softwareRecents["job"])

			self.setComboBox(self.profile_combo, softwareRecents["profile"])
			self.on_profile_change(softwareRecents["profile"])
			recentsTokens = softwareRecents["tokens"]
			for token, token_obj in self.token_obj_dict.iteritems():
				#self.setComboBox(self.tokenComboDict[token], recentsTokens[token])
				self.set_list_widget(token_obj.list_widget, recentsTokens[token])
				self.on_token_change(token, recentsTokens[token])
				# self.setComboBox(self.tokenComboDict[token], recentsTokens[token])
				# self.onTokenChange(recentsTokens[token], self.tokenComboDict[token])

	def save_recents(self, write_local_config=False):
		"""Saves the project to the software's local config."""
		recentOption = dict()
		recentOption["jobs_dir"] = str(self.jobs_dir)
		recentOption["job"] = str(self.job_combo.currentText())
		recentOption["profile"] = str(self.profile_combo.currentText())
		tokenDict = dict()
		for token, token_obj in self.token_obj_dict.iteritems():
			tokenDict[str(token)] = str(token_obj.get_current())

		recentOption["tokens"] = tokenDict

		for recent, value in recentOption.iteritems():
			os.environ[recent] = str(value)

		newConfig = self.read_local_config()
		newConfig[self.software] = recentOption
		with open(LOCAL_CONFIG_PATH, 'w') as outfile:
		    yaml.dump(newConfig, outfile, default_flow_style=False)

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

	def __str__(self):
		return "Token Obj:\nParent: " + str(self.parent) + " token: " + str(self.token)


	def on_token_change(self, text):
		self.current_text = text
		self.parent.on_token_change(self.token, text)

	def on_token_button(self):
		self.parent.on_token_button(self.token)

	def set_list(self, options_list):
		self.list_widget.clear()
		for element in options_list:
			QtGuiWidgets.QListWidgetItem(element, self.list_widget)

	def clear(self):
		self.list_widget.clear()

	def get_current(self):
		return self.current_text

# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Navigator(app.activeWindow(), 'maya')
	app.exec_()