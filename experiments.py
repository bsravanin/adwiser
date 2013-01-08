#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 8th January, 2013
Purpose: To do different experiments on the collected logs. Functions annotated
with "INTERFACE" are high-level and can be called by the user. Functions
annotated with "INTERNAL" are internal ones which may be called by the interface
functions.
'''

import adLib, adOps, adParser
import os, pylab, sys


def make_dir(dirpath):
	'''Create directory to save experiment results.

	Args:
		dirpath: Path to directory.
	'''
	if not os.path.isdir(dirpath):
		if os.path.exists(dirpath):
			print "ERROR:", dirpath, "exists and is not a directory."
			sys.exit(-1)
		else:
			os.makedirs(dirpath)


def ad_types_count(ad_list, ad_truth):
	'''INTERNAL: Count the number of targeted and untargeted ads in ad_list
	based on the ad_truth dict.

	Args:
		ad_list: List of ad objects.
		ad_truth: Two-level dictionary with AdURLs as keys, types as D/R/X and
		d_s as the (possibly empty) set of Ds.
	
	Return:
		type_counts: Dictionary with T and U as keys and counts as values.
	'''
	type_counts = {"D": 0, "R": 0, "X": 0}

	for ad in ad_list:
		url = ad.ad_urls[0]
		type_counts[ad_truth[url]["type"]] += 1

	return type_counts


def churn(adset_file, results_dir):
	'''INTERFACE: Churn is the number of ads per number of trials.

	Args:
		adset_file: Config file like "accounts.cf".
		results_dir: Directory path to save experiment results.
	'''
	file_set_lists = adParser.parse_conf(adset_file)
	ad_truth = adLib.true_ds_of_ads("dbs/adTruth.db")
	churn_out = "User\tTrials\tAll\tD\tR\tX\n"
	make_dir(results_dir)

	for user in file_set_lists:
		ad_list = []
		churn_out += "\t".join([user, "0", "0", "0", "0", "0"]) + "\n"

		for i in range(0, len(file_set_lists[user])):
			tmp_list = adParser.parse_html_set(file_set_lists[user][i])
			ad_list = adOps.union([ad_list, tmp_list])
			type_counts = ad_types_count(ad_list, ad_truth)
			churn_out += "\t".join([user, str(i+1), str(len(ad_list)), \
							str(type_counts["D"]), str(type_counts["R"]), \
							str(type_counts["X"])]) + "\n"
		
		fd = open(results_dir + "/" + user + ".txt", "w")
		fd.write(adOps.get_ads_str(ad_list))
		fd.flush()
		fd.close()

	fd = open(results_dir + "/churn.txt", "w")
	fd.write(churn_out)
	fd.flush()
	fd.close()


def avg_churn(churn, min_uid, max_uid):
	'''INTERNAL: Find the avg churn across users in a range.

	Args:
		churn: Multi-level dictionary of users, trials/total/d_s/r_s/x_s/knee_x/
		knee_y, with values for number of trials and corresponding number of
		ads, targeted ads, random ads and other targeted ads.
		min_uid: Integer between 10-30, form which user churn will be plotted.
		max_uid: Integer between 10-30, till which user churn will be plotted.

	Return:
		avgs: A dictionary of lists of avg total, d_s, r_s, x_s for each trial
		across a range of users.
	'''
	avgs = {"trials": [], "total": [], "d_s": [], "r_s": [], "x_s": []}

	for i in range(0, 100):
		users = 0

		for key in avgs:
			avgs[key].append(0)

		for user in churn:
			if "avg" in user:
				continue

			uid = int(user.strip("ccloudauditor"))

			if uid >= min_uid and uid <=max_uid:
				if len(churn[user]["trials"]) <= i:
					users = 0
					break

				users += 1

				for key in avgs:
					avgs[key][i] += churn[user][key][i]

		if users == 0:
			for key in avgs:
				avgs[key].pop()
			break
		else:
			for key in avgs:
				avgs[key][i] /= users

	return avgs


def save_churn_png(results_dir, churn, min_uid, max_uid, knee):
	'''INTERNAL: Save the churn PNG with all rings and bells.
	
	Args:
		results_dir: Directory path to save experiment results.
		churn: Multi-level dictionary of users, trials/total/d_s/r_s/x_s/knee_x/
		knee_y, with values for number of trials and corresponding number of
		ads, targeted ads, random ads and other targeted ads.
		min_uid: Integer between 10-30, form which user churn will be plotted.
		max_uid: Integer between 10-30, till which user churn will be plotted.
		knee: The "fictional" knee point for all users.
	'''
	for y_key in ["total", "d_s", "r_s", "x_s"]:
		for user in churn:
			if "avg" in user:
				continue

			uid = int(user.strip("ccloudauditor"))

			if uid >= min_uid and uid <=max_uid:
				pylab.plot(churn[user]["trials"], churn[user][y_key], "-", \
																	label=user)

				if y_key == "total":
					pylab.plot(churn[user]["knee_x"], churn[user]["knee_y"], \
															"o", color="black")

		pylab.xticks(range(0, 100, 10))
		pylab.xlim([0, 100])
		pylab.xlabel("Trials")
		pylab.legend(loc="best", prop={'size':10})

		if y_key == "total":
			pylab.axvline(x=knee, color="black")
			pylab.annotate("knee=" + str(knee), xy=(knee, 0))
			pylab.ylabel("All Ads")
			pylab.title("Number of All Ads Vs Number of Trials")
		elif y_key == "d_s":
			pylab.ylabel("TargetedDs")
			pylab.title("Number of TargetedDs Vs Number of Trials")
		elif y_key == "r_s":
			pylab.ylabel("Rs")
			pylab.title("Number of Rs Vs Number of Trials")
		elif y_key == "x_s":
			pylab.ylabel("TargetedXs")
			pylab.title("Number of TargetedXs Vs Number of Trials")

		pylab.savefig(results_dir + "/" + y_key + "-" + str(min_uid) + "-" + \
														str(max_uid) + ".png")
		pylab.clf()


def save_avg_churn_png(results_dir, churn):
	'''INTERNAL: Save the average churn PNGs.
	
	Args:
		results_dir: Directory path to save experiment results.
		churn: Multi-level dictionary of users, trials/total/d_s/r_s/x_s/knee_x/
		knee_y, with values for number of trials and corresponding number of
		ads, targeted ads, random ads and other targeted ads.
	'''
	for user in churn:
		if "avg" not in user:
			continue

		for y_key in churn[user]:
			if y_key == "trials":
				continue

			pylab.plot(churn[user]["trials"], churn[user][y_key], "-", \
													label=user + ", " + y_key)

		pylab.xticks(range(0, 100, 10))
		pylab.xlim([0, 100])
		pylab.xlabel("Trials")
		pylab.ylabel("Number of Ads")
		pylab.title("Avg. Number of Ads Vs Number of Trials")
		pylab.legend(loc="best", prop={'size':10})
		pylab.savefig(results_dir + "/" + user + ".png")
		pylab.clf()


def plot_churn(results_dir):
	'''INTERFACE: Plot the churn file as two PNGs.

	Args:
		results_dir: Directory path to save experiment results.
	'''
	fd = open(results_dir + "/churn.txt", "r")
	churn = {}

	for line in fd.readlines():
		if "Trials" in line:
			continue

		user, trials, total, d_s, r_s, x_s = line.strip().split()
		if user in churn:
			churn[user]["trials"].append(int(trials))
			churn[user]["total"].append(int(total))
			churn[user]["d_s"].append(int(d_s))
			churn[user]["r_s"].append(int(r_s))
			churn[user]["x_s"].append(int(x_s))
		else:
			churn[user] = {"trials": [int(trials)], "total": [int(total)], \
						"d_s": [int(d_s)], "r_s": [int(r_s)], "x_s": [int(x_s)]}

	fd.close()

	ratio = 0.75
	knees = []
	for user in churn:
		trials = churn[user]["trials"]
		totals = churn[user]["total"]

		for i in range(0, len(trials)):
			if totals[i]/float(totals[-1]) > ratio:
				churn[user]["knee_x"] = i
				churn[user]["knee_y"] = totals[i]
				knees.append(i)
				break

	knees = sorted(knees)
	knee = knees[len(knees)/2 + 1]

	churn["avg_10-20"] = avg_churn(churn, 10, 20)
	churn["avg_21-30"] = avg_churn(churn, 21, 30)

	make_dir(results_dir)
	save_churn_png(results_dir, churn, 10, 20, knee)
	save_churn_png(results_dir, churn, 21, 30, knee)
	save_avg_churn_png(results_dir, churn)


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
	(probably dumped before ad matching).

	Args:
		ads_file: File containing the string format of a list of ads.
		unique_ads_file: File where the unique ads seen in ads_file are written.
	'''
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


def compare_accounts(adset_file, results_dir):
	'''INTERFACE: Compare a "base" and "other" account to see which of the ads
	in "base" are found in "other".

	Args:
		adset_file: Config file like "accounts.cf" specifying "base" and "other".
		results_dir: Directory path to save experiment results.
	'''
	file_sets = adParser.parse_conf(adset_file)

	if "base" in file_sets and "other" in file_sets:
		base_file_sets = file_sets["base"]
		other_file_sets = file_sets["other"]
	else:
		print "ERROR:", adset_file, "doesn't specify base and other accounts."
		return

	make_dir(results_dir)
	result_str = "BaseTrial\tCount\tOtherTrials\tNotFound\n"

	for b in range(0, len(base_file_sets)):
		print "BaseTrial", b
		base_ads = adParser.parse_html_set(base_file_sets[b])
		adLib.dump_ads(base_ads, results_dir + "/base" + str(b) + ".txt")
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

		adLib.dump_ads(base_ads, results_dir + "/diff" + str(b) + ".txt")

	adLib.dump_ads(other_ads, results_dir + "/other.txt")

	fd = open(results_dir + "/results.txt", "w")
	fd.write(result_str)
	fd.flush()
	fd.close()


def plot_comparison(results_dir):
	'''INTERFACE: Plot the results of comparing two accounts for common ads.

	Args:
		results_dir: Directory path containing the comparison results file and
		also where the comparison plot should be saved.
	'''
	fd = open(results_dir + "/results.txt", "r")
	bases = []
	counts = []
	others = []
	misses = []
	founds = []

	for line in fd.readlines():
		if "BaseTrial" in line:
			continue

		base, count, other, missed = line.strip().split()
		base = int(base) + 1
		count = int(count)
		other = int(other) + 1
		missed = int(missed)
		found = 1 - (missed/float(count))

		if len(bases) > 0 and bases[-1] == base:
			others[-1] = other
			misses[-1] = missed
			founds[-1] = found
		else:
			bases.append(base)
			counts.append(int(count))
			others.append(other)
			misses.append(missed)
			founds.append(found)

	fd.close()

	pylab.ylim([0, 1])
	pylab.yticks(adLib.float_range(0, 1, 0.1))
	pylab.xlabel("Base Trial")
	pylab.ylabel("Fraction of Ads Found")
	pylab.plot(bases, founds, "b.", label="Found " + \
										str(round(sum(founds)/len(founds), 3)))
	pylab.legend(loc="upper left", prop={'size':10})
	pylab.title("Common Ads in Identical Accounts")

	pylab.twinx()
	pylab.xlim([0, 100])
	pylab.xticks(range(0, 100, 10))
	pylab.ylim([0, 15])
	pylab.yticks(range(0, 15, 1))
	pylab.ylabel("Number of Trials to Find Base Ads")
	pylab.plot(bases, others, "r.", label="In Trials " + \
								str(round(sum(others)/float(len(others)), 3)))
	pylab.legend(loc="lower right", prop={'size':10})

	pylab.savefig(results_dir + "/results.png")
	pylab.clf()
	print results_dir, sum(counts)/float(len(counts)), sum(misses)/float(len(misses))


# churn(sys.argv[1], sys.argv[2])
plot_churn(sys.argv[1])
# all_ads(sys.argv[1])
# unique_ads(sys.argv[1], sys.argv[2] + "/uniques.txt")
# compare_accounts(sys.argv[1], sys.argv[2])
# plot_comparison(sys.argv[1])
