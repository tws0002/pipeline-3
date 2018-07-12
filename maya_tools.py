# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os

import importer
import project_launcher
import saver

import maya.cmds as cmds

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



class MayaImporter(importer.Importer):

	def __init__(self):
		super(MayaImporter, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		self.debugMsg("Starting maya importer...")

	def import_file(self, file_path):
		import_dialog = ImportDialog(QtGuiWidgets.QApplication.activeWindow(), file_path).exec_()
		# Returns true or false based on the import dialog
		return import_dialog


	def debugMsg(self, msg):
		print(msg)

class ImportDialog(QtGuiWidgets.QDialog):

	def __init__(self, activeWindow, file_path):
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
		flags = dict()

		if self.ref_checkbox.isChecked():
			flags["reference"] = True
		else:
			flags["i"] = True

		
		if self.use_namespace_checkbox.isChecked():
			flags["namespace"] = self.namespace_lineedit.text()
		
		return flags


	def get_value(self):
		return "Yup, that definitely worked."


class MayaProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(MayaProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		self.debugMsg("Starting maya project launcher...")

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()

		try: 
			cmds.file(filePath, o=True)
			set_environment(self.configReader, self.template, self.get_token_dict())
			return True
		except RuntimeError:
			self.debugMsg("Hey, this is cool")
			ret = self.fileNotSavedDlg()
			if ret == QtGuiWidgets.QMessageBox.Save:
				cmds.file(save=True)
				cmds.file(filePath, o=True)
				set_environment(self.configReader, self.template, self.get_token_dict())
				return True
			elif ret == QtGuiWidgets.QMessageBox.Discard:
			    cmds.file(new=True, force=True) 
			    cmds.file(filePath, open=True)
			    set_environment(self.configReader, self.template, self.get_token_dict())
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


class MayaSaver(saver.Saver):
	def __init__(self):
		super(MayaSaver, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		self.debugMsg("Starting maya saver...")

	def save_file(self, file_path):

		try:
			cmds.file( rename=file_path)
			cmds.file(save=True)
			set_environment(self.configReader, self.template, self.get_token_dict())
			return True
		except:
			return False


	def debugMsg(self, msg):
		print(msg)



def set_environment(config_reader, template, token_dict,):
	# Find current root token
	rootToken = ""
	for token in token_dict:
		if token in ROOT_TOKENS:
			rootToken = token

	debugMsg("The last token is: " + rootToken)
	path = os.path.join(config_reader.getPath(template, token_dict, rootToken), token_dict[rootToken])
	filepath = os.path.join(path, WORKSPACE_FILE)
	debugMsg("Trying to load this workspace: " + path)
	if os.path.isfile(filepath):
		debugMsg("Loading this workspace: " + path)
		cmds.workspace(path, openWorkspace=True)
	else:
		debugMsg("That's not a valid workspace!")

def debugMsg(msg):
	print(msg)