#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 29th December, 2012
Purpose: A library of functions to analyze Gmail ads including derived class of
HTLMParser to parse Gmail ads.
'''

from adObj import AdObj
from HTMLParser import HTMLParser
import adOps
import magic, os, re, sys


NO_READ = 0
READ = 1
CHECK_READ = 2


class AdParser(HTMLParser):
	'''A HTMLParser sub-class to parse Ads in Gmail content.'''

	read = NO_READ
	ad_url = ""
	ad_text = ""
	ad_list = []
	username = ""
	tag = ""

	def init_parser(self):
		self.read = NO_READ
		self.ad_url = ""
		self.ad_text = ""
		self.ad_list = []


	def handle_starttag(self, tag, attrs):
		if self.username == "":
			self.tag = tag
		if self.read == NO_READ:
			for attr in attrs:
				if attr[0] == "href" and "pagead2" in attr[1]:
					self.read = READ
					self.ad_url = attr[1]
					self.ad_text = ""
					break
		if self.read == READ and "div" in tag:
			self.read = CHECK_READ


	def handle_data(self, data):
		if self.username == "" and self.tag == "title":
			self.username = data.split(" - ")[1]
		if self.read == CHECK_READ and re.match(r'\d*$', data):
			self.read = NO_READ
			ad = AdObj(self.ad_url, self.ad_text, self.username)
			# print >> sys.stderr, ad.get_ad_str()	# DEBUG AD COMPARING
			self.ad_list = adOps.include(self.ad_list, ad)
			self.ad_text = ""
			self.ad_url = ""
		if self.read != NO_READ:
			self.ad_text += " " + data


	def get_ads(self):
		return self.ad_list


def parse_html(html_file):
	'''Parse HTML to get ads in it.'''
	fd = open(html_file, "r")
	parser = AdParser()
	parser.init_parser()
	parser.feed(fd.read())
	fd.close()
	return parser.get_ads()


def parse_html_set(html_set):
	'''Parse a set of HTMLs to get union of ads in them.'''
	ad_list = []

	for html_file in html_set:
		if os.path.isfile(html_file) \
			and "text/html" in magic.from_file(html_file, mime=True):
			ad_list.append(parse_html(html_file))

	return adOps.union(ad_list)


def parse_conf(filename):
	'''Read the config file containing a new-line separated list of usernames
	and trial roots, and return a dictionary of users and their list of trial
	filesets. The files are expected to be Gmail HTML files.'''
	fd = open(filename, "r")
	file_set_lists = {}

	for line in fd.readlines():
		if not line.startswith("#") and line != "\n":
			words = line.strip().split()
			user = words.pop(0)

			if user not in file_set_lists:
				file_set_lists[user] = []

			for root_dir in words:
				if not root_dir.startswith("/"):
					root_dir = os.path.join(os.getcwd(), root_dir)
	
				if not os.path.isdir(root_dir):
					print "ERROR:", root_dir, "is not a trial root directory."
					continue

				for dirname in os.listdir(root_dir):
					dirname = os.path.join(root_dir, dirname)

					if not os.path.isdir(dirname):
						print "ERROR:", dirname, "is not a trial directory."
						continue

					file_set = set()

					for filename in os.listdir(dirname):
						file_set.add(os.path.join(dirname, filename))

					file_set_lists[user].append(file_set)

	fd.close()
	return file_set_lists
