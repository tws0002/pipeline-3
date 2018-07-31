# -*- coding: utf-8 -*-
# Adam Thompson 2018

import project_launcher
import importer
import saver
import software_tools

import hou

import os

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

SOFTWARE = "houdini"

class HoudiniTools(software_tools.SoftwareTools):

	def __init__(self):
		self.software = SOFTWARE

	def debugMsg(self, msg):
		print(msg)

	def _save_as(self, path):
		try:
			hou.hipFile.save(path)
			return True
		except:
			return False

	def _save(self):
		try:
			hou.hipFile.save()
			return True
		except:
			return False

	def get_project_path(self):
		return hou.hipFile.path()

	def is_project_modified(self):
		return hou.hipFile.hasUnsavedChanges()


class HoudiniProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		self.houdini_tools = HoudiniTools()
		super(HoudiniProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.houdini_tools)

	def launchProject(self, filePath):
		tokenDict = self.get_token_dict()
		self.houdini_tools.debugMsg("Setting environment variables: ")
		for token in tokenDict:
			os.environ[token] = tokenDict[token]
			self.houdini_tools.debugMsg(token + " = " + tokenDict[token])

		self.houdini_tools.debugMsg("Here we go!")
		hou.allowEnvironmentToOverwriteVariable("JOB", True)
		hou.putenv("JOB", "COOL DUDE")
		forwardSlashPath = filePath.replace('\\', '/')
		hou.hipFile.load(forwardSlashPath)
		return True


class HoudiniImporter(importer.Importer):

	def __init__(self):
		self.houdini_tools = HoudiniTools()
		super(HoudiniImporter, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.houdini_tools)
		self.houdini_tools.debugMsg("Starting houdini importer...")

	def import_file(self, file_path):

		try:
			basename, ext = os.path.splitext(os.path.basename(file_path))
			obj = hou.node("/obj")
			self.houdini_tools.debugMsg(basename)
			obj_node = obj.createNode("geo", basename, run_init_scripts=False)
			file_node = obj_node.createNode("file", basename)
			file_node.parm("file").set(file_path)
			return True
		except:
			raise
			return False


class HoudiniSaver(saver.Saver):
	def __init__(self):
		self.houdini_tools = HoudiniTools()
		super(HoudiniSaver, self).__init__(QtGuiWidgets.QApplication.activeWindow(), self.houdini_tools)
		self.houdini_tools.debugMsg("Starting houdini saver...")

	def save_file(self, file_path):

		try:
			hou.hipFile.save(file_path)
			return True
		except:
			return False


def setup():
	current_dir = os.path.dirname(os.path.abspath(__file__))
	houdini_path = os.path.join(current_dir, 'houdini')
	current_path = hou.getenv("HOUDINI_PATH")
	hou.putenv("HOUDINI_PATH", "&;" + houdini_path + ";" + current_path)
