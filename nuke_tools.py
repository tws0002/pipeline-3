# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os

import nuke
import nukescripts
import project_launcher
import importer
import saver
import software_tools

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

class NukeTools(software_tools.SoftwareTools):

    def __init__(self):
        self.software = SOFTWARE

    def debug_msg(self, msg):
        nuke.tprint(msg)

    def _save_as(self, path):
        try:
            nuke.scriptSaveAs(filename=path, overwrite=True)
            return True
        except:
            return False

    def _save(self):
        try:
            nuke.scriptSaveAs(overwrite=True)
            return True
        except:
            return False

    def get_project_path(self):
        return nuke.root().name()

    def is_project_modified(self):
        return nuke.root().modified()


class NukeProjectLauncher(project_launcher.ProjectLauncher):

    def __init__(self):
        self.nuke_tools = NukeTools()
        super(NukeProjectLauncher, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.nuke_tools)

    def launchProject(self, filePath):

        nuke.scriptOpen(filePath)
        super(NukeProjectLauncher, self).save_recents(write_local_config=True)
        return True

class NukeSaver(saver.Saver):

    def __init__(self):
        self.nuke_tools = NukeTools()
        super(NukeSaver, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.nuke_tools)

    def save_file(self, filePath):
        nuke.scriptSaveAs(filename=filePath, overwrite=True)
        super(NukeSaver, self).save_recents(write_local_config=True)
        return True


class NukeImporter(importer.Importer):

    def __init__(self):
        self.nuke_tools = NukeTools()
        super(NukeImporter, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.nuke_tools)

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

def add_menu():
    nuke.tprint("Adding pipeline tools...")
    menubar = nuke.menu("Nuke")
    assetmenu = menubar.addMenu('Carbon Pipeline')
    assetmenu.addCommand(
        'Project Launcher', 'reload(pipeline.nuke_tools).NukeProjectLauncher()', 'ctrl+shift+o')
    assetmenu.addCommand('Import', 'reload(pipeline.nuke_tools).NukeImporter()')
    assetmenu.addCommand('Save', 'reload(pipeline.nuke_tools).NukeSaver()')
    assetmenu.addCommand(
        'Version Up', 'pipeline.nuke_tools.NukeTools().version_up()')
    assetmenu.addCommand(
        'Publish', 'pipeline.nuke_tools.NukeTools().publish()')
