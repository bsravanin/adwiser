#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 13th November, 2012
Purpose: To find relevance and irrelevance of Ds. The core operation is
"intersection \ union". The sets can be either files or directories.
'''

import adOps, adParser, os, sys

if len(sys.argv) > 1:
	adset_file = sys.argv[1]
	DEBUG = 0

	if len(sys.argv) > 2:
		DEBUG = 1
else:
	print "Usage: python", sys.argv[0], "<adset_file> [DEBUG]"
	sys.exit(0)


def parse_line(line):
	'''Parse a line in the configuration file for HTML files.'''
	file_set = set()
	words = line.split("\t")
	words.pop(0)

	for word in words:
		if not word.startswith("/"):
			word = os.getcwd() + "/" + word

		if os.path.isfile(word):
			file_set.add(word)
		elif os.path.isdir(word):
			for root, dirnames, filenames in os.walk(word):
				for filename in filenames:
					file_set.add(os.path.join(root, filename))

	return file_set


def parse_html_sets(html_sets):
	'''Parse a list of HTML sets into a list of ad_lists.'''
	ad_lists = []

	for html_set in html_sets:
		ad_lists.append(adParser.parse_html_set(html_set))

	return ad_lists


def analyze_html_sets(html_sets, tag):
	'''Find union and intersection of ad_lists in html_sets.'''
	ad_lists = parse_html_sets(html_sets)
	union = adOps.union(ad_lists)
	intersection = adOps.intersection(ad_lists)
	print "Union of", tag, ":", adOps.count(union)
	print "Intersection of", tag, ":", adOps.count(intersection)
	return union, intersection


def save_to_file(filename, ads):
	fd = open(filename, "w")
	fd.write(adOps.get_ads_str(ads))
	fd.flush()
	fd.close()


ayes_html_sets = []
noes_html_sets = []

'''All files and directories in a line with Y/N are treated as one ad_list. Each
Y/N line is treated as an "account". Y and N don't have a specific meaning about
presence or absence of D_is. They are just labels to identify 2 different types
of sets. All other lines are comments.'''
afd = open(adset_file, "r")
for line in afd.readlines():
	if line.startswith("Y"):
		ayes_html_sets.append(parse_line(line.strip()))
	elif line.startswith("N"):
		noes_html_sets.append(parse_line(line.strip()))
afd.close()


(ayes_uni, ayes_int) = analyze_html_sets(ayes_html_sets, "Ys")
(noes_uni, noes_int) = analyze_html_sets(noes_html_sets, "Ns")

rel = adOps.difference(ayes_int, noes_uni)
irr = adOps.difference(noes_int, ayes_uni)

print "In Ys, but not Ns:", adOps.count(rel)
print "In Ns, but not Ys:", adOps.count(irr)

if DEBUG:
	save_to_file("ayes_uni.txt", ayes_uni)
	save_to_file("ayes_int.txt", ayes_int)
	save_to_file("noes_uni.txt", noes_uni)
	save_to_file("noes_int.txt", noes_int)
	save_to_file("rel.txt", rel)
	save_to_file("irr.txt", irr)
