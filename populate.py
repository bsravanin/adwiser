#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 18th November, 2012
Purpose: To populate a Gmail account with some of the emails in the mailbox.
'''


import os, re, subprocess, sys, time

if len(sys.argv) == 3:
	gmail_id = sys.argv[1] + "@gmail.com"
	thread = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<GmailID> <all|threadID|-threadID>"
	print "\tall: Populate account with all threads."
	print "\tthreadID: Populate account with just the threadID."
	print "\t-threadID: Populate account with all but threadID."
	sys.exit(-1)


# Stupid natural sort. Ref: http://stackoverflow.com/a/4836734
def natural_sort(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)


def send_thread(tid):
	mail_dir = "mailbox/" + tid

	fd = open(mail_dir + "/subject", "r")
	subject = fd.read().strip()
	fd.close()

	command=["mail.mailutils", "-a", '"Content-type: text/html;"', "-s", subject, "-t", gmail_id]

	for mail in natural_sort(os.listdir(mail_dir)):
		if mail != "subject":
			md = open(mail_dir + "/" + mail, "r")
			subprocess.call(command, stdin = md)
			md.close()
			time.sleep(1)


def send_threads(tids):
	for tid in tids:
		send_thread(tid)


my_threads = natural_sort(os.listdir("mailbox"))

if thread == "all":
	pass
elif thread in my_threads:
	my_threads = [thread]
elif str(int(thread)*-1) in my_threads:
	my_threads.remove(str(int(thread)*-1))
else:
	print "Thread", int(thread)*-1, "not in mailbox."
	sys.exit(-1)

send_threads(my_threads)
