#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 18th January, 2013
Purpose: To find whether ads are targeted or not, and on what if targeted.
'''


import adAnalyzer, adLib, adOps, adParser, adPlotter
import os, pylab, sys
from adGlobals import *


def get_file_set(file_sets, trials, base_account=""):
	'''Get a cumulative fileset from all user filesets except the base account
	for the specified number of trials.

	Args:
		file_sets: Dictionary with keys as users and values as a list of sets,
		where each set contains the HTML files in a trial directory.
		trials: Number of trials whose HTML files are of interest.
		base_account: The base account which will be ignored in getting the
		file_set.

	Returns:
		file_set: Set of HTML files.
	'''
	file_set = set()

	for user in file_sets:
		if user == base_account:
			continue

		for i in range(0, trials):
			max_trials = len(file_sets[user])

			if i < max_trials:
				file_set |= file_sets[user][i]
			else:
				print "WARNING:", user, "only has", max_trials, " trials."

	return file_set

'''
file_sets = adParser.parse_conf("accounts.cf")
base_file_set = file_sets["ccloudauditor10"][0]
shadow_file_set = get_file_set(file_sets, 73, "ccloudauditor10")
base_ads = adParser.parse_html_set(base_file_set)
shadow_ads = adParser.parse_html_set(shadow_file_set)
common_ads = adOps.intersection([base_ads, shadow_ads])
adAnalyzer.analyze_ads(common_ads)
adLib.dump_ads(base_ads, "tests/base.txt")
adLib.dump_ads(shadow_ads, "tests/shadow.txt")
adLib.dump_ads(common_ads, "tests/common.txt")
'''

adwiser = {"ads": adLib.load_ads(sys.argv[1])}
adwiser["prediction"] = adAnalyzer.analyze_ads(adwiser["ads"])
ad_truth = adLib.true_ds_of_ads("dbs/adTruth.db")
print adLib.ad_types_count(adwiser["ads"], ad_truth)

adwiser["truth"] = adAnalyzer.true_ds_of_ad_list(adwiser["ads"])
adwiser["verification"] = adAnalyzer.verify_predictions(adwiser)

aggregates = adAnalyzer.aggregate_verifications(adwiser)
adPlotter.draw_all_plots("tests/results", aggregates)
