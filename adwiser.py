#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd December, 2012
Purpose: To find relevance and irrelevance of Ds.
'''

import adOps, adParser, os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


analysis_str = ""


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


def ds_of_ad_list(ad_list):
	'''Find the Ds, their frequencies, and confidence levels of being targeted
	by an ad for all ads in a list, based on the account truth.'''
	account_truth = adParser.true_ds_of_accounts()
	ds_truth = adParser.true_accounts_of_ds()
	ds_of_ads = []

	for ad in ad_list:
		ds_of_ad = {}

		for account in ad.accounts:
			for d in account_truth[account]:
				if d in ds_of_ad:
					ds_of_ad[d]["accounts"] += 1
					ds_of_ad[d]["count"] += ad.accounts[account]
				else:
					ds_of_ad[d] = {"accounts":1, "count":ad.accounts[account]}

		for d in ds_of_ad:
			ds_of_ad[d]["account_confidence"] = \
					ds_of_ad[d]["accounts"] / float(len(ds_truth[d]))
			ds_of_ad[d]["count_confidence"] = 0

		max_confidence = max(ds_of_ad[x]["account_confidence"] for x in ds_of_ad)
		max_ds = set()
		for d in ds_of_ad:
			if ds_of_ad[d]["account_confidence"] == max_confidence:
				max_ds.add(d)

		ds_of_ad["prediction"] = max_ds
		ds_of_ad["prediction_confidence"] = max_confidence
		ds_of_ads.append(ds_of_ad)

	return ds_of_ads, account_truth["ALL"]


def true_ds_of_ad_list(ad_list):
	'''Find the true Ds of ads in the list.'''
	true_ds_of_ads = []
	ad_truth = adParser.true_ds_of_ads()

	for ad in ad_list:
		true_ds_of_ad = set()

		for url in set(ad.ad_urls) & set(ad_truth):
			true_ds_of_ad |= ad_truth[url]

		true_ds_of_ads.append(true_ds_of_ad)

	return true_ds_of_ads


def analyze_ad(ds_of_ad, true_ds_of_ad, all_ds, threshold):
	'''Given 3 lists of Ds: Ds along with their confidence levels based on
	observations, true Ds, and all possible Ds, find TPs, FPs, TNs, FNs given
	a minimum confidence level to predict.'''
	global analysis_str
	targeted = set()
	true_targeted = true_ds_of_ad
	true_untargeted = all_ds - true_ds_of_ad

	if ds_of_ad["prediction_confidence"] >= threshold:
		targeted = ds_of_ad["prediction"]

	untargeted = all_ds - targeted

	result = {}
	result["tps"] = len(targeted & true_targeted)
	result["fps"] = len(targeted & true_untargeted)
	result["tns"] = len(untargeted & true_untargeted)
	result["fns"] = len(untargeted & true_targeted)
	analysis_str += "analyze_ad " + str(threshold) + " " + result.__str__() + "\n"
	return result


def analyze_ads(ds_of_ads, true_ds_of_ads, all_ds, threshold):
	'''Analyze expected Ds of ads against the Ad truth, given a confidence
	level for prediction.'''
	global analysis_str
	total = {"tps":0, "fps":0, "tns":0, "fns":0}

	for i in range(0, len(ds_of_ads)):
		analyzed_ad = analyze_ad(ds_of_ads[i], true_ds_of_ads[i], all_ds, \
																	threshold)

		for key in total:
			total[key] += analyzed_ad[key]

	if (total["tps"] + total["fps"] + total["tns"] + total["fns"]) > 0:
		total["accuracy"] = (total["tps"] + total["tns"]) / \
			float(total["tps"] + total["fps"] + total["tns"] + total["fns"])
	else:
		total["accuracy"] = 0

	if (total["tps"] + total["fps"]) > 0:
		total["precision"] = total["tps"] / float(total["tps"] + total["fps"])
	else:
		total["precision"] = 0

	if (total["tps"] + total["fns"]) > 0:
		total["recall"] = total["tps"] / float(total["tps"] + total["fns"])
	else:
		total["recall"] = 0

	if (total["tns"] + total["fps"]) > 0:
		total["tnr"] = total["tns"] / float(total["tns"] + total["fps"])
	else:
		total["tnr"] = 0

	analysis_str += "analyze_ads " + str(threshold) + " " + total.__str__() + "\n"
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


def gen_plots(results, results_dir):
	'''Draw plots related to accuracy, precision, recall, true negative rate.'''
	x_values = sorted(results.keys())

	for key in ("accuracy", "precision", "recall", "tnr"):
		y_values = []

		for threshold in x_values:
			y_values.append(results[threshold][key])

		pylab.xlabel("Threshold")
		pylab.ylabel(key)
		pylab.plot(x_values, y_values)
		pylab.savefig(results_dir + "/" + key + ".png")
		pylab.clf()


def debug_logs(ad_list, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()

	fd = open(dirname + "/analysis.txt", "w")
	fd.write(analysis_str)
	fd.flush()
	fd.close()


ad_list = adParser.parse_html_set(parse_conf(adset_file))
ds_of_ads, all_ds = ds_of_ad_list(ad_list)
true_ds_of_ads = true_ds_of_ad_list(ad_list)
results = analyze_ads_all_thresholds(ds_of_ads, true_ds_of_ads, all_ds)
make_dirs(results_dir)
gen_plots(results, results_dir)
debug_logs(ad_list, results_dir)
