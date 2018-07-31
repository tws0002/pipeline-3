# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os

import importer
import project_launcher
import saver
import publisher
import environment
import maya_hooks
import software_tools


import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

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


def addMenu():
	print("Loading Pipeline...")
	# Name of the global variable for the Maya window
	MainMayaWindow = pm.language.melGlobals['gMainWindow']
	# Build a menu and parent underthe Maya Window
	customMenu = pm.menu('Carbon Pipeline', parent=MainMayaWindow)
	# Build a menu item and parent under the 'customMenu'
	pm.menuItem(label="Launch Project",command="pipeline.maya_tools.MayaProjectLauncher()", parent=customMenu)
	pm.menuItem(label="Import",command="pipeline.maya_tools.MayaImporter()", parent=customMenu)
	pm.menuItem(label="Save", command="pipeline.maya_tools.MayaSaver()", parent=customMenu)
	pm.menuItem(divider=True, parent=customMenu)
	pm.menuItem(label="Version Up", command="pipeline.maya_tools.MayaTools().version_up()", parent=customMenu)
	pm.menuItem(label="Publish", command="pipeline.maya_tools.MayaTools().publish()", parent=customMenu)



class MayaTools(software_tools.SoftwareTools):

	def __init__(self):
		self.software = SOFTWARE

	def debugMsg(self, msg):
		print(msg)

	def set_environment(self, config_reader, template, token_dict):
		""" Finds if the root is a shot or asset and looks for the WORKSPACE_FILE there. """
		# Find current root token
		rootToken = ""
		for token in token_dict:
			if token in ROOT_TOKENS:
				rootToken = token

		self.debugMsg("The last token is: " + rootToken)
		path = os.path.join(config_reader.getPath(
			template, token_dict, rootToken), token_dict[rootToken])
		filepath = os.path.join(path, WORKSPACE_FILE)
		self.debugMsg("Trying to load this workspace: " + path)
		if os.path.isfile(filepath):
			self.debugMsg("Loading this workspace: " + path)
			cmds.workspace(path, openWorkspace=True)
		else:
			self.debugMsg("That's not a valid workspace!")


	def _save_as(self, path):
		try:
			cmds.file(rename=path)
			cmds.file(save=True)
			return True
		except:
			return False

	def _save(self):
		try:
			cmds.file(save=True)
			return True
		except:
			raise
			return False

	def get_project_path(self):
		return pm.system.sceneName()

	def is_project_modified(self):
		return cmds.file(q=True, modified=True)

class MayaImporter(importer.Importer, MayaTools):
	def __init__(self):
		self.maya_tools = MayaTools()
		super(MayaImporter, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.maya_tools)
		self.maya_tools.debugMsg("Starting maya importer...")

	def import_file(self, file_path):
		import_dialog = ImportDialog(QtGuiWidgets.QApplication.activeWindow(), file_path).exec_()
		# Returns true or false based on the import dialog
		return import_dialog


class ImportDialog(QtGuiWidgets.QDialog):
	
	def __init__(self, activeWindow, file_path):
		self.maya_tools = MayaTools()
		super(ImportDialog, self).__init__(activeWindow)
		self.file_path = file_path
		self.file_name, self.file_ext = os.path.splitext(os.path.basename(file_path))

		self.initUI()
		self.setModal(True)
		self.show()

	def initUI(self):
		self.setWindowTitle("Import Dialog") 

		self.ok_button = QtGuiWidgets.QPushButton("OK")
		self.ok_button.clicked.connect(self.on_ok)
		self.cancel_button = QtGuiWidgets.QPushButton("Cancel")
		self.cancel_button.clicked.connect(self.reject)

		self.ref_checkbox = QtGuiWidgets.QCheckBox()
		self.ref_checkbox.setChecked(True)
		self.use_namespace_checkbox = QtGuiWidgets.QCheckBox()
		self.use_namespace_checkbox.setChecked(True)
		self.use_namespace_checkbox.stateChanged.connect(self.on_namespace_checkbox_change)
		self.namespace_lineedit = QtGuiWidgets.QLineEdit(self.file_name)


		reference_form = QtGuiWidgets.QFormLayout()
		reference_form.addRow("Reference", self.ref_checkbox)

		reference_group = QtGuiWidgets.QGroupBox("Reference")
		reference_group.setLayout(reference_form)

		namespace_form = QtGuiWidgets.QFormLayout()
		namespace_form.addRow("Use Namespace", self.use_namespace_checkbox)
		namespace_form.addRow("Namespace", self.namespace_lineedit)

		namespace_group = QtGuiWidgets.QGroupBox("Namespace")
		namespace_group.setLayout(namespace_form)

		hbox = QtGuiWidgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.ok_button)
		hbox.addWidget(self.cancel_button)

		vbox = QtGuiWidgets.QVBoxLayout()
		vbox.addWidget(reference_group)
		vbox.addWidget(namespace_group)
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)


	def on_ok(self):
		flags = self.get_flags()
		print("flags: " + str(flags))
		cmds.file(self.file_path, **flags)
		self.accept()

	def on_namespace_checkbox_change(self, state):
		self.namespace_lineedit.setEnabled(state)

	def get_flags(self):
		""" Returns a dictionary of flags based on what is currently selected in the dialog. """
		flags = dict()

		if self.ref_checkbox.isChecked():
			flags["reference"] = True
		else:
			flags["i"] = True

		
		if self.use_namespace_checkbox.isChecked():
			flags["namespace"] = self.namespace_lineedit.text()
		
		return flags


class MayaProjectLauncher(project_launcher.ProjectLauncher):
	def __init__(self):
		self.maya_tools = MayaTools()
		super(MayaProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.maya_tools)
		self.maya_tools.debugMsg("Starting maya project launcher...")

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()

		try: 
			cmds.file(filePath, o=True)
			self.set_environment(self.configReader, self.template, self.get_token_dict())
			return True
		except RuntimeError:
			self.maya_tools.debugMsg("Hey, this is cool")
			ret = self.fileNotSavedDlg()
			if ret == QtGuiWidgets.QMessageBox.Save:
				cmds.file(save=True)
				cmds.file(filePath, o=True)
				self.set_environment(self.configReader, self.template, self.get_token_dict())
				return True
			elif ret == QtGuiWidgets.QMessageBox.Discard:
			    cmds.file(new=True, force=True) 
			    cmds.file(filePath, open=True)
			    self.maya_tools.set_environment(self.configReader, self.template, self.get_token_dict())
			    return True
			elif ret == QtGuiWidgets.QMessageBox.Cancel:
				self.maya_tools.debugMsg("Nevermind...")
				return False

	def fileNotSavedDlg(self):
		msgBox = QtGuiWidgets.QMessageBox()
		msgBox.setText("The document has been modified.")
		msgBox.setInformativeText("Do you want to save your changes?")
		msgBox.setStandardButtons(QtGuiWidgets.QMessageBox.Save | QtGuiWidgets.QMessageBox.Discard | QtGuiWidgets.QMessageBox.Cancel)
		msgBox.setDefaultButton(QtGuiWidgets.QMessageBox.Save)
		ret = msgBox.exec_()
		return ret


class MayaSaver(saver.Saver):
	
	def __init__(self):
		self.maya_tools = MayaTools()
		super(MayaSaver, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.maya_tools)
		self.maya_tools.debugMsg("Starting maya saver...")

	def save_file(self, file_path):

		try:
			cmds.file( rename=file_path)
			cmds.file(save=True)
			self.maya_tools.set_environment(self.configReader, self.template, self.get_token_dict())
			return True
		except:
			raise
			return False
