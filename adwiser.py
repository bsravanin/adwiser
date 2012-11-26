#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 20th November, 2012
Purpose: To find relevance and irrelevance of Ds. The sets can be either files
or directories.

18th Nov, 2012: Core operation is signatures.
13th Nov, 2012: Core operation is "intersection \ union". 
'''

import adOps, adParser, os, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	signs_file = sys.argv[2]
	DEBUG = 0

	if len(sys.argv) > 3:
		DEBUG = 1
else:
	print "Usage: python", sys.argv[0], "<adset_file> <signs_file> [DEBUG]"
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
	ad_lists = []

	for name in accounts:
		ad_lists.append(accounts[name]['ad_list'])

	for ad in adOps.union(ad_lists):
		signs[ad.get_ad_str()] = signature(ad, accounts)

	return signs


def read_truth():
	'''Return a dictionary of truth DB.'''
	fd = open("truth.db", "r")
	truth = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			if len(words) == 2:
				truth[words[0]] = words[1]

	fd.close()
	return truth


def analyze_signatures(signs, truth):
	'''Find the precision and recall of ads.'''
	# [tps, fps, tns, fns] = [0, 0, 0, 0]
	errors = 0

	for sign in signs:
		for t in truth:
			if t in sign:
				if "No" + str(truth[t]) in signs[sign]:
					errors += 1
				else:
					print "Correctly found ad in", len(signs[sign]), "accounts."
				break

	print "Errors:", errors


def save_signatures(signs, filename):
	'''Write the signatures of all ads in all accounts to a file.'''
	sfd = open(filename, "w")
	signs_str = ""

	for sign in signs:
		signs_str += sign + "Accounts: "
		for name in sorted(list(signs[sign])):
			signs_str += name + "\t"
		signs_str += "\n" + "Count: " + str(len(signs[sign])) + "\n\n\n"

	sfd.write(signs_str)
	sfd.flush()
	sfd.close()


accounts = parse_conf(adset_file)
signs = signatures(accounts)
analyze_signatures(signs, read_truth())
save_signatures(signs, signs_file)
