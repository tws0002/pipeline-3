# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import config_reader
import distutils.dir_util
from shutil import copyfile

def createProject(configReader, templateString, tokenDict, software, fileName):
	# templateString = configReader.getProfileTemplate(software, profile)
	print(configReader.getPath(templateString, tokenDict))
	tokenList = configReader.findTokens(templateString)
	# Remove "job_path" token because it isn't necessary
	if "job_path" in tokenList:
		tokenList.remove("job_path")

	print(tokenList)

	# Create folders for each missing token
	# TODO: Better error handling
	missingToken = ""
	pathToMissingToken = ""
	for token in tokenList:
		createToken(configReader, templateString, tokenDict, token)

	_, fileExtension = os.path.splitext(fileName)
	print("fileExtension = " + fileExtension)

	pathToSoftwareFile = os.path.join(configReader.getTemplateDirectory(), (software+fileExtension))
	print("pathToSoftwareFile = " + pathToSoftwareFile)

	newFilePath = os.path.join(configReader.getPath(templateString, tokenDict), fileName)
	print("newFilePath = " + newFilePath)
	copyfile(pathToSoftwareFile, newFilePath)

def createToken(configReader, templateString, tokenDict, token, tokenValue=""):
	""" Creates a new folder based on the given token. """
	if not tokenValue:
		tokenValue = tokenDict[token]
	pathToToken = os.path.join(configReader.getPath(templateString, tokenDict, token), tokenValue)
	if not os.path.isdir(pathToToken):
		missingToken = token
		pathToMissingToken = pathToToken
		templateTokenFolder = os.path.join(os.path.dirname(pathToMissingToken),".[" + token + "]")
		print("template token folder: " + templateTokenFolder)
		distutils.dir_util.copy_tree(templateTokenFolder, pathToMissingToken)




# if __name__== '__main__':
# 	software = "houdini"
# 	profile = "shots"
# 	fileName = "fileName.hip"

# 	tokenDict = {'spot': 'Spot_01', 'shot': 'cool_shot2', 'step': 'lighting'}

# 	configReader = config_reader.ConfigReader("C:/Users/athompson/dev/XXXXXX_carbon_testJob2")
# 	createProject(configReader, profile, tokenDict, software, fileName)