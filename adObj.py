#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th January, 2013
Purpose: An object type for Ads and its related operations.
'''


import re, sys, urllib


def is_url(word):
	'''Check whether a string is a URL.

	Args:
		word: String which may be a URL.

	Returns:
		True or False
	'''
	if re.search(r'\.com|\.edu|\.gov|\.net|\.org', word, re.IGNORECASE) \
		or re.search("\.[a-z]+[\.\/]", word, re.IGNORECASE):
		return True
	else:
		return False


def clean_url(url):
	'''To strip URL of unnecessary data. Includes removing Google's ad metadata,
	removing extra redirection nonsense, removing prepending protocol substring,
	converting it into a readable lowercase format.

	Args:
		url: URL string

	Returns:
		URL string
	'''
	url = re.sub(r'.*\&adurl=', "", url)

	if "/redir.php" in url:
		url = re.sub(r'.+redir\.php.+http', "http", url)
	else:
		url = re.sub(r'http.+http:', "http:", url)

	prev_url = ""
	while url != prev_url:
		prev_url = url
		url = urllib.unquote(url)

	return re.sub(r'http[s]?://|www\.|\?.*', "", url).lower().strip("/")


def remove_nonascii(text):
	'''To replace as Non-ASCII characters with space. Safer than
	decode("ascii", "ignore").encode("ascii") which causes spacing issues.

	Args:
		text: String

	Returns:
		ascii_text: String with only ASCII characters.
	'''
	ascii_text = ""

	for i in text:
		if ord(i) < 128:
			ascii_text += i
		else:
			ascii_text += " "

	return ascii_text


class AdObj(dict):
	'''An ad is an extended dictionary corresponding to equal/similar Google Ads
	containing the displayed URLs, googlead URLs, texts.
	
	Attributes:
		accounts: Dictionary of accounts and their counts.
		ad_urls: List of AdURLs.
		displayed_urls: List of displayed URLs.
		texts: List of displayed text.
	'''

	def __init__(self, url, text, username):
		'''Initialize an ad object.

		Args:
			url: Raw AdURL.
			text: Displayed ad content.
			username: Account in which ad was displayed.
		'''
		self.accounts = {username:1}
		self.ad_urls = [clean_url(url)]

		ad_words = []
		displayed_urls = set()

		for word in remove_nonascii(text).split():
			if is_url(word):
				displayed_urls.add(clean_url(word))
			else:
				ad_words.append(word)

		self.displayed_urls = list(displayed_urls)

		text = " ".join(ad_words).replace("  ", " ").replace(" - - ", " ")
		self.texts = [text.lower()]


	def get_ad_str(self):
		'''
		Returns:
			String representation of an ad object.
		'''
		ad_str = "=====AD STARTS====="
		for account in self.accounts:
			ad_str += "\nAccount: " + account + "\tCount: " + \
						str(self.accounts[account])
		ad_str += "\nAdURL: " + "\nAdURL: ".join(sorted(self.ad_urls))

		try:
			ad_str += "\nURL: " + "\nURL: ".join(sorted(self.displayed_urls))
		except UnicodeDecodeError:
			print "DEBUG UnicodeDecodeError", self.displayed_urls

		ad_str += "\nText: " + "\nText: ".join(sorted(self.texts))
		ad_str += "\n                   =====AD ENDS=====\n"
		return ad_str


	def compare(self, ad):
		'''Compare this ad object with another for similarity.

		Args:
			ad: Ad object.
		'''
		if len(set(self.ad_urls) & set(ad.ad_urls)) > 0 \
			or len(set(self.texts) & set(ad.texts)) > 0:
			return True

		'''
		If some displayed URLs match and those URLs are descriptive.
		displayed = set(self.displayed_urls) & set(ad.displayed_urls)

		if len(displayed) > 0:
			for url in displayed:
				if "/" in url:
					return True

		or len(set(self.displayed_urls) & set(ad.displayed_urls)) > 0 \
		Jacard Index, Many words match, many long words match, many chars match,
		etc. If there are common displayed_urls, AND ad_urls/text overlap.
		'''

		return False


	def merge(self, ad):
		'''Merge another ad object into this ad.

		Args:
			ad: Ad object.
		'''
		for account in set(ad.accounts):
			if account in self.accounts:
				self.accounts[account] += ad.accounts[account]
			else:
				self.accounts[account] = ad.accounts[account]

		self.ad_urls = list(set(self.ad_urls) | set(ad.ad_urls))
		self.displayed_urls = list(set(self.displayed_urls) |\
									set(ad.displayed_urls))
		self.texts = list(set(self.texts) | set(ad.texts))
