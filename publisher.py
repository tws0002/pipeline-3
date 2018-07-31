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
	def __init__(self, pub_path, pub_name):
		super(Publisher, self).__init__(QtGuiWidgets.QApplication.activeWindow())
		self.pub_name = pub_name
		self.pub_path = pub_path
		self.init_ui()
		self.on_name_change()
		self.show()

	def init_ui(self):
		self.ok_button = QtGuiWidgets.QPushButton("OK")
		self.ok_button.clicked.connect(self.accept)
		self.cancel_button = QtGuiWidgets.QPushButton("Cancel")
		self.cancel_button.clicked.connect(self.reject)
		self.file_name_box = QtGuiWidgets.QLineEdit()
		self.file_name_box.setText(self.pub_name)
		self.file_name_box.textEdited.connect(self.on_name_change)
		self.path_label = QtGuiWidgets.QLabel()

		hbox = QtGuiWidgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.ok_button)
		hbox.addWidget(self.cancel_button)

		vbox = QtGuiWidgets.QVBoxLayout()
		vbox.addWidget(self.file_name_box)
		vbox.addStretch(1)
		vbox.addWidget(self.path_label)
		vbox.addLayout(hbox)

		self.setLayout(vbox)
		# self.resize(500,500)

	def on_name_change(self):
		self.path_label.setText(os.path.join(self.pub_path, self.file_name_box.text()))

	def get_name(self):
		return self.file_name_box.text()
# Debugging -----------------------------------------------
if __name__== '__main__':
	app = QtGuiWidgets.QApplication(sys.argv)
	ex = Publisher('path/to/place', 'maya')
	if ex.exec_():
		name = ex.file_name_box.text()
		print(name)
	# app.exec_()
