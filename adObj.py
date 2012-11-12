#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 12th November, 2012
Purpose: An object type for Ads and its related operations.
'''

from adGlobals import *
import pprint, re, urllib


def is_url(word):
	'''Check whether a string is a URL.'''
	if re.search("\.com|\.edu|\.gov|\.net|\.org", word) or re.search("\.[a-z]+[\.\/]", word):
		return True
	else:
		return False


class AdObj(dict):
	'''An ad is an extended dictionary corresponding to equal/similar Google Ads
	containing the displayed URLs, googlead URLs, texts.'''

	def __init__(self, url, text):
		self.ad_urls = []
		self.displayed_urls = []
		self.texts = []

		''' From the URL remove Google's ad metadata, extra redirection
		nonsense, and convert it into a readable lowercase format. '''
		url = re.sub(r'.*\&adurl=', "", url)
		if "/redir.php" in url:
			url = re.sub(r'.*url.*http', "http", url)
		self.ad_urls.append(urllib.unquote(url).lower())

		ad_words = []
		for word in text.split():
			if is_url(word):
				self.displayed_urls.append(word.lower())
			else:
				ad_words.append(word.lower())

		self.texts.append(" ".join(ad_words).replace(" - - ", " "))


	def display(self):
		print "=====AD STARTS====="
		for text in self.texts:
			print "Text:", text
		for url in self.displayed_urls:
			print "URL:", url
		for url in self.ad_urls:
			print "Ad URL:", url
		print "=====AD ENDS====="


	def compare(self, ad):
		'''Compare this ad object with another to see whether they are equal,
		similar, or otherwise.'''
		if self.__dict__ == ad.__dict__:
			return EQUAL

		for url1 in self.ad_urls:
			for url2 in ad.ad_urls:
				if url1 == url2:
					return SIMILAR

		for url1 in self.displayed_urls:
			for url2 in ad.displayed_urls:
				if url1 == url2:
					return SIMILAR

		# Jacard Index, Many words match, many long words match, etc.
		return UNEQUAL


	def merge(self, ad):
		'''Merge another ad object into this ad.'''
		for au in ad.ad_urls:
			if au not in self.ad_urls:
				self.ad_urls.append(au)

		for du in ad.displayed_urls:
			if du not in self.displayed_urls:
				self.displayed_urls.append(du)

		for t in ad.texts:
			if t not in self.texts:
				self.texts.append(t)
