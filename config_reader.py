# -*- coding: utf-8 -*-
# Adam Thompson 2018

import yaml
import os

JOB_PATH_TOKEN = "job_path"
from pipeline_config import CONFIG_FILE_NAME
class ConfigReader:

	def __init__(self, job_path, config_path=None):
		"""Initialize configReader class with a path to the root of the job"""
		self.job_path = job_path
		if config_path is None:
			self.configPath = os.path.join(self.job_path, CONFIG_FILE_NAME)
		else:
			self.configPath = os.path.join(config_path)
		self.config = self.readConfig(self.configPath)

	def mergeDicts(self, x, y):
		"""Merges two dictionarys. Overwrites values of the first dictionary with the second. """
		z = x.copy()
		z.update(y)
		return z

	def readConfig(self, configPath):
		"""Reads the config file and returns a dictionary"""
		with open(configPath) as stream:
			try:
				config = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
		return config

	def replaceTokens(self, templateString, tokenDict):
		"""Takes a templateString and attempts to create a path with a dictionary of tokens and values"""
		templateTokens = self.findTokens(templateString)
		formatedTemplateString = templateString
		for token in templateTokens:
			if token in tokenDict and tokenDict.get(token):
				tokenSyntax = "<" + token + ">"
				# print("trying to replace " + token + " of this syntax: " + tokenSyntax + " with " + self.tokenList.get(token))
				# print("first it's this: " + templateString)
				formatedTemplateString = formatedTemplateString.replace(tokenSyntax, tokenDict.get(token))
			else:
				pass
				# raise ValueError("Missing token: " + token)

		# If there are still unreplaced tokens in the tokenDict, in the path, recursively replace them
		remaining_tokens = self.findTokens(formatedTemplateString)

		
		# more_left = False
		# for remaining_token in remaining_tokens:
		# 	if remaining_token in tokenDict:
		# 		more_left = True
		
		# Check if any of the remaining tokens exist in tokenDict and are not empty
		non_empty_token_dict = {token:value for (token,value) in tokenDict.items() if value}
		if any(x in remaining_tokens for x in non_empty_token_dict):
			formatedTemplateString = self.replaceTokens(formatedTemplateString, tokenDict)

		# Fix path separators:
		pathList = formatedTemplateString.split("/")
		finalPath = ""
		for directory in pathList:
			if pathList.index(directory) == 0:
				finalPath = directory
			elif pathList.index(directory) >= 0:
				finalPath = os.path.join(finalPath, directory)

		return finalPath

	def getGlobals(self):
		""" Returns a dictionary of global variables. """
		try:
			return self.config['globals']
		except:
			return dict()

	def getNameProfileTemplate(self, profile, software=None):
		""" Returns the template for a name if it exists in globals or a software override. """
		name_template = ''
		if 'name_profiles' in self.getGlobals():
			name_profiles = self.getGlobals()['name_profiles']
			try: 
				name_template = name_profiles[profile]
			except:
				pass
		if software and 'name_profiles' in self.getSoftwareConfig(software):
			name_profiles = self.getSoftwareConfig(software)['name_profiles']
			try:
				name_template = name_profiles[profile]
			except:
				pass
		return name_template
			

	def getName(self, profile, tokenDict, software=None, ver="001"):
		name_template = self.getNameProfileTemplate(profile, software)
		tokenDict["ver"] = "v"+ver
		tokenDict = self.mergeDicts(self.getGlobals(), tokenDict)
		name = self.replaceTokens(name_template, tokenDict)
		return name

	def getPath(self, templateString, tokenDict, destinationToken=None):
		"""Attempts to return the path to an optional destinationToken from the template and a dictionary of tokens"""
		tokenDict['job_path'] = self.job_path

		tokenDict = self.mergeDicts(self.getGlobals(), tokenDict)

		templateString = self.replaceTokens(templateString, self.getGlobals())

		if (destinationToken != None):
			destinationToken = "<" + destinationToken + ">"
			tokenIndex = templateString.find(destinationToken)
			templateString = templateString[:tokenIndex]

		templateString = self.replaceTokens(templateString, tokenDict)

		return templateString

	def getTokens(self, templateString):
		"""Returns a list of tokens in the given template minus the job path which is defined when configReader is created"""
		# First, expand the template string with all the globals
		templateString = self.replaceTokens(templateString, self.getGlobals())
		tokens = self.findTokens(templateString)
		if JOB_PATH_TOKEN in tokens:
			tokens.remove(JOB_PATH_TOKEN)
		return tokens


	def findTokens(self, templateString):
		"""Finds tokens in a template and returns them in a list"""
		i = 0
		tokenList = list()
		while (i >= 0):
			i = templateString.find('<', i, len(templateString))
			if (i >= 0) : 
				start = i+1
				i = templateString.find('>', i, len(templateString))
				if (i > 0):
					end = i
					tokenList.append(templateString[start:end])
				else:
					break
			else: 
				break
		return tokenList

	def getSoftwareConfig(self, software):
		""" Returns the config dictionary for the given software. """
		softwareConfig = dict()
		try: 
			softwareConfig = self.config['software'][software]

		except: 
			print("Software not supported in this yaml config")

		return softwareConfig

	def checkSoftwareSupport(self, software):
		if 'software' in self.config.keys() and software in self.config['software']:
			return True
		return False

	def getLauncherProfiles(self, software):
		"""Return a list of profiles for current software"""
		launcher_profiles = dict()

		try: 
			launcher_profiles = self.getSoftwareConfig(software)['launcher_profiles']
		except:
			print("launcher_profiles not found in project config")

		return launcher_profiles

	def getExtensions(self, software):
		extensions = []
		try: 
			extensions = self.getSoftwareConfig(software)['extensions']
		except:
			print("No extensions found in project config!")

		return extensions

	def getHooksPath(self, software):
		try: 
			hook_path = self.getSoftwareConfig(software)['hooks']
			return hook_path
		except:
			return ''
		
	def getProfileTemplate(self, software, profile):
		profileTemplate = self.getLauncherProfiles(software)[profile]
		return profileTemplate

	def getExcludes(self, token):
		"""Return a list of all excludes associated with the given token"""
		excludes = []
		if 'exclude' in self.config.keys():
			if token in self.config['exclude'].keys():
				excludes = self.config['exclude'][token]
		return excludes

	def getTemplateDirectory(self):
		# TODO Error handling non-existant "template_directory"
		path = self.config["template_directory"]
		return self.getPath(path, {})

	def getConfigPath(self):
		return self.configPath

	def sayHello(self):
		return "Hello there!"

# DEBUG ------------------------------------------------------------------------------------------------------

if __name__== '__main__':
	tokens = dict()
	tokens["job_path"] = "V:/Jobs/XXXXXX_carbon_testJob4"
	tokens["spot"] = "cool_spot"
	tokens["shot"] = "shot01"
	tokens["step"] = "modeling"
	template = "nuke_projects"
	software = "nuke"
	profile = 'shots'

	configReader = ConfigReader("V:/Jobs/XXXXXX_carbon_testJob4")

	print(configReader.getNameProfileTemplate('assets'))
	print(configReader.getName(profile,tokens, ver="001"))
	print(configReader.getPath(configReader.getProfileTemplate(software, profile), tokens))

	# print(configReader.mergeDicts({'a':'1','b':'1'},{'a':'a','b':'b','c':'c'}))
