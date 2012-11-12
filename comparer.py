#! /usr/bin/python
#  Name: Sravan Bhamidipati
#  Date: 6th November, 2012
#  Purpose: To compare GMail ads between two sets of HTMLs.
#  The sets can be either files or directories.


from adParser import AdParser
import os, pylab, sys, time

if len(sys.argv) > 3:
	base_set = sys.argv[1]
	test_set = sys.argv[2]
	image = sys.argv[3]
	DEBUG = 0

	if len(sys.argv) > 4:
		DEBUG = int(sys.argv[4])
else:
	print "Usage: python", sys.argv[0], "<base_htmls> <test_htmls> <image> [DEBUG]"
	sys.exit(0)

parser = AdParser()
trials = []
total_ads = []
overlaps =[]

if DEBUG > 0:
	print "Trial\tBase\tTest\tCommon\t%Common"


# Print an ad_set for debugging.
def print_ad_set(ad_set):
	if DEBUG < 2:
		return

	ads = []
	for ad in ad_set:
		ad_list = list(ad)
		ad_list.sort()
		ads.append(" ".join(ad_list))
	ads.sort()
	print "=== AD SET START ==="
	for ad in ads:
		print ad
	print "=== AD SET END ==="


def is_html(html_file):
	if html_file.endswith(".html"):
		return True
	else:
		return False


def parse_html(html_file):
	fd = open(html_file, "r")
	parser.init_set()
	parser.feed(fd.read())
	fd.close()
	return parser.get_set()


def parse_html_set(html_set):
	count = 0
	ad_set = set()

	if os.path.isfile(html_set):
		if is_html(html_set):
			count += 1
			ad_set |= parse_html(html_set)
	elif os.path.isdir(html_set):
		for html_file in os.listdir(html_set):
			if is_html(html_file):
				count += 1
				ad_set |= parse_html(html_set + "/" + html_file)
	else:
		print html_set, "is neither a file nor a directory."

	print_ad_set(ad_set)
	return [count, ad_set]


# Compare 2 ads, i.e., 2 frozen sets and return True if they are "similar".
def compare_ads(ad1, ad2):
	# Equality is too strict.
	if ad1 == ad2:
		return True

	# Jaccard index isn't as useful as expected.
	# jaccard = len(ad1 & ad2) / float(len(ad1 | ad2))

	ad1_chars = 0
	ad2_chars = 0
	common_words_chars = 0

	for w1 in ad1:
		if "adwiser_url=" in w1:
			ad1_url = w1
		else:
			ad1_chars += len(w1)
		for w2 in ad2:
			if w1 == w2:
				common_words_chars += len(w1)
				break

	for w2 in ad2:
		if "adwiser_url=" in w2:
			ad2_url = w2
		else:
			ad2_chars += len(w2)

	if ad1_url == ad2_url:
		return True

	# Count of common words is misleading. We want as much "content" as possible
	# to match. One long common word is worth more than N puny common words.
	# This still has limitations.
	threshold = 0.5
	if (common_words_chars / float(ad1_chars)) > threshold or (common_words_chars / float(ad2_chars)) > threshold:
		if DEBUG > 1:
			print "Treating these 2 ads as equal:"
			print " ".join(sorted(list(ad1)))
			print " ".join(sorted(list(ad2)))
		return True

	return False


# Compare 2 ad_sets. Each ad_set is a set of frozen sets.
def compare_ad_sets(trial, ad_set1, ad_set2):
	common_ads = set()

	for ad1 in ad_set1:
		for ad2 in ad_set2:
			if compare_ads(ad1, ad2):
				common_ads.add(ad1)
				break

	if len(ad_set1) > 0:
		common = len(common_ads) * 100.0 / len(ad_set1)
	else:
		common = 0

	if DEBUG > 0:
		print trial, "\t", len(ad_set1), "\t", len(ad_set2), "\t", len(common_ads), "\t", common

	trials.append(trial)
	total_ads.append(len(ad_set2))
	overlaps.append(common)


# Compare the base ad_set and test ad_set cumulatively.
def compare_html_set_cumulative(base_set, test_set):
	[base_count, base_ad_set] = parse_html_set(base_set)
	test_count = 0
	test_ad_set = set()

	if os.path.isfile(test_set):
		if is_html(test_set):
			test_count += 1
			test_ad_set |= parse_html(test_set)
			print_ad_set(test_ad_set)
			compare_ad_sets(test_count, base_ad_set, test_ad_set)
	elif os.path.isdir(test_set):
		for html_file in sorted(os.listdir(test_set)):
			if is_html(html_file):
				test_count += 1
				test_ad_set |= parse_html(test_set + "/" + html_file)
				print_ad_set(test_ad_set)
				compare_ad_sets(test_count, base_ad_set, test_ad_set)
	else:
		print test_ad_set, "is neither a file nor a directory."


# Cumulative plot of total ads and overlap percentage seen after each trial.
def plot_overlaps():
	pylab.xlabel("Trial")
	pylab.plot(trials, total_ads, "bo-")
	pylab.plot(trials, overlaps, "go-")
	pylab.legend(("TotalAds", "Overlap%"))
	pylab.savefig(image)


compare_html_set_cumulative(base_set, test_set)
plot_overlaps()
