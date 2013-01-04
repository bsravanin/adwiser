#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd January, 2013
Purpose: To find whether ads are targeted or not, and on what if targeted.
'''

import adAnalyzer, adLib, adOps, adParser, adPlotter
import os, pylab, sys


def get_file_set(file_sets, trials):
	'''Get a cumulative fileset from all user filesets for the specified number
	of trials.'''
	file_set = set()

	for user in file_sets:
		if user == "ccloudauditor10":
			continue

		for i in range(0, trials):
			max_trials = len(file_sets[user])

			if i < max_trials:
				file_set |= file_sets[user][i]
			else:
				print "WARNING:", user, "only has", max_trials, " trials."

	return file_set


def debug_logs(ad_list, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()


# ad_truth_accounts = adAnalyzer.true_accounts_of_ads()

'''
file_sets = adParser.parse_conf("accounts.cf")
base_file_set = file_sets["ccloudauditor10"][0]
shadow_file_set = get_file_set(file_sets, 34)
base_ads = adParser.parse_html_set(base_file_set)
shadow_ads = adParser.parse_html_set(shadow_file_set)
common_ads = adOps.intersection([base_ads, shadow_ads])
analyze_ads(common_ads)
adLib.dump_ads(base_ads, "base.txt")
adLib.dump_ads(shadow_ads, "shadow.txt")
adLib.dump_ads(common_ads, "common.txt")
'''

adwiser = {"ads": adLib.load_ads("common.txt")}
adwiser["truth"] = adAnalyzer.true_ds_of_ad_list(adwiser["ads"])
adwiser["prediction"] = adAnalyzer.analyze_ads(adwiser["ads"])
adwiser["verification"] = adAnalyzer.verify_predictions(adwiser)

aggregates = adAnalyzer.aggregate_verifications(adwiser["verification"])
adPlotter.draw_all_plots(sys.argv[1], aggregates)
