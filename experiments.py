#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 9th January, 2013
Purpose: To do different experiments on the collected logs. Functions annotated
with "INTERFACE" are high-level and can be called by the user. Functions
annotated with "INTERNAL" are internal ones which may be called by the interface
functions.
'''

import adLib, adOps, adParser
import os, pylab, re, sys


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


def types_count_str(types_count):
	'''Return string form of the types_count dictionary, which has D, R and X
	as keys and their respective counts as values.'''
	return "\t".join([str(types_count["D"]), str(types_count["R"]), str(types_count["X"])])


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
		# for i in range(len(file_set_lists[user])-1, -1, -1):
			tmp_list = adParser.parse_html_set(file_set_lists[user][i])
			ad_list = adOps.union([ad_list, tmp_list])
			type_counts = adLib.ad_types_count(ad_list, ad_truth)
			churn_out += "\t".join([user, str(i+1), str(len(ad_list)), \
										types_count_str(type_counts)]) + "\n"
		
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
	if len(knees) > 2:
		knee = knees[len(knees)/2 + 1]
	else:
		knee = knees[len(knees)/2]
	print "Knee:", knee

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
	ad_truth = adLib.true_ds_of_ads("dbs/adTruth.db")

	if "base" in file_sets and "other" in file_sets:
		base_file_sets = file_sets["base"]
		other_file_sets = file_sets["other"]
	else:
		print "ERROR:", adset_file, "doesn't specify base and other accounts."
		return

	make_dir(results_dir)
	result_str = "Base\tCount\tDs\tRs\tXs\tOther\tNF\tDs\tRs\tXs\tCommon\tDs\tRs\tXs\n"

	for b in range(0, len(base_file_sets)):
		# print "BaseTrial", b
		base_ads = adParser.parse_html_set(base_file_sets[b])
		# adLib.dump_ads(base_ads, results_dir + "/base" + str(b) + ".txt")
		base_count = len(base_ads)
		base_tc = adLib.ad_types_count(base_ads, ad_truth)
		other_ads = []
		prev_diff = base_count
		printed = False

		for o in range(0, len(other_file_sets)):
			other_ads = adOps.union([other_ads, \
								adParser.parse_html_set(other_file_sets[o])])
			base_ads = adOps.difference(base_ads, other_ads)
			diff = len(base_ads)
			diff_tc = adLib.ad_types_count(base_ads, ad_truth)

			common = base_count - diff
			common_tc = {}
			for key in base_tc:
				common_tc[key] = base_tc[key] - diff_tc[key]

			if (not printed and o == len(other_file_sets)-1) or diff != prev_diff:
				printed = True
				result_str += "\t".join([str(b), str(base_count), \
								types_count_str(base_tc), str(o), str(diff), \
								types_count_str(diff_tc), str(common), \
								types_count_str(common_tc)]) + "\n"
			
			prev_diff = diff

			if diff == 0:
				break

		# adLib.dump_ads(base_ads, results_dir + "/diff" + str(b) + ".txt")

	# adLib.dump_ads(other_ads, results_dir + "/other.txt")

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


def analyze_comparison(results_file):
	'''INTERFACE: To compute various averages of a comparison.

	Args:
		results_file: File like the "results.txt" of compare_accounts.
	'''
	fd = open(results_file, "r")
	results = []

	for line in fd.readlines():
		if "Base" in line:
			continue

		words = line.strip().split()
		ints = []

		for word in words:
			ints.append(int(word))

		base = ints.pop(0)
		if base == len(results):
			results.append(ints)
		else:
			results[base] = ints

	fd.close()

	avgs = []
	for i in range(0, len(results[0])):
		avgs.append(0.0)

		for j in range(0, len(results)):
			avgs[i] += results[j][i]

		avgs[i] /= len(results)

	result = os.path.basename(results_file).strip(".txt") + "\t" + \
				str(len(results)) + "\t" + "\t".join([str(x) for x in avgs])
	print result


def analyze_comparisons(comparisons_file):
	'''INTERFACE: To compute various averages across comparisons.

	Args:
		comparisons_file: File with various analyze_comparison outputs.
	'''
	fd = open(comparisons_file, "r")
	similar_9_1 = []
	similar_1_9 = []
	similar_1_1 = []

	for line in fd.readlines():
		words = line.strip().split()

		if re.match(r'similar_1|similar_20', words[0]):
			similar_9_1.append(words[1:])
		elif re.match(r'similar_2\d-1|similar_30-20', words[0]):
			similar_1_9.append(words[1:])
		elif re.match(r'similar_[23]', words[0]):
			similar_1_1.append(words[1:])
	fd.close()

	for similar in [similar_9_1, similar_1_9, similar_1_1]:
		print len(similar)
		avg = []
		maxi = []
		mini = []

		for i in range(0, len(similar[0])):
			avg.append(0.0)
			maxi.append(0.0)
			mini.append(1000.0)

			for s in similar:
				f = float(s[i])
				avg[i] += f

				if maxi[i] <= f:
					maxi[i] = f

				if mini[i] >= f:
					mini[i] = f

			avg[i] /= len(similar)

		print "Avg", "\t".join([str(x) for x in avg])
		print "Max", "\t".join([str(x) for x in maxi])
		print "Min", "\t".join([str(x) for x in mini])
		print


# plot_churn(sys.argv[2])
# all_ads(sys.argv[1])
# unique_ads(sys.argv[1], sys.argv[2] + "/uniques.txt")
# compare_accounts(sys.argv[1], sys.argv[2])
# plot_comparison(sys.argv[1])
# analyze_comparison(sys.argv[1])
# analyze_comparisons(sys.argv[1])
