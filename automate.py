#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th January, 2013
Purpose: Automate Gmail navigation using Selenium.
'''


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
import datetime, os, subprocess, sys, time


if len(sys.argv) > 3:
	accounts_file = sys.argv[1]
	log_root = sys.argv[2]
	trials = int(sys.argv[3])
else:
	print "Usage: python", sys.argv[0], "<accounts_file> <log_root> <trials>"
	sys.exit(0)


try:
	browser = webdriver.Firefox()
except:
	print "Could not open Selenium WebDriver for Firefox."
	sys.exit(-1)

ts = datetime.datetime
wait = ui.WebDriverWait(browser, 10)
LOAD_TIME = 5
prev_url = ""
opened = 0


def get_dirname(dirname, username):
	'''Create a dirname based on username and timestamp to save the trial.

	Args:
		dirname: Root directory under which trial has to be saved.
		username: Username directory which the trial belongs to.

	Returns:
		String which is a directory path.
	'''
	timestamp = ts.today()
	return dirname + "/" + username + "/" + str(timestamp.year) + "-" \
			+ str(timestamp.month) + "-" + str(timestamp.day) + "_" \
			+ str(timestamp.hour) + "-" + str(timestamp.minute) + "-" \
			+ str(timestamp.second)


def save_page(dirname, filename):
	'''Save the displayed Gmail page as a HTML file.

	Args:
		dirname: Path to trial directory.
		filename: Filename where the page needs to be saved.
	'''
	filepath = dirname + "/" + filename
	fd = open(filepath, "w")
	fd.write(browser.page_source.encode("utf-8"))
	fd.flush()
	fd.close()


def login(username, password, save_dir):
	'''Log into a Gmail account and save the inbox page.

	Args:
		username: Username of Gmail account.
		password: Password of Gmail account.
		save_dir: Path to the trial directory.
	'''
	global prev_url
	browser.get("https://mail.google.com")
	wait.until(lambda browser: browser.find_element_by_id("signIn"))
	browser.find_element_by_id("Email").send_keys(username)
	passwd_id = browser.find_element_by_id("Passwd")
	passwd_id.send_keys(password)
	passwd_id.submit()
	
	# if "AccountRecoveryOptionsPrompt" in browser.current_url.encode("utf-8"):
		# save_id = wait.until(lambda browser: browser.find_element_by_id("save"))
		# save_id.submit()

	wait.until(lambda browser: browser.find_element_by_xpath("//div[@title='Older']"))
	save_page(save_dir, "inbox.html")
	prev_url = browser.current_url.encode("utf-8")


def verify_click():
	'''Verify whether click loaded a new page.

	Returns:
		True or False
	'''
	global prev_url
	global opened
	curr_url = browser.current_url.encode("utf-8")
	if prev_url == curr_url:
		print "Opened", opened, "URLs. No more emails to open."
		return False
	else:
		opened += 1
		prev_url = curr_url
		return True


def open_email(save_dir):
	'''Open first email.

	Args:
		save_dir: Path to the trial directory.

	Returns:
		True or False
	'''
	try:
		browser.find_element_by_xpath("//div[@title='Older']").send_keys("o")
	except:
		print "Couldn't find element. Skipping."
		return False

	time.sleep(LOAD_TIME)
	if verify_click():
		save_page(save_dir, "email1.html")
		return True
	else:
		return False


def navigate(save_dir):
	'''Navigate emails.

	Args:
		save_dir: Path to the trial directory.
	'''
	i = 2
	while True:
		try:
			if "ccloudauditor/" in save_dir \
				or "ccloudauditor2/" in save_dir \
				or "ccloudauditor6/" in save_dir \
				or "ccloudauditor7/" in save_dir \
				or "ccloudauditor8/" in save_dir \
				or "ccloudauditor13/" in save_dir:
				browser.find_element_by_xpath("//div[@aria-label='Older']").click()
			else:
				browser.find_element_by_xpath("//div[@aria-label='Older Conversation']").click()
		except:
			print "Couldn't find element. Skipping."
			break

		time.sleep(LOAD_TIME)
		if verify_click():
			filename = "email" + str(i) + ".html"
			save_page(save_dir, filename)
			i += 1
		else:
			break


def logout():
	'''Log out of the Gmail account and delete all cookies.'''
	browser.get("https://mail.google.com/mail/?logout&hl=en&hlor")
	time.sleep(LOAD_TIME)
	browser.delete_all_cookies()


def get_accounts(filename):
	'''Read account usernames and passwords into a dict.

	Args:
		filename: File with Gmail usernames and passwords.

	Returns:
		accounts: Dictionary of Gmail usernames and passwords.
	'''
	accounts = {}
	fd = open(filename, "r")
	for line in fd.readlines():
		[username, password] = line.strip().split()
		accounts[username] = password
	fd.close()
	return accounts


def run_trials(accounts, trials):
	'''Run a bunch of trials on every account.

	Args:
		accounts: Dictionary of Gmail usernames and passwords.
		trials: Number of trials to run.
	'''
	global opened
	global prev_url
	for i in range(trials):
		for username in sorted(accounts.iterkeys()):
			opened = 0
			print ts.today(), "Trial", i, "for", username

			save_dir = get_dirname(log_root, username)
			if not os.path.exists(save_dir):
				os.makedirs(save_dir)

			prev_url = ""
			login(username, accounts[username], save_dir)
			if open_email(save_dir):
				navigate(save_dir)
			logout()


accounts = get_accounts(accounts_file)
run_trials(accounts, trials)
