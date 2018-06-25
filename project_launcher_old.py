# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
from collections import OrderedDict
import yaml

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

import config_reader
import project_creator

DEFAULT_JOBS_DIR = "V:\\Jobs"
CONFIG_FILE_NAME = "config.yml"
LOCAL_CONFIG_PATH = os.path.expanduser('~/carbonLocalConfig.yml')

class CustomComboBox(QtGuiWidgets.QComboBox):
	"""This comboBox extends QComboBox, is editable, and suggests semi-fuzzy results from query
	https://stackoverflow.com/questions/4827207/how-do-i-filter-the-pyqt-qcombobox-items-based-on-the-text-input
	"""
	def __init__( self,  parent = None):
		super( CustomComboBox, self ).__init__( parent )

		self.setFocusPolicy( QtCore.Qt.StrongFocus )
		self.setEditable( True )
		self.completer = QtGuiWidgets.QCompleter( self )

		# always show all completions
		self.completer.setCompletionMode( QtGuiWidgets.QCompleter.UnfilteredPopupCompletion )

		# THIS IS AN IMPORTANT
		try:
			# < Nuke 11
			self.pFilterModel = QtGui.QSortFilterProxyModel( self )
		except:
			# > Nuke 11
			self.pFilterModel = QtCore.QSortFilterProxyModel( self )

		self.pFilterModel.setFilterCaseSensitivity( QtCore.Qt.CaseInsensitive )

		self.completer.setPopup( self.view() )

		self.setCompleter( self.completer )

		self.lineEdit().textEdited[unicode].connect( self.pFilterModel.setFilterFixedString )
		self.completer.activated.connect(self.setTextIfCompleterIsClicked)

	def createItemModel(self, comboList):
		model = QtGui.QStandardItemModel()
		for i,element in enumerate(comboList):
			item = QtGui.QStandardItem(element)
			model.setItem(i, 0, item)
		return model

	def setModel(self, model):
		super(CustomComboBox, self).setModel( model )
		self.pFilterModel.setSourceModel( model )
		self.completer.setModel(self.pFilterModel)

	def setModelColumn(self, column):
		self.completer.setCompletionColumn( column )
		self.pFilterModel.setFilterKeyColumn( column )
		super(CustomComboBox, self).setModelColumn( column )

	def addItems(self, comboList):
		super(CustomComboBox, self).addItems(comboList)
		self.setModel(self.createItemModel(comboList))

	def view( self ):
		return self.completer.popup()
 
	def index( self ):
		return self.currentIndex()

	def setTextIfCompleterIsClicked(self, text):
	  if text:
		index = self.findText(text)
		self.setCurrentIndex(index)


class ProjectLauncher(QtGuiWidgets.QDialog):
	
	def __init__(self, activeWindow, software):
		super(ProjectLauncher, self).__init__(activeWindow)
		self.jobsDir = DEFAULT_JOBS_DIR
		self.currentJobPath = ""
		self.profileDict = dict()
		self.tokenComboDict = OrderedDict()
		self.tokenDict = OrderedDict()
		self.configReader = None
		self.finalPath = ""
		self.software = software
		self.template = ""
		self.extensions = ""
		self.previousTokens = dict()
		self.initUI()
		self.populateJobs()
		self.loadRecents()
		self.show()
		print("...")

		
	def initUI(self):
		"""Initialize UI"""
		# Create job selection area ------------------------------------------------------
		self.jobSearchLocLabel = QtGuiWidgets.QLabel(self.jobsDir)
		self.jobComboBox = CustomComboBox()
		self.jobComboBox.activated[str].connect(self.onJobChange)

		jobvBox = QtGuiWidgets.QVBoxLayout()
		jobvBox.addWidget(self.jobSearchLocLabel)
		jobvBox.addWidget(self.jobComboBox)

		jobGroupBox = QtGuiWidgets.QGroupBox("Job")
		jobGroupBox.setLayout(jobvBox)

		# Profile selection area ---------------------------------------------------------
		self.profileComboBox = QtGuiWidgets.QComboBox()
		self.profileComboBox.activated[str].connect(self.onProfileChange)

		profilevBox = QtGuiWidgets.QVBoxLayout()
		profilevBox.addWidget(self.profileComboBox)

		profileGroupBox = QtGuiWidgets.QGroupBox("Profile")
		profileGroupBox.setLayout(profilevBox)

		# Token selection Area -----------------------------------------------------------

		self.formLayout = QtGuiWidgets.QFormLayout()
		self.formLayout.setFieldGrowthPolicy(self.formLayout.AllNonFixedFieldsGrow)

		self.tokenGroupBox = QtGuiWidgets.QGroupBox("Tokens")
		self.tokenGroupBox.setLayout(self.formLayout)


		# File selection Area ------------------------------------------------------------
		self.fileComboBox = CustomComboBox()
		self.fileComboBox.activated[str].connect(self.onFileChange)

		filevBox = QtGuiWidgets.QVBoxLayout()
		filevBox.addWidget(self.fileComboBox)

		fileGroupBox = QtGuiWidgets.QGroupBox("File")
		fileGroupBox.setLayout(filevBox)

		self.pathLabel = QtGuiWidgets.QLabel(self.jobsDir)

		# Launch and cancel buttons ------------------------------------------------------
		self.launchButton = QtGuiWidgets.QPushButton("Launch")
		self.launchButton.clicked.connect(self.onLaunchClick)
		# self.launchButton.setEnabled(False)
		cancelButton = QtGuiWidgets.QPushButton("Cancel")
		cancelButton.clicked.connect(self.close)

		# Layout -------------------------------------------------------------------------
		hbox = QtGuiWidgets.QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(self.launchButton)
		hbox.addWidget(cancelButton)

		vbox = QtGuiWidgets.QVBoxLayout()
		vbox.addWidget(jobGroupBox)
		vbox.addWidget(profileGroupBox)
		vbox.addWidget(self.tokenGroupBox)
		vbox.addWidget(fileGroupBox)
		vbox.addWidget(self.pathLabel)
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)

		# Select text in combo box on creation
		self.jobComboBox.setFocus()
		
		self.resize(600,0)
		self.setWindowTitle(self.software.capitalize() + " Project Launcher") 


	def onJobChange(self, job):
		self.currentJobPath = os.path.join(self.jobsDir, job)
		self.configReader = config_reader.ConfigReader(self.currentJobPath)

		# check software support for current job
		if self.configReader.checkSoftwareSupport(self.software):
			self.extensions = self.configReader.getExtensions(self.software)
			self.populateProfiles()
		else:
			self.tokenDict.clear()
			self.tokenComboDict.clear()
			self.profileComboBox.clear()
			self.template = ""
			self.createTokenCombos()
			self.debugMsg("Project does not include support for this software")

		self.pathLabel.setText(self.currentJobPath)
		# self.launchButton.setEnabled(False)
		# self.comboLabel.adjustSize()


	def onProfileChange(self, profile):
		self.template = self.configReader.getProfileTemplate(self.software, profile)
		self.createTokenCombos()
		# self.launchButton.setEnabled(False)


	def onTokenChange(self, text, thisCombo = None):
		# If no combo box passed along set it to the sender
		if thisCombo is None:
			thisCombo = self.sender()

		index = self.tokenComboDict.values().index(thisCombo)

		# Set self.tokenDict to list of all previous combos + new one
		self.tokenDict.clear()
		for token, combo in self.tokenComboDict.iteritems():
			self.tokenDict[token] = combo.currentText()
			if combo == thisCombo:
				# Set pathLabel to updated path
				currentPath = self.configReader.getPath(self.template, self.tokenDict, token)
				self.pathLabel.setText(os.path.join(currentPath, combo.currentText()))
				self.pathLabel.adjustSize()
				break

		# Always clear fileComboBox
		self.fileComboBox.clear()
		# self.launchButton.setEnabled(False)

		# Populate next token combo 
		if index+1 < len(self.tokenComboDict.values()):
			self.populateTokenCombo(self.tokenComboDict.keys()[index+1])            
		# Else, populate the file combo
		else:
			self.populateFileCombo()


	def onFileChange(self):
		# Update pathLabel to reflect new file 
		currentPath = self.configReader.getPath(self.template, self.tokenDict)
		self.finalPath = os.path.join(currentPath, self.fileComboBox.currentText())
		self.pathLabel.setText(self.finalPath)
		self.launchButton.setEnabled(True)


	def populateJobs(self):
		"""Look in jobs folder for jobs that contain the config file at root"""
		jobsList = self.getDirList(self.jobsDir)
		jobsList[:] = [job for job in jobsList if os.path.isfile(os.path.join(self.jobsDir, job, CONFIG_FILE_NAME))]
		self.jobComboBox.clear()
		self.jobComboBox.addItems(jobsList)
		self.onJobChange(jobsList[0])


	def populateProfiles(self):
		profileList = self.configReader.getLauncherProfiles(self.software).keys()
		self.profileComboBox.clear()
		self.profileComboBox.addItems(profileList)
		profile = ""
		# Check if any profiles exist
		if len(profileList) > 0:
			profile = profileList[0]
		self.onProfileChange(profile)


	def populateTokenCombo(self, token):
		comboBox = self.tokenComboDict[token]
		populatePath = self.configReader.getPath(self.template, self.tokenDict, token)
		comboBox.clear()

		folderList = self.getDirList(populatePath)
		excludeList = self.configReader.getExcludes(token)

		# Remove any occurances of excludeList from folderList
		folderList = [x for x in folderList if x not in excludeList]

		# TODO: Handle empty lists better

		# Remove template folder from list
		# tokenFolder = "[" + token + "]"
		# if tokenFolder in folderList:
		# 	folderList.remove(tokenFolder)
		comboBox.addItems(folderList)
		comboBox.setCurrentIndex(0)
		comboBox.activated.emit(0)


	def populateFileCombo(self):
		self.fileComboBox.clear()
		populatePath = self.configReader.getPath(self.template, self.tokenDict)
		fileList = self.getFileList(populatePath, self.extensions)
		# self.debugMsg("Trying to pupulate file box at this location: " + str(populatePath))
		if len(fileList) > 0:
			self.fileComboBox.addItems(fileList)
			# Set to latest version
			self.fileComboBox.setCurrentIndex(self.fileComboBox.count()-1)
			self.onFileChange()


	def createTokenCombos(self):
		"""Create a form with a combobox for each token"""

		# Remove all rows from the formLayout
		for i in reversed(range(self.formLayout.count())): 
			self.formLayout.itemAt(i).widget().setParent(None)

		self.tokenComboDict.clear()

		tokenList = self.configReader.getTokens(self.template)

		for token in tokenList:
			tokenCombo = CustomComboBox()
			index = tokenList.index(token)
			tokenCombo.activated.connect(self.onTokenChange)
			self.tokenComboDict[token] = tokenCombo
			self.formLayout.addRow(self.tr(token), tokenCombo)

			# Set tab order after layout!!
			if index == 0:
				self.setTabOrder(self.profileComboBox, tokenCombo)
			elif index < len(self.tokenComboDict):
				self.setTabOrder(self.tokenComboDict.values()[index-1], tokenCombo)

		self.fileComboBox.clear()
		if len(self.tokenComboDict) > 0:
			self.populateTokenCombo(self.tokenComboDict.keys()[0])


	def launchProject(self, filePath):
		print("Oh, I get it...")
		self.close()


	def onLaunchClick(self):
		# Update tokenDict
		for token in self.tokenComboDict:
			self.tokenDict[token] = self.tokenComboDict[token].currentText()

		currentPath = self.configReader.getPath(self.template, self.tokenDict)
		self.finalPath = os.path.join(currentPath, self.fileComboBox.currentText())

		# If the file doesn't exist, create it with project_creator
		if not os.path.isfile(self.finalPath):
			print("This file doesn't exist! " + self.finalPath)
			project_creator.createProject(self.configReader, self.template, self.tokenDict, self.software, self.fileComboBox.currentText())

		self.launchProject(self.finalPath)			
		self.saveRecents()

	def setComboBox(self, comboBox, value):
		index = comboBox.findText(value)
		if index >= 0:
			comboBox.setCurrentIndex(index)

	def readLocalConfig(self):
		localConfig = None
		try:
			with open(LOCAL_CONFIG_PATH, 'r') as stream:
				localConfig = yaml.safe_load(stream) or {}
		except IOError:
			open(LOCAL_CONFIG_PATH, 'w')
			localConfig = {}
		return localConfig

	def loadRecents(self):
		localConfig = self.readLocalConfig()
		if localConfig is not None and self.software in localConfig:
			softwareRecents = localConfig[self.software]
			self.jobsDir = softwareRecents["jobsDir"]
			self.populateJobs()
			self.setComboBox(self.jobComboBox, softwareRecents["job"])
			self.onJobChange(softwareRecents["job"])

			self.jobComboBox.setCurrentIndex(2)
			self.setComboBox(self.profileComboBox, softwareRecents["profile"])
			self.onProfileChange(softwareRecents["profile"])
			recentsTokens = softwareRecents["tokens"]
			for token in self.tokenComboDict:
				#self.setComboBox(self.tokenComboDict[token], recentsTokens[token])
				self.setComboBox(self.tokenComboDict[token], recentsTokens[token])
				self.onTokenChange(recentsTokens[token], self.tokenComboDict[token])

	def saveRecents(self):
		recentOption = dict()
		recentOption["jobsDir"] = str(self.jobsDir)
		recentOption["job"] = str(self.jobComboBox.currentText())
		recentOption["profile"] = str(self.profileComboBox.currentText())
		tokenDict = dict()
		for token in self.tokenComboDict:
			tokenDict[str(token)] = str(self.tokenComboDict[token].currentText())

		recentOption["tokens"] = tokenDict

		newConfig = self.readLocalConfig()
		newConfig[self.software] = recentOption
		with open(LOCAL_CONFIG_PATH, 'w') as outfile:
		    yaml.dump(newConfig, outfile, default_flow_style=False)

	def debugMsg(self, msg):
		'''Override this to customize how each software prints debug reports.'''
		print(msg)


	def getDirList(self, directory, reverse=False):
		"""Returns a sorted list of directories in a given directory with an optional flag to reverse the order."""
		try:
			dirs = [name for name in os.listdir(directory)
					if os.path.isdir(os.path.join(directory, name))]
		except:
			return []
		return sorted(dirs, reverse=reverse)


	def getFileList(self, directory, extensions, reverse=False):
		"""Returns a sorted list of files with a given extension in a given directory with an optional flag to reverse the order."""
		try:
			files = [name for name in os.listdir(directory)
					if (not os.path.isdir(os.path.join(directory, name))) & name.lower().endswith(tuple(extensions))]
		except:
			return []
		return sorted(files, reverse=reverse)


	def getTokenDict(self):
		return self.tokenDict

# DEBUGGING --------------------------------------------

if __name__== '__main__':
	app = QtGui.QApplication(sys.argv)
	ex = ProjectLauncher(app.activeWindow(), 'max')
	app.exec_()