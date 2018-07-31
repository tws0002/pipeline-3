# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys
import config_reader
import distutils.dir_util
from shutil import copyfile

def createProject(configReader, templateString, tokenDict, software, fileName):
    """ Creates the necessary folders and a project file. Returns the path to the file created. """
    # templateString = configReader.get_profile_template(software, profile)
    print(configReader.get_path(templateString, tokenDict))
    tokenList = configReader.find_tokens(templateString)
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

    # If no file extension is defined, grab the first file extension from that software's config
    if not fileExtension:
        try:
            fileExtension = configReader.get_extensions(software)[0]
            fileName = fileName + fileExtension
        except:
            print("No file extensions for the current software: " + software)

    pathToSoftwareFile = os.path.join(
        configReader.get_template_directory(), (software+fileExtension))
    print("pathToSoftwareFile = " + pathToSoftwareFile)

    newFilePath = os.path.join(configReader.get_path(templateString, tokenDict), fileName)
    print("newFilePath = " + newFilePath)
    copyfile(pathToSoftwareFile, newFilePath)

    return newFilePath

def createToken(configReader, templateString, tokenDict, token, tokenValue=""):
    """ Creates a new folder based on the given token. """
    if not tokenValue:
        tokenValue = tokenDict[token]
    pathToToken = os.path.join(configReader.get_path(templateString, tokenDict, token), tokenValue)
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
