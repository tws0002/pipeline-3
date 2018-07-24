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


class Publisher(QtGuiWidgets.QDialog):
	def __init__(self, activeWindow, software):
		super(Publisher, self).__init__(activeWindow)
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

# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Publisher(app.activeWindow(), 'maya')
	app.exec_()