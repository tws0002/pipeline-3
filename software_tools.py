# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import re
import importlib
import imp
import publisher
import environment

from pipeline_config import TEMP_FILE_SUFFIX

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

    def debug_msg(self, msg):
        """ Defines how each software prints to the console. """
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

    def remove_temp_suffix(self, name):
        """ If the temporary file suffix exists, strip it and add the extension 
        back to the end. """
        raw_name, ext = os.path.splitext(name)
        if raw_name.endswith(TEMP_FILE_SUFFIX):
            name = raw_name[:-len(TEMP_FILE_SUFFIX)] + ext
        return name

    def create_pub_name(self, name):
        """ Takes the project name and replaces v### with 'PUBLISH' """
        # If it's a temporary file, strip the suffix before renaming
        name = self.remove_temp_suffix(name)
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
            raise ValueError("More or less than one instance of v### in file name.")

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
        """ Returns the version of the given path as an integer. """
        try:
            return int(self.get_version_str(path))
        except:
            raise

    def find_env_file(self, path, env_file_name):
        """ Looks in each directory level of "path" for the env_file_name.
        If it finds it, it returns the path to the file """
        current_dir = path
        while current_dir:
            env_file_path = os.path.join(current_dir, env_file_name)
            if os.path.isfile(env_file_path):
                return env_file_path
            current_dir, check_folder = os.path.split(current_dir)
            # If there are no more directories, break
            if not check_folder:
                break
        return ''

    def version_up(self, only_filename=False):
        """ Given a path this will version up the file and return the incremented path if the 
        file doesn't already exist, or if the user chooses to overwrite the existing file. 
        """
        path = self.get_project_path()
        directory = os.path.dirname(path)
        if only_filename:
            path = os.path.basename(path)

        # Attempt to version up the file
        try:
            path = self.increment_version(path)
        except:
            raise

        # If we previously stripped off the filename, add the path back to the beginning
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
            # Create dialog
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

    def publish(self, project_path=None):
        """ Publishes the current file base on the file name and location. """
        if not project_path:
            project_path = self.get_project_path()
        # Check that the environment is valid
        if environment.is_valid(software=self.get_software()):
            # Check if the file has been modified
            if self.is_project_modified():
                if self.file_not_saved_dlg():
                    self._save()
                else:
                    return False
            
            # Define directories
            proj_dir = os.path.dirname(project_path)
            raw_proj_name, proj_ext = os.path.splitext(os.path.basename(project_path))
            self.debug_msg("project basename = " + os.path.basename(project_path))
            archive_dir = os.path.join(proj_dir, 'archive')
            publish_dir = os.path.join(proj_dir, 'publish')

            # Append 'PUBLISH' to file before archiving it
            archive_name, ext = os.path.splitext(os.path.basename(project_path))
            archive_name = self.remove_temp_suffix(archive_name)
            archive_name = archive_name + '_PUBLISH' + ext

            # Create publish name
            pub_name = self.create_pub_name(os.path.basename(project_path))

            publisher_dlg = publisher.Publisher(publish_dir, pub_name)
            if publisher_dlg.exec_():
                pub_name = publisher_dlg.get_name()
                # If a valid name comes back from the dialog, copy it to the publish directory
                if pub_name:
                    # Create archive directory if it doesn't exist
                    try:
                        os.makedirs(archive_dir)
                    except OSError:
                        if not os.path.isdir(archive_dir):
                            raise
                    copyfile(project_path, os.path.join(archive_dir, archive_name))

                    # Create publish folder if it doesn't exist
                    try:
                        os.makedirs(publish_dir)
                    except OSError:
                        if not os.path.isdir(publish_dir):
                            raise
                    copyfile(project_path, os.path.join(publish_dir, pub_name))

                    if publisher_dlg.get_del_state():
                        if raw_proj_name.endswith(TEMP_FILE_SUFFIX):
                            if os.path.isfile(project_path):
                                self.debug_msg("Deleting this file: " + project_path)
                                os.remove(project_path)
                    # If a temporary file is currently open, open the versioned file instead
                    versioned_file = self.remove_temp_suffix(project_path)
                    if versioned_file != project_path and os.path.isfile(versioned_file):
                        self.debug_msg("Opening versioned file")
                        self.open_project(versioned_file)
        else:
            self.debug_msg("Environment is not valid!")

    def get_software(self):
        """ Returns the name of the current software """
        return self.software

    def get_project_path(self):
        """ Returns the full path to the project file. """
        raise NotImplementedError

    def is_project_modified(self):
        """ Returns true if the current project has been modified without and not saved """
        raise NotImplementedError

    def _save(self):
        """ Defines how the current software saves the current file. """
        raise NotImplementedError

    def _save_as(self, path):
        """ Defines how the current software saves to a specified path. """
        raise NotImplementedError

    def set_environment(self, config_reader, template, token_dict):
        """ Defines actions a software can take to setup the current environment. """
        pass

    def open_project(self, path):
        """ Opens the project at the specified path. """
        raise NotImplementedError

# DEBUGGING------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    path = 'V:/Jobs/182276_Essilor_Out_of_Focus/Design/Production/TVC60/Assets/Environments/Gym/model/esof_gym_model_V05.ma'
    app = QtGuiWidgets.QApplication(sys.argv)
    # print(SoftwareTools().version_up(path))
    print("Here it is! " + SoftwareTools().find_env_file(
        'V:\\Jobs\\182350_Lululemon\\Design\\Production\\tvc_20_1920\\Previz\\Projects\\CG\\layout', 'workspaces.mel'))
    # print(os.path.isfile("C:\\Users\\athompson\\Desktop\\test.md"))
    # print("C:\\Users\\athompson\\Desktop\\test.md")
    # print(get_version_str(path, False))
    # print(get_version_int(path))
