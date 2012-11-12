#! /usr/bin/python
#  Name: Sravan Bhamidipati
#  Date: 6th November, 2012
#  Purpose: To do set operations on ads in different directories.
#  The core operation is "intersection \ union".
#  The sets can be either files or directories.


import adOps, adParser, os, sys

if len(sys.argv) > 1:
	adset_file = sys.argv[1]
	DEBUG = 0

	if len(sys.argv) > 2:
		DEBUG = 1
else:
	print "Usage: python", sys.argv[0], "<adset_file> [DEBUG]"
	sys.exit(0)


# Parse a line in the configuration file for HTML files.
def parse_line(line):
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


# Parse a list of HTML sets into a list of ad_sets.
def parse_html_sets(html_sets):
	ad_sets = []

	for html_set in html_sets:
		ad_sets.append(adParser.parse_html_set(html_set))

	return ad_sets


ayes_html_sets = []
noes_html_sets = []

''' All files and directories in a line are treated as one ad_set. Lines
starting with Y imply the presence of a D_i in the corresponding HTMLs. Lines
starting with N imply the absence of a D_i in the corresponding HTMLs. All other
lines are treated as comments. '''
afd = open(adset_file, "r")
for line in afd.readlines():
	if line.startswith("Y"):
		ayes_html_sets.append(parse_line(line.strip()))
	elif line.startswith("N"):
		noes_html_sets.append(parse_line(line.strip()))
afd.close()


ayes_ad_sets = parse_html_sets(ayes_html_sets)
noes_ad_sets = parse_html_sets(noes_html_sets)

'''
ayes_uni = adOps.union(ayes_ad_sets)
ayes_int = adOps.intersection(ayes_ad_sets)
noes_uni = adOps.union(noes_ad_sets)
noes_int = adOps.intersection(noes_ad_sets)

rel = adOps.difference(ayes_int, noes_uni)
irr = adOps.difference(noes_int, ayes_uni)

print "Union of Ys", len(ayes_uni)
print "Intersection of Ys", len(ayes_int)
print "Union of Ns", len(noes_uni)
print "Intersection of Ns", len(noes_int)
print "In Ys, but not Ns", len(rel)
print "In Ns, but not Ys", len(irr)

if DEBUG:
	print "Relevance:", rel
	print "Irrelevance:", irr

print "ayes_uni", ayes_uni
print "ayes_int", ayes_int
print "noes_uni", noes_uni
print "noes_int", noes_int
'''
