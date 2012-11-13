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


# Parse a list of HTML sets into a list of ad_lists.
def parse_html_sets(html_sets):
	ad_lists = []

	for html_set in html_sets:
		ad_lists.append(adParser.parse_html_set(html_set))

	return ad_lists


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


ayes_ad_lists = parse_html_sets(ayes_html_sets)
noes_ad_lists = parse_html_sets(noes_html_sets)


ayes_uni = adOps.union(ayes_ad_lists)
adOps.display_ads(ayes_uni)
sys.exit(0)
ayes_int = adOps.intersection(ayes_ad_lists)
noes_uni = adOps.union(noes_ad_lists)
noes_int = adOps.intersection(noes_ad_lists)

rel = adOps.difference(ayes_int, noes_uni)
irr = adOps.difference(noes_int, ayes_uni)

print "Union of Ys", adOps.count(ayes_uni)
print "Intersection of Ys", adOps.count(ayes_int)
print "Union of Ns", adOps.count(noes_uni)
print "Intersection of Ns", adOps.count(noes_int)
print "In Ys, but not Ns", adOps.count(rel)
print "In Ns, but not Ys", adOps.count(irr)

if DEBUG:
	print "\nRELEVANCE"
	adOps.display_ads(rel)
	print "\nIRRELEVANCE"
	adOps.display_ads(irr)
