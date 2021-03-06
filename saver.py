# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys

import navigator

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


class Saver(navigator.Navigator):

    def __init__(self, active_window, current_software_tools):
        super(Saver, self).__init__(active_window, current_software_tools)
        self.current_software_tools = current_software_tools
        self.load_recents()
        self.setWindowTitle(self.software.capitalize() + " Saver") 
        self.current_software_tools.debug_msg("Starting saver...")
    
    def create_execute_button(self):
        """ Defines the execute_botton as 'save'. """
        execute_button = QtGuiWidgets.QPushButton("Save")
        execute_button.setEnabled(False)
        execute_button.clicked.connect(self.on_save_click)
        return execute_button

    def on_save_click(self):
        """Called when the save button is clicked. Attempts to save file with child's 
        'save_file' function.
        """
        currentPath = self.configReader.get_path(self.template, self.get_token_dict())
        self.finalPath = os.path.join(currentPath, self.file_line_edit.text())

        # Check if file exists
        if os.path.isfile(self.finalPath):
            ok_button = QtGuiWidgets.QMessageBox.Ok
            cancel_button = QtGuiWidgets.QMessageBox.Cancel
            ret = QtGuiWidgets.QMessageBox.information(self, 
                "File Already Exists", "This file already exists." 
                " Are you sure you want to overwrite it?", ok_button, cancel_button)

            if ret == ok_button:
                if self.save_file(self.finalPath):
                    self.close()

        else:
            if self.save_file(self.finalPath):
                self.save_recents(write_local_config=True)
                self.close()

    def save_file(self, file_path):
        """Just a placeholder. Should be overridden by child."""
        self.current_software_tools.debug_msg("Saving!")
        return True

    def get_extensions(self):
        """ Override navigator's 'get_extensions' in order to return all extensions. """
        return []

# Debugging -----------------------------------------------
if __name__== '__main__':
    app = QtGuiWidgets.QApplication(sys.argv)
    ex = Saver(app.activeWindow(), 'maya')
    app.exec_()
