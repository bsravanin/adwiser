#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 18th November, 2012
Purpose: To find relevance and irrelevance of Ds. The sets can be either files
or directories.

18th Nov, 2012: Core operation is signatures.
13th Nov, 2012: Core operation is "intersection \ union". 
'''

import adOps, adParser, os, sys

if len(sys.argv) > 1:
	adset_file = sys.argv[1]
	DEBUG = 0

	if len(sys.argv) > 2:
		DEBUG = 1
else:
	print "Usage: python", sys.argv[0], "<adset_file> [DEBUG]"
	sys.exit(0)


def parse_line(line):
	'''Parse a line in the configuration file for HTML files.'''
	file_set = set()
	words = line.split("\t")
	account = words.pop(0)

	for word in words:
		if not word.startswith("/"):
			word = os.getcwd() + "/" + word

		if os.path.isfile(word):
			file_set.add(word)
		elif os.path.isdir(word):
			for root, dirnames, filenames in os.walk(word):
				for filename in filenames:
					file_set.add(os.path.join(root, filename))

	return account, file_set


def parse_conf(filename):
	'''In the config file, lines starting with # are ignored as comments. In
	other lines, tab is the delimiter, all files and directories are treated as
	being related to one account, identified by the first word.'''
	afd = open(filename, "r")
	accounts = {}

	for line in afd.readlines():
		line = line.strip()
		if not line.startswith("#") and line != "":
			[name, htmls] = parse_line(line.strip())
			if name in accounts:
				accounts[name]['html_set'] |= htmls
			else:
				accounts[name] = {}
				accounts[name]['html_set'] = htmls

	afd.close()

	for name in accounts:
		accounts[name]['ad_list'] = adParser.parse_html_set(accounts[name]['html_set'])

	return accounts


def signature(ad, accounts, origin=None):
	'''Returns the set of accounts in which the ad is found.'''
	sign = set()

	if origin != None:
		sign.add(origin)

	for name in accounts:
		if name != origin and adOps.belongs_to(ad, accounts[name]['ad_list']):
			sign.add(name)

	return sign


def signatures(accounts):
	'''Finds the signatures of all ads in all accounts.'''
	signs = {}

	for name in accounts:
		for ad in accounts[name]['ad_list']:
			ad_str = ad.get_ad_str()
			if ad_str not in signs:
				signs[ad_str] = signature(ad, accounts, name)

	return signs


signs = signatures(parse_conf(adset_file))
