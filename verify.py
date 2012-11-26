#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 25th November, 2012
Purpose: Verify whether a trial was okay or not.
'''

import magic, os, string, sys

if len(sys.argv) > 1:
	trial_root = sys.argv[1]
else:
	print "Usage: python", sys.argv[0], "<trial_root>"
	sys.exit(-1)


def get_trials(trial_root):
	'''Get the set of trials in trial_root.'''
	trial_set = set()

	if os.path.isdir(trial_root):
		for root, dirnames, filenames in os.walk(trial_root):
			trial_set.add(root)

	return trial_set


def verify(trial_dir):
	'''Verify whether a trial went smoothly.'''
	html_files = set()

	for filename in os.listdir(trial_dir):
		if "text/html" in magic.from_file(trial_dir + "/" + filename, mime=True):
			html_files.add(filename)

	if "inbox.html" not in html_files:
		print "FAIL: No inbox.html in", trial_dir
		return
	elif "ccloudauditor10" in trial_dir and len(html_files) < 11:
		print "FAIL: Some email*.html missing in", trial_dir
		return
	elif "ccloudauditor1" in trial_dir and len(html_files) < 10:
		print "FAIL: Some email*.html missing in", trial_dir
		return
	elif "ccloudauditor20" in trial_dir and len(html_files) < 10:
		print "FAIL: Some email*.html missing in", trial_dir
		return
	elif "ccloudauditor2" in trial_dir and len(html_files) < 2:
		print "FAIL: Some email*.html missing in", trial_dir
		return
	elif "ccloudauditor30" in trial_dir and len(html_files) < 2:
		print "FAIL: Some email*.html missing in", trial_dir
		return

	for html_file in html_files:
		html_path = trial_dir + "/" + html_file

		fd = open(html_path, "r")
		count = fd.read().count("pagead2")
		fd.close()

		if count == 0:
			print "FAIL: A HTML file has no ads in", trial_dir
			return
		elif count % 2 == 1:
			print "FAIL: A HTML file has incomplete ads in", trial_dir
			return


for trial_dir in get_trials(trial_root):
	verify(trial_dir)
