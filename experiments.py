#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 1st February, 2013
Purpose: To do different experiments on the collected logs. Functions annotated
with "INTERFACE" are high-level and can be called by the user. Functions
annotated with "INTERNAL" are internal ones which may be called by the interface
functions.
'''


import adAnalyzer, adLib, adOps, adParser
import ast, os, pylab, re, sys


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


def write_conf(base, other):
	'''Write a conf file for comparing accounts.'''
	fd = open("tests/test.cf", "w")
	conf_str = "base\tlogs/ccloudauditor" + str(base) + "\n" + \
				"other\tlogs/ccloudauditor" + str(other) + "\n"
	fd.write(conf_str)
	fd.flush()
	fd.close()


def analyze_areas(areas_file):
	'''INTERFACE: Analyze the precision-recall areas for various models, alphas,
	betas, thresholds, and find the optimal parameters.

	Args:
		areas_file: A file of areas dump, e.g. "results/models_34t/areas.txt"
	'''
	fd = open(areas_file, "r")
	areas = {}
	max_areas = {}
	models = set()
	alphas = set()
	betas = set()
	thresholds = set()

	for line in fd.readlines():
		words = line.strip().split(". ")
		model = words.pop(0)
		area = float(words.pop())
		alpha = beta = threshold = -1

		for word in words:
			if word.startswith("Alpha"):
				alpha = round(float(word.lstrip("Alpha ")), 1)
			elif word.startswith("Beta"):
				beta = round(float(word.lstrip("Beta ")), 1)
			elif word.startswith("Threshold"):
				threshold = round(float(word.lstrip("Threshold ")), 1)

		if alpha == 0 or beta == 0:
			continue

		if model not in areas:
			areas[model] = {}
			max_areas[model] = {"ab": 0, "at": 0, "bt": 0}

		if alpha not in areas[model]:
			areas[model][alpha] = {}

		if beta not in areas[model][alpha]:
			areas[model][alpha][beta] = {}

		areas[model][alpha][beta][threshold] = area

		if threshold == -1 and max_areas[model]["ab"] < area:
			max_areas[model]["ab"] = area
		elif beta == -1 and max_areas[model]["at"] < area:
			max_areas[model]["at"] = area
		elif alpha == -1 and max_areas[model]["bt"] < area:
			max_areas[model]["bt"] = area

		models.add(model)
		alphas.add(alpha)
		betas.add(beta)
		thresholds.add(threshold)

	fd.close()

	alphas -= set([-1])
	betas -= set([-1])
	thresholds -= set([-1])

	for model in models:
		for alpha in alphas:
			for beta in betas:
				area1 = areas[model][alpha][beta][-1]
				area2 = areas[model][beta][alpha][-1]
				if area1 == area2:
					print "Equal area", model, alpha, beta
				else:
					print "Unequal area", model, alpha, beta, area1, area2

				if areas[model][alpha][beta][-1] == max_areas[model]["ab"]:
					print "AB", model, alpha, beta, max_areas[model]["ab"]

		for alpha in alphas:
			for threshold in thresholds:
				if areas[model][alpha][-1][threshold] == max_areas[model]["at"]:
					print "AT", model, alpha, threshold, max_areas[model]["at"]

		for beta in betas:
			for threshold in thresholds:
				if areas[model][-1][beta][threshold] == max_areas[model]["bt"]:
					print "BT", model, beta, threshold, max_areas[model]["bt"]


def compute_prs(ads_file):
	'''INTERFACE: Compute precision and recall for various combinations of
	model, alpha, beta, threshold for the set of ads dumped into a file.

	Args:
		ads_file: File containing dumped ads. Usually after merging across
		accounts.
	'''
	adwiser = {"ads": adLib.load_ads(ads_file)}
	adwiser["prediction"] = adAnalyzer.analyze_ads(adwiser["ads"])
	# Uncomment below line to try all possible thresholds.
	# adwiser["scores"] = adAnalyzer.get_scores(adwiser["prediction"])
	adwiser["truth"] = adAnalyzer.true_ds_of_ad_list(adwiser["ads"])
	adwiser["verification"] = adAnalyzer.verify_predictions(adwiser)
	adAnalyzer.aggregate_verifications(adwiser, True)


def show_verifications(ads_file):
	'''INTERFACE: Print the verifications of predictions made for the set of
	ads dumped into a file.

	Args:
		ads_file: File containing dumped ads. Usually after merging across
		accounts.
	'''
	adwiser = {"ads": adLib.load_ads(ads_file)}
	adwiser["prediction"] = adAnalyzer.analyze_ads(adwiser["ads"])
	adwiser["truth"] = adAnalyzer.true_ds_of_ad_list(adwiser["ads"])
	adwiser["verification"] = adAnalyzer.verify_predictions(adwiser)

	for i in range(0, len(adwiser["ads"])):
		print adwiser["ads"][i].get_ad_str(), adwiser["prediction"][i]
		print adwiser["verification"][i]
		print


def dump_all_ads(conf_file, results_dir):
	file_sets = adParser.parse_conf("accounts.cf")
	shadow_ads = []

	make_dir(results_dir + "/base")
	make_dir(results_dir + "/shadow")

	print "Trial Base Shadow Cumulative"
	for i in range(0, 91):
		base_file_set = file_sets["ccloudauditor10"][i]
		base_ads = adParser.parse_html_set(base_file_set)
		adLib.dump_ads(base_ads, results_dir + "/base/base_" + str(i) + ".txt")
		shadow_file_set = adParser.get_file_set(file_sets, i, "ccloudauditor10")
		sads = adParser.parse_html_set(shadow_file_set)
		shadow_ads = adOps.union([shadow_ads, sads])
		adLib.dump_ads(shadow_ads, results_dir + "/shadow/shadow_" + str(i) + ".txt")
		print i, len(base_ads), len(sads), len(shadow_ads)


'''
Common + Diff ads.
for i in range(0, 91):
	print i
	for j in [9, 33, 72, 90]:
		base_ads = adLib.load_ads("results/dumped_ads/base/base_" + str(i) + \
																		".txt")
		shadow_ads = adLib.load_ads("results/dumped_ads/shadow/shadow_" + \
																str(j) + ".txt")
		common_ads = adOps.intersection([base_ads, shadow_ads])
		adOps.difference(base_ads, common_ads)
		adLib.dump_ads([base_ads, common_ads], \
						"results/dumped_ads/analyzed/analyzed_" + str(i) + \
						"_" + str(j) + ".txt")
'''


def find_good_abs(pr_file):
	'''INTERNAL: Find the set of (alpha, beta) tuples in a precision-recall file
	for which both precision and recall are at least min_val.

	Args:
		pr_file: File with model, alpha, beta, threshold, precision, recall
		records.

	Return:
		Directory of sets of (alpha, beta) tuples.
	'''
	fd = open(pr_file, "r")
	prs = []
	for line in fd.readlines():
		words = line.strip().split()
		prs.append([words[1], words[2], float(words[4]), float(words[5])])
	fd.close()

	alpha_betas = {}
	for f in [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
		alpha_betas[f] = set()

		for record in prs:
			if record[2] >= f and record[3] >= f:
				alpha_betas[f].add((record[0], record[1]))

	return alpha_betas


def find_optimal_abs(rawdir, result_prefix):
	'''INTERFACE: Identify the optimal set of (alpha, beta) tuples.

	Args:
		rawdir: Directory containing optimal_b_s.txt files.
		result_prefix: Prefix to the results file to be written.
	'''
	docs = 91

	for t in [33, 72]:
		alpha_betas = []
		output = ""

		for i in range(0, docs):
			alpha_betas.append(find_good_abs(rawdir + "/optimal_" + str(i) \
													+ "_" + str(t) + ".txt"))

		for f in [0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]:
			ab_freqs = {}

			for i in range(0, docs):
				for ab in alpha_betas[i][f]:
					if ab in ab_freqs:
						ab_freqs[ab] += 1
					else:
						ab_freqs[ab] = 1

			output += str(f) + " " + str(ab_freqs) + "\n"

		fd = open(result_prefix + "_" + str(t) + ".txt", "w")
		fd.write(output)
		fd.flush()
		fd.close()


def area(x_values, y_values):
	'''INTERNAL: To calculate the area under a curve.

	Args:
		x_values: List of x-coordinates.
		y_values: List of y-coordinates.

	Return:
		A real number indicating the area under the plot of x Vs y.
	'''
	area = 0

	for i in range(1, len(x_values)):
		area += (0.5 * (x_values[i] - x_values[i-1]) * \
					(y_values[i] + y_values[i-1]))

	return area


def find_good_thresholds(pr_file, alpha_betas):
	'''INTERNAL: Find the set of thresholds in a precision-recall file for which
	both precision and recall are at least min_val (0.6), for the given set of
	(alpha, beta) tuples.

	Args:
		pr_file: File with model, alpha, beta, threshold, precision, recall
		records.
		alpha_betas: Set of (alpha, beta) tuples.

	Return:
		thresholds: Dictionary of good thresholds and their respective
		(precision, recall) tuples for each (alpha, beta) tuples in alpha_betas.
	'''
	min_val = 0.6
	fd = open(pr_file, "r")
	thresholds = {}

	for line in fd.readlines():
		words = line.strip().split()
		precision = float(words[4])
		recall = float(words[5])

		for (alpha, beta) in alpha_betas:
			if words[1] == alpha and words[2] == beta and precision >= min_val \
				and recall >= min_val:
				if (alpha, beta) not in thresholds:
					thresholds[(alpha, beta)] = {}

				thresholds[(alpha, beta)][float(words[3])] = (precision, recall)

	fd.close()
	return thresholds


def find_optimal_thresholds(rawdir, file_suffix, alpha_betas):
	'''INTERFACE: Find the optimal thresholds for the given set of (alpha, beta)
	tuples for the given model.

	Args:
		rawdir: Directory containing optimal_b_s.txt files.
		file_suffix: Suffix of the optimal_b_s.txt files which'ld be considered.
		alpha_betas: Set of (alpha, beta) tuples.
	'''
	good_thresholds = []
	optimals = {}

	for ab in alpha_betas:
		optimals[ab] = {}

	for filename in os.listdir(rawdir):
		if not filename.endswith(file_suffix):
			continue

		good_ts = find_good_thresholds(rawdir + "/" + filename, \
															alpha_betas)
		for ab in good_ts:
			for t in good_ts[ab]:
				if t not in optimals[ab]:
					optimals[ab][t] = {"limits": (0.6, 0.65, 0.7, 0.75, 0.8, \
										0.85, 0.9, 0.95),"bases": [0, 0, 0, 0, \
										0, 0, 0, 0]}

		good_thresholds.append(good_ts)

	for good_ts in good_thresholds:
		for ab in good_ts:
			for t in optimals[ab]:
				if t in good_ts[ab]:
					(precision, recall) = good_ts[ab][t]

					for i in range(0, len(optimals[ab][t]["limits"])):
						if precision >= optimals[ab][t]["limits"][i] \
							and recall >= optimals[ab][t]["limits"][i]:
							optimals[ab][t]["bases"][i] += 1
				else:
					smaller_ts = []

					for t2 in good_ts[ab]:
						if t2 <= t:
							smaller_ts.append(t2)

					if len(smaller_ts) > 0:
						(precision, recall) = good_ts[ab][max(smaller_ts)]

						for i in range(0, len(optimals[ab][t]["limits"])):
							if precision >= optimals[ab][t]["limits"][i] \
								and recall >= optimals[ab][t]["limits"][i]:
								optimals[ab][t]["bases"][i] += 1

	for ab in optimals:
		for t in optimals[ab]:
			optimals[ab][t]["area"] = area(optimals[ab][t]["limits"], \
												optimals[ab][t]["bases"])

		max_area = max([optimals[ab][t]["area"] for t in optimals[ab]])
		for t in optimals[ab]:
			if optimals[ab][t]["area"] >= max_area:
				print ab[0], ab[1], t, optimals[ab][t]


def f_measure(precision, recall):
	beta = 1
	return precision*recall / ((beta*beta*precision) + recall)


def threshold_f_measures(pr_file, alpha_betas):
	'''INTERNAL: Find the set of thresholds in a precision-recall file for the
	given set of (alpha, beta) tuples, and their respective F-measures.

	Args:
		pr_file: File with model, alpha, beta, threshold, precision, recall
		records.
		alpha_betas: Set of (alpha, beta) tuples.

	Return:
		thresholds: Dictionary of thresholds and their respective F-measures for
		each (alpha, beta) tuples in alpha_betas.
	'''
	fd = open(pr_file, "r")
	thresholds = {}

	for line in fd.readlines():
		words = line.strip().split()
		precision = float(words[4])
		recall = float(words[5])

		for (alpha, beta) in alpha_betas:
			if words[1] == alpha and words[2] == beta:
				if (alpha, beta) not in thresholds:
					thresholds[(alpha, beta)] = {}

				thresholds[(alpha, beta)][float(words[3])] = \
													f_measure(precision, recall)

	fd.close()
	return thresholds


def summarize_optimal_params(optimal_file, rawdir):
	'''INTERFACE: Final round of identifying optimal parameters. Based on area
	under the curve of "limit Vs base".

	Args:
		optimal_file: File containing precision and recall limits and a
		stringified dictionary of parameters (tuples) and their corresponding
		number of base trials. e.g. "results/optimal/p_exp_33.txt"
		rawdir: Directory containing optimal_b_s.txt files.

	Return:
		summary: A multi-level dictionary of parameters and their corresponding
		limits, bases and areas.
	'''
	fd = open(optimal_file, "r")
	summary = {}

	for line in fd.readlines():
		words = line.strip().split()
		limit = float(words[0])
		params_dict = ast.literal_eval(" ".join(words[1:]))

		for param in params_dict:
			if param in summary:
				summary[param]["limits"].append(limit)
				summary[param]["bases"].append(params_dict[param])
			else:
				summary[param] = {"limits": [limit], \
												"bases": [params_dict[param]]}

	fd.close()

	for param in summary:
		summary[param]["area"] = area(summary[param]["limits"], \
														summary[param]["bases"])

	optimal = {"area": max([summary[param]["area"] for param in summary])}
	alpha_betas = set()

	for param in summary:
		if summary[param]["area"] >= optimal["area"]:
			limits = tuple(summary[param]["limits"])
			bases = tuple(summary[param]["bases"])
			lb = tuple([limits, bases])
			alpha_betas.add(param)

			if lb in optimal:
				optimal[lb].append(param)
			else:
				optimal[lb] = [param]

	# find_optimal_thresholds(rawdir, optimal_file.split("_")[-1], alpha_betas)
	# return optimal
	return alpha_betas


def summarize_all_optimal_params(optimal_dir):
	'''INTERFACE:

	Args:
		optimal_dir: Directory containing outputs of find_optimal_abs.
	'''
	summaries = {}

	for optimal_file in os.listdir(optimal_dir):
		summaries[optimal_file.strip(".txt")] = \
					summarize_optimal_params(optimal_dir + "/" + optimal_file)

	for model in summaries:
		output = model + "\t" + str(summaries[model]["area"])
		for key in summaries[model]:
			if key != "area":
				output += "\t" + str(key[1])
		print output


def find_optimal_params(optimal_abs_file, rawdir, file_suffix):
	alpha_betas = summarize_optimal_params(optimal_abs_file, rawdir)
	all_f_measures = []
	optimals = {}

	for ab in alpha_betas:
		optimals[ab] = {}

	for filename in os.listdir(rawdir):
		if not filename.endswith(file_suffix):
			continue

		f_measures = threshold_f_measures(rawdir + "/" + filename, alpha_betas)
		all_f_measures.append(f_measures)

		for ab in f_measures:
			for t in f_measures[ab]:
				if t not in optimals[ab]:
					optimals[ab][t] = 0

	for f_measures in all_f_measures:
		for ab in f_measures:
			for t in optimals[ab]:
				if t in f_measures[ab]:
					optimals[ab][t] += f_measures[ab][t]
				else:
					smaller_ts = []

					for t2 in f_measures[ab]:
						if t2 <= t:
							smaller_ts.append(t2)

					if len(smaller_ts) > 0:
						optimals[ab][t] += f_measures[ab][max(smaller_ts)]

	for ab in optimals:
		max_f_measure = max(optimals[ab].values())
		max_ts = []

		for t in optimals[ab]:
			if optimals[ab][t] >= max_f_measure:
				max_ts.append(t)

		print ab, max_ts, max_f_measure

# churn(sys.argv[1], sys.argv[2])
# plot_churn(sys.argv[2])
# all_ads(sys.argv[1])
# unique_ads(sys.argv[1], sys.argv[2] + "/uniques.txt")
# compare_accounts(sys.argv[1], sys.argv[2])
# plot_comparison(sys.argv[1])
# analyze_comparison(sys.argv[1])
# analyze_comparisons(sys.argv[1])
# analyze_areas(sys.argv[1])
# plot_pr(sys.argv[1])
# compute_prs(sys.argv[1])
# show_verifications(sys.argv[1])
# dump_all_ads(sys.argv[1], sys.argv[2])
# find_optimal_abs(sys.argv[1], sys.argv[2])
# find_optimal_thresholds(sys.argv[1])
# summarize_optimal_params(sys.argv[1], sys.argv[2])
# summarize_all_optimal_params(sys.argv[1])
# find_optimal_params(sys.argv[1], sys.argv[2], sys.argv[3])
'''
dirname = "results/dumped_ads/analyzed"
for filename in os.listdir(dirname):
	if "_33.txt" in filename:
		# compute_prs(dirname + "/" + filename)
		show_verifications(dirname + "/" + filename)
'''
