#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 7th November, 2012
Purpose: A library of functions to analyze Gmail ads including derived class of
HTLMParser to parse Gmail ads.
NOTE: An ad is a frozen set of words in the ad and the corresponding URL. An
ad_set is a set of ads.
'''

from HTMLParser import HTMLParser
import magic, os, re, string, urllib


def clean_data(url, text):
	# Remove Google's ad metadata.
	url = re.sub(r'.*\&adurl=', "", url)
	# Remove extra redirection nonsense.
	if "/redir.php" in url:
		url = re.sub(r'.*url.*http', "http", url)

	''' Replace all punctuation and special characters with whitespace. Include
	the URL in the ad, because frozen set can't be a dict. '''
	text = re.sub(r'[^\w\s]', " ", text.lower()) + " adwiser_url=" + urllib.unquote(url).lower()

	return frozenset(text.split())


NO_READ = 0
READ = 1
CHECK_READ = 2
class AdParser(HTMLParser):

	read = NO_READ
	ad_url = ""
	ad_text = ""
	ad_set = set()


	def init_set(self):
		self.read = NO_READ
		self.ad_url = ""
		self.ad_text = ""
		self.ad_set = set()


	def handle_starttag(self, tag, attrs):
		if self.read == NO_READ:
			for attr in attrs:
				if attr[0] == "href" and "pagead2" in attr[-1]:
					self.read = READ
					self.ad_url = attrs[-1][1]
					self.ad_text = ""
		if self.read == READ and "div" in tag:
			self.read = CHECK_READ


	def handle_data(self, data):
		if self.read == CHECK_READ and ("512" in data or "128" in data):
			self.read = NO_READ
			self.ad_set.add(clean_data(self.ad_url, self.ad_text))
			self.ad_text = ""
			self.ad_url = ""
		if self.read != NO_READ:
			self.ad_text += " " + data


	def get_set(self):
		return self.ad_set


# Parse HTML to get ads in it.
def parse_html(html_file):
	fd = open(html_file, "r")
	parser = AdParser()
	parser.init_set()
	parser.feed(fd.read())
	fd.close()
	return parser.get_set()


# Parse a set of HTMLs to get union of ads in them.
def parse_html_set(html_set):
	ad_set = set()

	for html_file in html_set:
		if os.path.isfile(html_file) and "text/html" in magic.from_file(html_file, mime=True):
			ad_set |= parse_html(html_file)

	return ad_set


# Return union of a list of ad_sets.
def union(ad_sets):
	ad_union = set()

	for ad_set in ad_sets:
		ad_union |= ad_set

	return ad_union


# Compare 2 ads, i.e., 2 frozen sets and return True if they are "similar".
def compare_ads(ad1, ad2):
	# Equality is too strict.
	if ad1 == ad2:
		return True

	# Jaccard index isn't as useful as expected.
	# jaccard = len(ad1 & ad2) / float(len(ad1 | ad2))

	ad1_chars = 0
	ad2_chars = 0
	common_words_chars = 0

	for w1 in ad1:
		if "adwiser_url=" in w1:
			ad1_url = w1
		else:
			ad1_chars += len(w1)
		for w2 in ad2:
			if w1 == w2:
				common_words_chars += len(w1)
				break

	for w2 in ad2:
		if "adwiser_url=" in w2:
			ad2_url = w2
		else:
			ad2_chars += len(w2)

	if ad1_url == ad2_url:
		return True

	''' Count of common words is misleading. We want as much "content" as
	possible to match. One long common word is worth more than N puny common
	words. This still has limitations. '''
	threshold = 0.5
	if (common_words_chars / float(ad1_chars)) > threshold or (common_words_chars / float(ad2_chars)) > threshold:
		return True

	return False


''' Return intersection of two ad_sets. This isn't a strict set intersection. If
2 ads are "similar" we consider them as being "equal". '''
def intersection2(ad_set1, ad_set2):
	common_ads = set()

	for ad1 in ad_set1:
		for ad2 in ad_set2:
			if compare_ads(ad1, ad2):
				common_ads.add(ad1)
				break

	return common_ads


''' Return intersection of a list of ad_sets. This isn't a strict set
intersection. If 2 ads are "similar" we consider them as being "equal". '''
def intersection(ad_sets):
	if len(ad_sets) == 0:
		return set()

	ad_intersection = ad_sets[0]

	for i in range(1,len(ad_sets)):
		ad_intersection = intersection2(ad_intersection, ad_sets[i])

	return ad_intersection


''' Return difference between two ad_sets. This isn't a strict set difference.
If 2 ads are "similar" we consider them as being "equal". '''
def difference(ad_set1, ad_set2):
	return ad_set1 - intersection2(ad_set1, ad_set2)
