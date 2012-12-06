#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th December, 2012
Purpose: To find relevance and irrelevance of Ds.
'''

import adAnalyzer, adOps, adParser
import os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


debug_str = ""


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


def analyze_ad(ds_of_ad, true_ds_of_ad, all_ds, threshold):
	'''Given 3 lists of Ds: Ds along with their confidence levels based on
	observations, true Ds, and all possible Ds, find TPs, FPs, TNs, FNs given
	a minimum confidence level to predict.'''
	global debug_str
	targeted = set()
	true_targeted = true_ds_of_ad
	true_untargeted = all_ds - true_ds_of_ad

	# if ds_of_ad["confidence"] >= threshold:
		# targeted = ds_of_ad["prediction"]
	for d in all_ds:
		if d in ds_of_ad and ds_of_ad[d]["confidence"] >= threshold:
			targeted.add(d)

	untargeted = all_ds - targeted

	result = {}
	result["tps"] = len(targeted & true_targeted)
	result["fps"] = len(targeted & true_untargeted)
	result["tns"] = len(untargeted & true_untargeted)
	result["fns"] = len(untargeted & true_targeted)
	debug_str += "analyze_ad " + str(threshold) + " " + result.__str__() + "\n"
	return result


def analyze_ads(ds_of_ads, true_ds_of_ads, all_ds, threshold):
	'''Analyze expected Ds of ads against the Ad truth, given a confidence
	level for prediction.'''
	global debug_str 
	total = {"tps":0, "fps":0, "tns":0, "fns":0}

	for i in range(0, len(ds_of_ads)):
		analyzed_ad = analyze_ad(ds_of_ads[i], true_ds_of_ads[i], all_ds, threshold)

		for key in total:
			total[key] += analyzed_ad[key]

	total = adAnalyzer.compute_stats(total)
	debug_str += "analyze_ads " + str(threshold) + " " + total.__str__() + "\n"
	return total


def analyze_ads_all_thresholds(ds_of_ads, true_ds_of_ads, all_ds):
	'''Analyze expected Ds of ads against the Ad truth, for different confidence
	levels of prediction.'''
	results = {}
	threshold = 0
	step = 0.1

	while threshold < 1:
		results[threshold] = analyze_ads(ds_of_ads, true_ds_of_ads, all_ds, \
																	threshold)
		threshold += step

	return results


def make_dirs(dirname):
	'''Create the required directories for results.'''
	if not os.path.isdir(dirname):
		if os.path.exists(dirname):
			print dirname, "exists and is not a directory."
		else:
			os.makedirs(dirname)


def single_plot(results, results_dir, key):
	'''Plot a single key against threshold values.'''
	x_values = sorted(results.keys())
	y_values = []

	for threshold in x_values:
		y_values.append(results[threshold][key])

	pylab.xlabel("Threshold")
	pylab.ylabel(key)
	pylab.plot(x_values, y_values, "bo-")
	pylab.savefig(results_dir + "/" + key + ".png")
	pylab.clf()


def double_plot(results, results_dir, key1, key2):
	'''Plots two keys against one another.'''
	x_values = []
	y_values = []

	for threshold in sorted(results.keys()):
		x_values.append(results[threshold][key1])
		y_values.append(results[threshold][key2])

	pylab.xlabel(key1)
	pylab.ylabel(key2)
	pylab.plot(x_values, y_values, "bo-")
	pylab.savefig(results_dir + "/" + key1 + "-" + key2 + ".png")
	pylab.clf()


def gen_plots(results, results_dir):
	'''Draw various plots.'''
	for key in ("accuracy", "precision", "recall", "tnr"):
		single_plot(results, results_dir, key)

	double_plot(results, results_dir, "precision", "recall")
	double_plot(results, results_dir, "recall", "precision")


def debug_logs(ad_list, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()

	fd = open(dirname + "/debug.txt", "w")
	fd.write(debug_str)
	fd.flush()
	fd.close()


account_truth = adAnalyzer.true_ds_of_accounts()
ds_truth = adAnalyzer.true_accounts_of_ds()
ad_truth_ds = adAnalyzer.true_ds_of_ads()
# ad_truth_accounts = adAnalyzer.true_accounts_of_ads()

ad_list = adParser.parse_html_set(parse_conf(adset_file))
true_ds_of_ads = adAnalyzer.true_ds_of_ad_list(ad_list, ad_truth_ds)
ds_of_ads = adAnalyzer.ds_of_ad_list(ad_list, account_truth, ds_truth)
results = analyze_ads_all_thresholds(ds_of_ads, true_ds_of_ads, account_truth["ALL"])
make_dirs(results_dir)
gen_plots(results, results_dir)
debug_logs(ad_list, results_dir)
