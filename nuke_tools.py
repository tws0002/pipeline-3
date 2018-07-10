# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os

import nuke
import nukescripts
import project_launcher
import importer
import saver

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

SOFTWARE = "nuke"

class NukeProjectLauncher(project_launcher.ProjectLauncher):

	def __init__(self):
		super(NukeProjectLauncher, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		nuke.tprint(self.configReader.sayHello())

	def launchProject(self, filePath):

		nuke.scriptOpen(filePath)
		super(NukeProjectLauncher, self).save_recents(write_local_config=True)
		return True

	def debugMsg(self, msg):
		nuke.tprint(msg)

class NukeSaver(saver.Saver):

	def __init__(self):
		super(NukeSaver, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		nuke.tprint(self.configReader.sayHello())

	def save_file(self, filePath):
		nuke.scriptSaveAs(filename=filePath, overwrite=True)
		super(NukeSaver, self).save_recents(write_local_config=True)
		return True

	def debugMsg(self, msg):
		nuke.tprint(msg)


class NukeImporter(importer.Importer):

	def __init__(self):
		super(NukeImporter, self).__init__(QtGuiWidgets.QApplication.activeWindow(), SOFTWARE)
		nuke.tprint(self.configReader.sayHello())

	def import_file(self, filePath):
		if filePath[-4:] == '.abc' and os.path.exists(filePath):
			readGeo = nuke.createNode('ReadGeo2', 'file {%s}' % (filePath))
			sceneView = readGeo['scene_view']
			allItems = sceneView.getAllItems()

			if allItems:
				sceneView.setImportedItems(allItems)
				sceneView.setSelectedItems(allItems)
			else:
				nuke.delete(readGeo)
				nuke.createNode('Camera2', 'file {%s} read_from_file True' % (filePath))
			return True
		elif filePath[-3] == '.nk' and os.path.exists(filePath):
			nuke.scriptReadFile(filePath)
			return True
		return False

	def debugMsg(self, msg):
		nuke.tprint(msg)