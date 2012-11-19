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


def get_accounts(filename):
	'''Read account usernames and passwords into a dict.'''
	accounts = {}
	fd = open(filename, "r")
	while line in fd.readlines():
		[username, password] = line.strip().split()
		accounts[username] = password
	fd.close()
	return accounts


def get_filename(dirname, username):
	timestamp = datetime.datetime.today()
	return dirname + "/" + account[username] + "/" + timestamp.year + "-" \
	+ timestamp.month + "-" + timestamp.date + "_" + timestamp.hour + "-" \
	+ timestamp.minute + "-" + timestamp.second


def run_trials(accounts, trials):
	for i in range(trials):
		for account in accounts:
			print "Trial", i, "for", accounts[username]
			save_file = get_filename(save_dir, account[username])
			subprocess.call(["python", "automate.py", account[username], \
							account[password], save_file])


accounts = get_accounts(accounts_file)
run_trials(accounts, trials)
