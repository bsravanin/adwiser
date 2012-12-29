#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 28th December, 2012
Purpose: To do different experiments on the collected logs.
'''

import adOps, adParser
import os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


def churn(adset_file, results_dir):
	'''Churn is the number of ads per number of trials.'''
	file_set_lists = adParser.parse_conf(adset_file)
	churn_out = "User\tTrials\tAds\n"

	for user in file_set_lists:
		ad_list = []
		churn_out += user + "\t0\t0\n"

		for i in range(0, len(file_set_lists[user])):
			tmp_list = adParser.parse_html_set(file_set_lists[user][i])
			ad_list = adOps.union([ad_list, tmp_list])
			churn_out += user + "\t" + str(i+1) + "\t" + str(len(ad_list)) + "\n"
		
		fd = open(results_dir + "/" + user + ".txt", "w")
		fd.write(adOps.get_ads_str(ad_list))
		fd.flush()
		fd.close()

	fd = open(results_dir + "/churn.txt", "w")
	fd.write(churn_out)
	fd.flush()
	fd.close()


def save_churn_png(churn, min_uid, max_uid, results_dir):
	'''Save the churn PNG with all rings and bells.'''
	for user in churn:
		uid = int(user.strip("ccloudauditor"))
		if uid >= min_uid and uid <=max_uid:
			pylab.plot(churn[user]['x'], churn[user]['y'], "-", label=user)

	pylab.xticks(range(0, 100, 10))
	pylab.axvline(x=30, color="black")
	pylab.xlim([0, 100])
	pylab.xlabel("Trials")
	pylab.ylabel("Ads")
	pylab.title("Number of Ads Vs Number of Trials")
	pylab.legend(loc="best", prop={'size':10})
	pylab.savefig(results_dir + "/churn" + str(min_uid) + "-" + str(max_uid) + ".png")
	pylab.clf()


def plot_churn(results_dir):
	'''Plot the churn file as two PNGs.'''
	fd = open(results_dir + "/churn.txt", "r")
	churn = {}

	for line in fd.readlines():
		if "Trials" in line:
			continue

		user, trials, count = line.strip().split()
		if user in churn:
			churn[user]['x'].append(trials)
			churn[user]['y'].append(count)
		else:
			churn[user] = {}
			churn[user]['x'] = [trials]
			churn[user]['y'] = [count]

	fd.close()

	save_churn_png(churn, 10, 20, results_dir)
	save_churn_png(churn, 21, 30, results_dir)


def all_ads(adset_file):
	'''Print all ads to stderr.'''
	file_sets = adParser.parse_conf(adset_file)
	html_set = set()

	for user in file_sets:
		for file_set in file_sets[user]:
			html_set |= file_set

	adParser.parse_html_set(html_set)


def unique_ads(ads_file, unique_ads_file):
	'''Extract all unique ads from a file containing a list of ads (probably
	dumped before ad matching.'''
	ad_set = set()
	NEW_AD = 0
	ad = ""

	fd = open(ads_file, "r")
	for line in fd.readlines():
		if "START" in line:
			NEW_AD = 1
		if NEW_AD == 1:
			ad += line
		if "END" in line:
			NEW_AD = 0
			ad_set.add(ad)
			ad = ""
	fd.close()

	fd = open(unique_ads_file, "w")
	for ad in ad_set:
		fd.write(ad)
	fd.flush()
	fd.close()


if not os.path.isdir(results_dir):
	if os.path.exists(results_dir):
		print dirname, "exists and is not a directory."
	else:
		os.makedirs(results_dir)

# churn(adset_file, results_dir)
# plot_churn(results_dir)
# all_ads(adset_file)
# unique_ads(adset_file, results_dir + "/uniques.txt")

'''
AWK script to measure performance of ad matching.
awk 'BEGIN {tp=fp=fn=0} {for (i=1; i<=NF; i++) {if($i~/TP/) tp+=$i; if($i~/FP/) fp+=$i; if($i~/FN/) fn+=$i}} END {print tp" "fp" "fn}' performance_file
'''
