#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 30th November, 2012
Purpose: To find relevance and irrelevance of Ds.
'''

import adOps, adParser, os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


def parse_conf(filename):
	'''Read the config file containing a new-line separated list of files or
	directories and return the set of files. The files are expected to be Gmail
	HTML files.'''
	fd = open(filename, "r")
	file_set = set()

	for line in fd.readlines():
		if not line.startswith("#") and line != "\n":
			root_dir = line.strip()
			if not root_dir.startswith("/"):
				root_dir = os.getcwd() + "/" + root_dir
	
			if os.path.isfile(root_dir):
				file_set.add(root_dir)
			elif os.path.isdir(root_dir):
				for root, dirnames, filenames in os.walk(root_dir, followlinks=True):
					for filename in filenames:
						file_set.add(os.path.join(root, filename))

	fd.close()
	return file_set


def analyze_ad(all_accounts, ad_truth, ad_accounts):
	'''Give 3 sets of accounts: universal, truth, observations, find various
	statistics about the observations.'''
	result = {}
	result["tps"] = len(ad_truth & ad_accounts)
	result["fps"] = len(ad_accounts - ad_truth)
	result["tns"] = len(all_accounts - (ad_truth | ad_accounts))
	result["fns"] = len(ad_truth - ad_accounts)

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


def analyze_ads(ad_truth, ad_list):
	'''Given the Ad truth find various statistics of ads.'''
	total = {"tps":0, "fps":0, "tns":0, "fns":0}
	analyzed_ads = []

	for ad in ad_list:
		relevant_ad_truth = set()
		for ad_url in set(ad.ad_urls) & set(ad_truth.keys()):
			relevant_ad_truth |= ad_truth[ad_url]

		if len(relevant_ad_truth) == 0:
			continue

		analyzed_ad = analyze_ad(ad_truth["ALL"], relevant_ad_truth, \
						set(ad.accounts))
		analyzed_ads.append(analyzed_ad)
		print ad.get_ad_str()
		print analyzed_ad
		print "\n\n\n"

		for key in total:
			total[key] += analyzed_ad[key]

	print total
	return analyzed_ads


def make_dirs(dirname):
	'''Create the required directories for results.'''
	if not os.path.isdir(dirname):
		if os.path.exists(dirname):
			print dirname, "exists and is not a directory."
		else:
			os.makedirs(dirname)


def threshold_freq(analyzed_ads, key, value):
	'''Find the number of ads with key value >= value.'''
	count = 0

	for ad in analyzed_ads:
		if ad[key] >= value:
			count += 1

	return count


def gen_plots(analyzed_ads, results_dir):
	'''Draw plots related to accuracy, precision, recall, true negative rate.'''
	x_values = []
	value = 0
	step = 0.1
	while value <= 1:
		x_values.append(value)
		value += step

	for key in ("accuracy", "precision", "recall", "tnr"):
		y_values = []
	
		for value in x_values:
			y_values.append(threshold_freq(analyzed_ads, key, value))
	
		pylab.xlabel(key + " Threshold")
		pylab.ylabel("Number of ads above threshold")
		pylab.plot(x_values, y_values)
		pylab.savefig(results_dir + "/" + key + ".png")
		pylab.clf()


def debug_logs(ad_list, analyzed_ads, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()

	fd = open(dirname + "/analysis.txt", "w")
	string = ""
	for ad in analyzed_ads:
		string += ad.__str__() + "\n"
	fd.write(string)
	fd.flush()
	fd.close()


ad_list = adParser.parse_html_set(parse_conf(adset_file))
analyzed_ads = analyze_ads(adParser.parse_ad_truth(), ad_list)
make_dirs(results_dir)
gen_plots(analyzed_ads, results_dir)
debug_logs(ad_list, analyzed_ads, results_dir)
