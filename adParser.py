#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 2nd December, 2012
Purpose: A library of functions to analyze Gmail ads including derived class of
HTLMParser to parse Gmail ads.
'''

from adObj import AdObj
from HTMLParser import HTMLParser
import adOps
import magic, os


NO_READ = 0
READ = 1
CHECK_READ = 2
AD_TRUTH = "dbs/adTruth.db"
ACCOUNT_TRUTH = "dbs/accountTruth.db"


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
		if self.read == CHECK_READ and ("512" in data or "128" in data):
			self.read = NO_READ
			ad = AdObj(self.ad_url, self.ad_text, self.username)
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


def parse_account_truth():
	'''Return a dictionary of Account truth: for each d_i, its accounts.'''
	fd = open(ACCOUNT_TRUTH, "r")
	all_accounts = set()
	account_truth = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			all_accounts.add(words[0])

			for d_i in words[1:]:
				if d_i in account_truth:
					account_truth[d_i].add(words[0])
				else:
					account_truth[d_i] = set([words[0]])

	fd.close()
	account_truth["ALL"] = all_accounts
	return account_truth


def parse_ad_truth():
	'''Return a dictionary of Ad truth: for each ad, its accounts.'''
	account_truth = parse_account_truth()

	fd = open(AD_TRUTH, "r")
	ad_truth = {"ALL":account_truth["ALL"]}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			ad_truth[words[0]] = set()

			if len(words) > 1:
				for d_i in words[1:]:
					ad_truth[words[0]] |= account_truth[d_i]

	fd.close()
	return ad_truth
