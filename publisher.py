# -*- coding: utf-8 -*-
# Adam Thompson 2018
import os
import sys

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

import software_tools

class Publisher(QtGuiWidgets.QDialog):
	def __init__(self, current_software_tools):
		super(Publisher, self).__init__(QtGuiWidgets.QApplication.activeWindow())
		self.current_software_tools = current_software_tools
		self.init_ui()
		self.show()

	def init_ui(self):
		self.ok_button = QtGuiWidgets.QPushButton("OK")
		# self.ok_button.clicked.connect(self.on_ok)
		self.cancel_button = QtGuiWidgets.QPushButton("Cancel")
		# self.cancel_button.clicked.connect(self.reject)
		self.file_name_box = QtGuiWidgets.QLineEdit()

		hbox = QtGuiWidgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.ok_button)
		hbox.addWidget(self.cancel_button)

		vbox = QtGuiWidgets.QVBoxLayout()
		vbox.addWidget(self.file_name_box)
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)
		# self.resize(500,500)

	def publish():
		# First, check that the current evironment is valid
		if environment.is_valid(software='maya'):
			# Check if file has been modified
			file_modified = cmds.file(q=True, modified=True)
			if file_modified and self.file_not_saved_dlg():
				cmds.file(save=True)
			env_config_reader = environment.get_config_reader()
			profile = environment.get_profile()

			if maya_hooks.publish():
				pass
			else:
				print("Publish failed, reverting to previous save.")
		else:
			print("Environment is not valid!")


# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Publisher('maya')
	app.exec_()
