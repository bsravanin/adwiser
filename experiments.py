#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 30th December, 2012
Purpose: To do different experiments on the collected logs. Functions annotated
with "INTERFACE" are high-level and can be called by the user. Functions
annotated with "INTERNAL" are internal ones which may be called by the interface
functions.
'''

import adOps, adParser
import os, pylab, sys


def make_dir(dirname):
	if not os.path.isdir(dirname):
		if os.path.exists(dirname):
			print "ERROR:", dirname, "exists and is not a directory."
			sys.exit(-1)
		else:
			os.makedirs(dirname)


def churn(adset_file, results_dir):
	'''INTERFACE: Churn is the number of ads per number of trials.'''
	file_set_lists = adParser.parse_conf(adset_file)
	churn_out = "User\tTrials\tAds\n"
	make_dir(results_dir)

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


def save_churn_png(churn, min_uid, max_uid, knee, results_dir):
	'''INTERNAL: Save the churn PNG with all rings and bells.'''
	for user in churn:
		uid = int(user.strip("ccloudauditor"))
		if uid >= min_uid and uid <=max_uid:
			pylab.plot(churn[user]['x'], churn[user]['y'], "-", label=user)
			pylab.plot(churn[user]['knee_x'], churn[user]['knee_y'], "o", \
																color="black")

	pylab.xticks(range(0, 100, 10))
	pylab.axvline(x=knee, color="black")
	pylab.annotate("knee=" + str(knee), xy=(knee, 0))
	pylab.xlim([0, 100])
	pylab.xlabel("Trials")
	pylab.ylabel("Ads")
	pylab.title("Number of Ads Vs Number of Trials")
	pylab.legend(loc="best", prop={'size':10})
	pylab.savefig(results_dir + "/churn" + str(min_uid) + "-" + str(max_uid) + \
																		".png")
	pylab.clf()


def plot_churn(results_dir):
	'''INTERFACE: Plot the churn file as two PNGs.'''
	fd = open(results_dir + "/churn.txt", "r")
	churn = {}

	for line in fd.readlines():
		if "Trials" in line:
			continue

		user, trials, count = line.strip().split()
		if user in churn:
			churn[user]['x'].append(int(trials))
			churn[user]['y'].append(int(count))
		else:
			churn[user] = {}
			churn[user]['x'] = [int(trials)]
			churn[user]['y'] = [int(count)]

	fd.close()

	ratio = 0.75
	knees = []
	for user in churn:
		x_s = churn[user]['x']
		y_s = churn[user]['y']

		for i in range(0, len(x_s)):
			if y_s[i]/float(y_s[-1]) > ratio:
				churn[user]['knee_x'] = i
				churn[user]['knee_y'] = y_s[i]
				knees.append(i)
				break

	knees = sorted(knees)
	knee = knees[len(knees)/2 + 1]
	make_dir(results_dir)
	save_churn_png(churn, 10, 30, knee, results_dir)
	save_churn_png(churn, 10, 20, knee, results_dir)
	save_churn_png(churn, 21, 30, knee, results_dir)


def all_ads(adset_file):
	'''INTERFACE: Print all ads to stderr. Needs a line in adParser to be
	uncommented.'''
	file_sets = adParser.parse_conf(adset_file)
	html_set = set()

	for user in file_sets:
		for file_set in file_sets[user]:
			html_set |= file_set

	adParser.parse_html_set(html_set)


def unique_ads(ads_file, unique_ads_file):
	'''INTERFACE: Extract all unique ads from a file containing a list of ads
	(probably dumped before ad matching.'''
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

	make_dir(results_dir)
	fd = open(unique_ads_file, "w")
	for ad in ad_set:
		fd.write(ad)
	fd.flush()
	fd.close()


'''
AWK script to measure performance of ad matching.
awk 'BEGIN {tp=fp=fn=0} {for (i=1; i<=NF; i++) {if($i~/TP/) tp+=$i; if($i~/FP/) fp+=$i; if($i~/FN/) fn+=$i}} END {print tp" "fp" "fn}' performance_file
'''


def dump_ads(ad_list, filename):
	fd = open(filename, "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()


def compare_accounts(adset_file, results_dir):
	file_sets = adParser.parse_conf(adset_file)
	base_file_sets = file_sets["base"]
	other_file_sets = file_sets["other"]
	make_dir(results_dir)
	result_str = "BaseTrial\tCount\tOtherTrials\tNotFound\n"

	for b in range(0, len(base_file_sets)):
		print "BaseTrial", b
		base_ads = adParser.parse_html_set(base_file_sets[b])
		dump_ads(base_ads, results_dir + "/base" + str(b) + ".txt")
		base_count = len(base_ads)
		other_ads = []
		prev_diff = base_count

		for o in range(0, len(other_file_sets)):
			other_ads = adOps.union([other_ads, \
								adParser.parse_html_set(other_file_sets[o])])
			base_ads = adOps.difference(base_ads, other_ads)
			diff = len(base_ads)

			if diff != prev_diff:
				result_str += str(b) + "\t" + str(base_count) + "\t" + str(o) \
													+ "\t" + str(diff) + "\n"
			prev_diff = diff

			if diff == 0:
				break

		dump_ads(base_ads, results_dir + "/diff" + str(b) + ".txt")

	dump_ads(other_ads, results_dir + "/other.txt")

	fd = open(results_dir + "/results.txt", "w")
	fd.write(result_str)
	fd.flush()
	fd.close()


# churn(sys.argv[1], sys.argv[2])
# plot_churn(sys.argv[1])
# all_ads(sys.argv[1])
# unique_ads(sys.argv[1], sys.argv[2] + "/uniques.txt")
compare_accounts(sys.argv[1], sys.argv[2])
