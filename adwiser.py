#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 28th November, 2012
Purpose: To find relevance and irrelevance of Ds. The sets can be either files
or directories.

13th Nov, 2012: Core operation is "intersection \ union". 
18th Nov, 2012: Core operation is signatures.
28th Nov, 2012: TPs, FPs, TNs, FNs. Plots.
'''

import adOps, adParser, os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
	DEBUG = 0

	if len(sys.argv) > 3:
		DEBUG = 1
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir> [DEBUG]"
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
			for root, dirnames, filenames in os.walk(word, followlinks=True):
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
			truth[words[0]] = frozenset(words[1:])

	fd.close()
	return truth


def read_account_truth():
	'''Return a dictionary of account truths.'''
	fd = open("setup.db", "r")
	account_truth = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			account_truth[words[0]] = frozenset(words[1:])

	fd.close()
	return account_truth


def anal_sign(signature, truth, account_truth):
	'''Determine number of TPs, FPs, TNs, FNs in ad signature.'''
	result = {}
	result["tps"] = 0
	result["fps"] = 0
	result["tns"] = 0
	result["fns"] = 0

	for account in account_truth:
		if account in signature and account in truth:
			result["tps"] += 1
		elif account in signature and account not in truth:
			result["fps"] += 1
		elif account not in signature and account in truth:
			result["fns"] += 1
		elif account not in signature and account not in truth:
			result["tns"] += 1

	if (result["tps"] + result["fps"] + result["tns"] + result["fns"]) > 0:
		result["accuracy"] = (result["tps"] + result["tns"]) / \
			(float)(result["tps"] + result["fps"] + result["tns"] + result["fns"])
	else:
		result["accuracy"] = 0

	if (result["tps"] + result["fps"]) > 0:
		result["precision"] = result["tps"] / (float)(result["tps"] + result["fps"])
	else:
		result["precision"] = 0

	if (result["tps"] + result["fns"]) > 0:
		result["recall"] = result["tps"] / (float)(result["tps"] + result["fns"])
	else:
		result["recall"] = 0

	if (result["tns"] + result["fps"]) > 0:
		result["tnr"] = result["tns"] / (float)(result["tns"] + result["fps"])
	else:
		result["tnr"] = 0

	return result


def analyze_signatures(signs, truth, account_truth):
	'''Find the precision and recall of ads.'''
	total = {}
	total["tps"] = 0
	total["fps"] = 0
	total["tns"] = 0
	total["fns"] = 0
	analyzed_signs = {}

	for ad_str in signs:
		for ad_url in truth:
			if ad_url in ad_str:
				result = anal_sign(signs[ad_str], truth[ad_url], account_truth)
				analyzed_signs[ad_str] = result
				analyzed_signs[ad_str]["accounts"] = signs[ad_str]
				total["tps"] += result["tps"]
				total["fps"] += result["fps"]
				total["tns"] += result["tns"]
				total["fns"] += result["fns"]
				break

	print total
	return analyzed_signs


def save_signatures(analyzed_signs, filename):
	'''Write the signatures of all ads in all accounts to a file.'''
	sfd = open(filename, "w")
	signs_str = ""

	for ad_str in analyzed_signs:
		signs_str += ad_str + "Accounts: "
		for name in sorted(list(analyzed_signs[ad_str]["accounts"])):
			signs_str += name + "\t"
		signs_str += "\n"

		for key in sorted(analyzed_signs[ad_str]):
			if key != "accounts":
				signs_str += key + ": " + str(analyzed_signs[ad_str][key]) + "\t"
		signs_str += "\n\n\n"

	sfd.write(signs_str)
	sfd.flush()
	sfd.close()


def threshold_freq(analyzed_signs, key, value):
	'''Find the number of ads with key value >= value.'''
	count = 0

	for ad_str in analyzed_signs:
		if analyzed_signs[ad_str][key] >= value:
			count += 1

	return count


def gen_plots(analyzed_signs, results_dir):
	'''Generate plots related to accuracy, precision, recall, true negative rate.'''
	x_values = []
	value = 0
	step = 0.1
	while value <= 1:
		x_values.append(value)
		value += step

	for key in ("accuracy", "precision", "recall", "tnr"):
		y_values = []
	
		for value in x_values:
			y_values.append(threshold_freq(analyzed_signs, key, value))
	
		pylab.xlabel(key + " Threshold")
		pylab.ylabel("Number of ads above threshold")
		pylab.plot(x_values, y_values)
		pylab.savefig(results_dir + "/" + key + ".png")
		pylab.clf()


accounts = parse_conf(adset_file)
signs = signatures(accounts)

if DEBUG:
	fd.open("debug.txt", "w")
	ad_strs = ""
	for ad_str in signs:
		ad_strs += ad_str + "\n"
	fd.write(ad_strs)
	fd.flush()
	fd.close()

analyzed_signs = analyze_signatures(signs, read_truth(), read_account_truth())

if not os.path.isdir(results_dir):
	if os.path.exists(results_dir):
		print results_dir, "exists and is not a directory."
	else:
		os.makedirs(results_dir)

save_signatures(analyzed_signs, results_dir + "/signs.txt")
gen_plots(analyzed_signs, results_dir)
