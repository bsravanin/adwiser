#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 18th November, 2012
Purpose: Automate Gmail navigation using Selenium.
TODO: How to tell whether a page, including advertisements, loaded fully?
'''


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
import os, sys, time

if len(sys.argv) > 3:
	username = sys.argv[1]
	password = sys.argv[2]
	save_dir = sys.argv[3]
else:
	print "Usage: python", sys.argv[0], "<username> <password> <save_dir>"
	sys.exit(0)


try:
	browser = webdriver.Firefox()
except WebDriverException:
	time.sleep(10)
	browser = webdriver.Firefox()

wait = ui.WebDriverWait(browser, 10)
LOAD_TIME = 5
prev_url = ""
opened = 0

if not os.path.exists(save_dir):
	os.makedirs(save_dir)


# Save page.
def save_page(filename):
	filepath = save_dir + "/" + filename
	fd = open(filepath, "w")
	fd.write(browser.page_source.encode("utf-8"))
	fd.flush()
	fd.close()


# Login.
def login(username, password):
	global prev_url
	browser.get("https://mail.google.com")
	wait.until(lambda browser: browser.find_element_by_id("signIn"))
	browser.find_element_by_id("Email").send_keys(username)
	passwd_id = browser.find_element_by_id("Passwd")
	passwd_id.send_keys(password)
	passwd_id.submit()
	wait.until(lambda browser: browser.find_element_by_xpath("//div[@title='Older']"))
	save_page("inbox.html")
	prev_url = browser.current_url.encode("utf-8")


# Verify whether click loaded a new page.
def verify_click():
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


# Open first email.
def open_email():
	browser.find_element_by_xpath("//div[@title='Older']").send_keys("o")
	time.sleep(LOAD_TIME)
	if verify_click():
		save_page("email1.html")
		return True
	else:
		return False


# Navigate emails.
def navigate():
	i = 2
	while True:
		browser.find_element_by_xpath("//div[@aria-label='Older Conversation']").click()
		time.sleep(LOAD_TIME)
		if verify_click():
			filename = "email" + str(i) + ".html"
			save_page(filename)
			i += 1
		else:
			break


# Logout.
def logout():
	browser.get("https://mail.google.com/mail/?logout&hl=en&hlor")
	time.sleep(LOAD_TIME)


# Quit.
def quit():
	browser.close()
	browser.delete_all_cookies()
	browser.quit()
	os.system("rm -rf /tmp/tmp*")


login(username, password)
if open_email():
	navigate()
logout()
quit()
