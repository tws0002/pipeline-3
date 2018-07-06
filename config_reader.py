# -*- coding: utf-8 -*-
# Adam Thompson 2018

import yaml
import os

JOB_PATH_TOKEN = "job_path"
class ConfigReader:

	def __init__(self, job_path, config_path=None):
		"""Initialize configReader class with a path to the root of the job"""
		self.job_path = job_path
		self.ymlFileName = "config.yml"
		if config_path is None:
			self.configPath = os.path.join(self.job_path, self.ymlFileName)
		else:
			self.configPath = os.path.join(config_path)
		self.config = self.readConfig(self.configPath)
		self.tokenList = dict()
		self.tokenList['job_path'] = job_path

	def mergeDicts(self, x, y):
		"""Merges two dictionarys"""
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
			if token in self.tokenList and  self.tokenList.get(token):
				tokenSyntax = "<" + token + ">"
				# print("trying to replace " + token + " of this syntax: " + tokenSyntax + " with " + self.tokenList.get(token))
				# print("first it's this: " + templateString)
				formatedTemplateString = formatedTemplateString.replace(tokenSyntax, self.tokenList.get(token))
			else:
				raise ValueError("Missing token: " + token)
		# Fix path separators:
		pathList = formatedTemplateString.split("/")
		finalPath = ""
		for directory in pathList:
			if pathList.index(directory) == 0:
				finalPath = directory
			elif pathList.index(directory) >= 0:
				finalPath = os.path.join(finalPath, directory)
		return finalPath

	def getPath(self, templateString, tokenDict, destinationToken=None):
		"""Attempts to return the path to an optional destinationToken from the template and a dictionary of tokens"""
		self.tokenList = tokenDict
		self.tokenList['job_path'] = self.job_path


		if (destinationToken != None):
			destinationToken = "<" + destinationToken + ">"
			tokenIndex = templateString.find(destinationToken)
			templateString = templateString[:tokenIndex]

		return self.replaceTokens(templateString, tokenDict)

	def getTokens(self, templateString):
		"""Returns a list of tokens in the given template minus the job path which is defined when configReader is created"""
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

# if __name__== '__main__':
# 	tokens = dict()
# 	tokens["job_path"] = "V:/Jobs/XXXXXX_thompsona_testJob"
# 	tokens["spot"] = "cool_spot"
# 	tokens["shot"] = "wow_such_shot"
# 	template = "nuke_projects"
# 	software = "nuke"

# 	configReader = ConfigReader("V:/Jobs/XXXXXX_thompsona_testJob")

# 	try:
# 		templateString = configReader.getProfileTemplate(software, 'projects')
# 		fullPath = configReader.getPath(templateString, tokens)
# 		print(fullPath)
# 		print(configReader.getTokens(templateString))
# 		print(configReader.getExtensions(software))
# 		print(configReader.getLauncherProfiles(software))
# 		print(configReader.getProfileTemplate(software, 'projects'))
# 	except ValueError as e:
# 		print(e)