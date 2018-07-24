# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys

from pipeline_config import CONFIG_FILE_NAME

def get_software():
	try:
		return os.environ['software']
	except:
		return ''

def get_profile():
	try:
		return os.environ['profile']
	except:
		return ''

def get_token_dict():
	""" Returns a dictionary of tokens associated with the current environment. """
	try:
		return ast.literal_eval(os.environ["tokens"])
	except:
		return {}

def get_token_value(token):
	""" Returns the given token from the environment if it exists. """
	try:
		return get_token_dict()[token]
	except:
		return ''

def get_jobs_dir():
	try:
		return os.environ['jobs_dir']
	except:
		return ''

def get_job():
	try:
		return os.environ["job"]
	except:
		return ''

def get_template():
		try:
		return os.environ["template"]
	except:
		return ''

def get_config_reader():
	raise NotImplementedError
