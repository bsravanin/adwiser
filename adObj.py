#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 12th November, 2012
Purpose: An object type for Ads and its related operations.
'''

from adGlobals import *
import re, sys, urllib


def is_url(word):
	'''Check whether a string is a URL.'''
	if re.search("\.com|\.edu|\.gov|\.net|\.org", word) \
		or re.search("\.[a-z]+[\.\/]", word):
		return True
	else:
		return False


def clean_url(url):
	'''To strip URL of unnecessary data. Includes removing Google's ad metadata,
	removing extra redirection nonsense, removing prepending protocol substring,
	converting it into a readable lowercase format.'''
	url = re.sub(r'.*\&adurl=', "", url)

	if "/redir.php" in url:
		url = re.sub(r'.+redir\.php.+http', "http", url)

	prev_url = ""
	while url != prev_url:
		prev_url = url
		url = urllib.unquote(url)

	return re.sub(r'http[s]?://|www\.|\?.*', "", url).lower().strip("/")


class AdObj(dict):
	'''An ad is an extended dictionary corresponding to equal/similar Google Ads
	containing the displayed URLs, googlead URLs, texts.'''

	def __init__(self, url, text):
		self.ad_urls = [clean_url(url)]

		ad_words = []
		displayed_urls = set()
		for word in text.split():
			if is_url(word):
				displayed_urls.add(clean_url(word))
			else:
				ad_words.append(word)

		self.displayed_urls = list(displayed_urls)
		text = " ".join(ad_words).decode("ascii", "ignore").encode("ascii")
		self.texts = [text.replace(" - - ", " ").lower()]


	def display(self, debug=False):
		display_str = "=====AD STARTS====="
		display_str += "\nAdURL: " + "\nAdURL: ".join(self.ad_urls)
		display_str += "\nURL: " + "\nURL: ".join(self.displayed_urls)
		display_str += "\nText: " + "\nText: ".join(self.texts)
		display_str += "\n                   =====AD ENDS====="

		if debug:
			print >> sys.stderr, display_str
		else:
			print display_str


	def compare(self, ad):
		'''Compare this ad object with another to see whether they are equal,
		similar, or otherwise.'''
		if self.__dict__ == ad.__dict__:
			return EQUAL

		if len(set(self.ad_urls) & set(ad.ad_urls)) > 0 \
			or len(set(self.displayed_urls) & set(ad.displayed_urls)) > 0 \
			or len(set(self.texts) & set(ad.texts)) > 0:
			return SIMILAR

		# Jacard Index, Many words match, many long words match, etc.
		return UNEQUAL


	def merge(self, ad):
		'''Merge another ad object into this ad.'''
		self.ad_urls = list(set(self.ad_urls) | set(ad.ad_urls))
		self.displayed_urls = list(set(self.displayed_urls) \
								| set(ad.displayed_urls))
		self.texts = list(set(self.texts) | set(ad.texts))
