#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 19th November, 2012
Purpose: Wrapper around automate.py to run mutiple trials for all accounts.
'''

import datetime, subprocess, sys

if len(sys.argv) > 3:
	accounts_file = sys.argv[1]
	save_dir = sys.argv[2]
	trials = int(sys.argv[3])
else:
	print "python", sys.argv[0], "<accounts_file> <save_dir> <trials>"
	sys.exit(-1)


ts = datetime.datetime


def get_accounts(filename):
	'''Read account usernames and passwords into a dict.'''
	accounts = {}
	fd = open(filename, "r")
	for line in fd.readlines():
		[username, password] = line.strip().split()
		accounts[username] = password
	fd.close()
	return accounts


def get_filename(dirname, username):
	'''Create a filename based on username and timestamp to save the trial.'''
	timestamp = ts.today()
	return dirname + "/" + username + "/" + str(timestamp.year) + "-" \
	+ str(timestamp.month) + "-" + str(timestamp.date) + "_" \
	+ str(timestamp.hour) + "-" + str(timestamp.minute) + "-" \
	+ str(timestamp.second)


def run_trials(accounts, trials):
	'''Run a bunch of trials on every account.'''
	for i in range(trials):
		for username in sorted(accounts.iterkeys()):
			print ts.today(), "Trial", i, "for", username
			save_file = get_filename(save_dir, username)
			subprocess.call(["python", "automate.py", username, \
							accounts[username], save_file])


accounts = get_accounts(accounts_file)
run_trials(accounts, trials)
