# -*- coding: utf-8 -*-
# Adam Thompson 2018
import os

import project_launcher
import importer
import saver

import software_tools

import MaxPlus

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

SOFTWARE = "max"
WORKSPACE_FILE = "maxWorkspace.mxp"


class MaxTools(software_tools.SoftwareTools):

    def __init__(self):
        self.software = SOFTWARE

    def debug_msg(self, msg):
        print(msg)

    def _save_as(self, path):
        try:
            MaxPlus.FileManager.Save(path)
            return True
        except:
            return False

    def _save(self):
        try:
            MaxPlus.FileManager.Save()
            return True
        except:
            return False

    def get_project_path(self):
        return MaxPlus.FileManager.GetFileNameAndPath()

    def is_project_modified(self):
        return MaxPlus.FileManager.IsSaveRequired()

    def set_environment(self, config_reader, template, token_dict):
        """ Find the workspace file and implements it. """

        # Find workspace file
        filepath = self.find_env_file(config_reader.get_path(
            template, token_dict), WORKSPACE_FILE)
        path = os.path.dirname(filepath)

        filepath = filepath.replace(os.path.sep, '/')
        self.debug_msg("Trying to load this workspace: " + path)
        if os.path.isfile(filepath):
            self.debug_msg("Loading this workspace: " + path)
            # Create maxscript to run to load project workspace
            maxscript = ('pathConfig.load "' + filepath + '"')
            print("Maxscript to run: " + maxscript)
            MaxPlus.Core.EvalMAXScript(maxscript)
        else:
            self.debug_msg("That's not a valid workspace!")



class MaxProjectLauncher(project_launcher.ProjectLauncher):

    def __init__(self):
        self.max_tools = MaxTools()
        super(MaxProjectLauncher, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.max_tools)

    def launchProject(self, filePath):
        tokenDict = self.get_token_dict()
        self.max_tools.debug_msg("Setting environment variables: ")
        for token in tokenDict:
            os.environ[token] = tokenDict[token]
            self.max_tools.debug_msg(token + " = " + tokenDict[token])
        # nuke.scriptOpen(filePath)

        fm = MaxPlus.FileManager
        fm.Open(filePath)
        self.max_tools.set_environment(
            self.configReader, self.template, self.get_token_dict())
        return True


class MaxImporter(importer.Importer):

    def __init__(self):
        self.max_tools = MaxTools()
        super(MaxImporter, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.max_tools)
        self.max_tools.debug_msg("Starting max importer...")

    def import_file(self, file_path):
        root, ext = os.path.splitext(file_path)
        ext = ext.lower()
        fm = MaxPlus.FileManager
        try:
            if ext == '.max':
                fm.Merge(file_path)
            else:
                fm.Import(file_path)
            return True
        except:
            return False

class MaxSaver(saver.Saver):
    def __init__(self):
        self.max_tools = MaxTools()
        super(MaxSaver, self).__init__(
            QtGuiWidgets.QApplication.activeWindow(), self.max_tools)
        self.max_tools.debug_msg("Starting max saver...")

    def save_file(self, file_path):
        fm = MaxPlus.FileManager
        try:
            fm.Save(file_path)
            self.max_tools.set_environment(
                self.configReader, self.template, self.get_token_dict())
            return True
        except:
            return False


def open_project_launcher():
    MaxProjectLauncher()

def open_importer():
    MaxImporter()

def open_saver():
    MaxSaver()

def version_up():
    MaxTools().version_up()

def publish():
    MaxTools().publish()

def addMenu():
    menu_name = u"Carbon Pipeline"

    MaxPlus.MenuManager.UnregisterMenu(menu_name)

    if not MaxPlus.MenuManager.MenuExists(menu_name):
        mb = MaxPlus.MenuBuilder(menu_name)
        mb.AddItem(MaxPlus.ActionFactory.Create(
            'Do something', 'Launch Project', open_project_launcher))
        mb.AddItem(MaxPlus.ActionFactory.Create(
            'Do something', 'Import', open_importer))
        mb.AddItem(MaxPlus.ActionFactory.Create('Do something', 'Save', open_saver))
        mb.AddSeparator()
        mb.AddItem(MaxPlus.ActionFactory.Create(
            'Do something', 'Version Up', version_up))
        mb.AddItem(MaxPlus.ActionFactory.Create(
            'Do something', 'Publish', publish))
        menu = mb.Create(MaxPlus.MenuManager.GetMainMenu())
        print 'menu created', menu.Title
    else:
        print 'The menu ', menu_name, ' already exists'
