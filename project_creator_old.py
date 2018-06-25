# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import config_reader
import distutils.dir_util
import shutil

FOLDER_STRUCT_TEMPLATE_PATH = "V:/Jobs/XXXXXX_carbon_testJob2/Pipeline"

def createProject(configReader, profile, tokenDict, software, fileName):
	templateString = configReader.getProfileTemplate(software, profile)
	print(configReader.getPath(templateString, tokenDict))
	tokenList = configReader.findTokens(templateString)
	# Remove "job_path" token because it isn't necessary
	if "job_path" in tokenList:
		tokenList.remove("job_path")

	print(tokenList)

	# Find first instance of a missing token
	missingToken = ""
	pathToMissingToken = ""
	for token in tokenList:
		pathToToken = os.path.join(configReader.getPath(templateString, tokenDict, token), tokenDict[token])
		if not os.path.isdir(pathToToken):
			missingToken = token
			pathToMissingToken = pathToToken
			break

	# Create new config reader for template directory
	templateDir = configReader.getTemplateDirectory()
	configPath = configReader.getConfigPath()
	templateConfigReader = config_reader.ConfigReader(templateDir, configPath)

	# Create folder template formated token dictionary
	templateTokenDict = {}
	for token in tokenDict:
		templateTokenDict[token] = "[" + token + "]"

	# Syncronized path to template directory
	pathToMissingTemplateToken = os.path.join(templateConfigReader.getPath(templateString, templateTokenDict, missingToken), templateTokenDict[missingToken])

	# Copy to new location
	newTokenDirectory = os.path.join(os.path.dirname(pathToMissingToken), tokenDict[missingToken])
	print("newTokenDirectory = " + newTokenDirectory)
	distutils.dir_util.copy_tree(pathToMissingTemplateToken, pathToMissingToken)

	# createTempDir(pathToMissingTemplateToken)

	print("Path to missing token: " + pathToMissingToken)
	print("Path to missing template token: " + pathToMissingTemplateToken)



	# rmDirectory(tempDir)

def createTempDir(directory):
	# Create a duplicate directory preceded by a "." and return that path
	basename = os.path.basename(directory)
	dirname = os.path.dirname(directory)

	tempDir = os.path.join(dirname, ("." + basename))
	print(tempDir)

	distutils.dir_util.copy_tree(directory, tempDir)

	return tempDir

def rmDirectory(dir):
	if query_yes_no("Are you sure you want to delete this folder: " + dir):
		shutil.rmtree(dir)
	else:
		print("nevermind...")


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__== '__main__':
	software = "houdini"
	profile = "shots"
	fileName = "fileName.hip"

	tokenDict = {'spot': 'Spot_01', 'shot': 'cool_shot', 'step': 'cool_step'}

	configReader = config_reader.ConfigReader("C:/Users/athompson/dev/XXXXXX_carbon_testJob2")
	createProject(configReader, profile, tokenDict, software, fileName)