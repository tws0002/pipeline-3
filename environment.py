# -*- coding: utf-8 -*-
# Adam Thompson 2018

import os
import sys

import config_reader

from pipeline_config import CONFIG_FILE_NAME

def is_valid(software=None):
	""" Return if the current environment is valid. Given a software, it will check if it matches."""
	check_software = (not software or software == get_software())
	return bool(get_jobs_dir() and get_job()) and check_software

def set_environment(software, jobs_dir, job, profile, token_dict):
	os.environ['software'] = str(software)
	os.environ['jobs_dir'] = str(jobs_dir)
	os.environ['job'] = str(job)
	os.environ['profile'] = str(profile)
	os.environ['token_dict'] = str(token_dict)

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
	job_path = os.path.join(get_jobs_dir(), get_job())
	env_config_reader = config_reader.ConfigReader(job_path)
	return env_config_reader


# DEBUG------------------------------------------------------------------------
if __name__ == '__main__':
	set_environment('cool', 'also_cool', 'job', 'profile', 'token_dict')
	print(is_valid())