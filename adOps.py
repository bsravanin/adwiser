#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th January, 2013
Purpose: A library to do operations on collections (lists) of ads.
'''


from adObj import AdObj


def get_ads_str(ads):
	'''To print all ads in a collection of ads.

	Args:
		ads: Collection of ads, which could be an ad or a list of ads or a
		list of lists of ads or ...

	Returns:
		ads_str: String.
	'''
	ads_str = ""
	if type(ads) == AdObj:
		return ads.get_ad_str()
	elif type(ads) == list:
		for ad in ads:
			ads_str += get_ads_str(ad)
	return ads_str


def count(ads):
	'''To count the number of ads in a collection.

	Args:
		ads: Collection of ads, which could be an ad or a list of ads or a
		list of lists of ads or ...

	Returns:
		total: Whole number.
	'''
	total = 0
	if type(ads) == AdObj:
		return 1
	elif type(ads) == list:
		for ad in ads:
			total += count(ad)
	return total


def include(ad_list, ad):
	'''Add ad to ad_list, if possible by merging into a similar ad.

	Args:
		ad_list: List of ad objects.
		ad: Ad object.

	Returns:
		ad_list: List of ad objects.
	'''
	for i in range(0, len(ad_list)):
		if ad_list[i].compare(ad):
			ad_list[i].merge(ad)
			return ad_list

	ad_list.append(ad)
	return ad_list


def exclude(ad_list, ad):
	'''Remove ad or a similar ad from ad_list if possible.

	Args:
		ad_list: List of ad objects.
		ad: Ad object.

	Returns:
		ad_list: List of ad objects.
	'''
	for i in range(0, len(ad_list)):
		if ad_list[i].compare(ad):
			ad_list.pop(i)
			break

	return ad_list


def union(ad_lists):
	'''Return union of lists of ads.

	Args:
		ad_lists: List of lists of ad objects.

	Returns:
		ad_union: List of ad objects.
	'''
	ad_union = []

	for ad_list in ad_lists:
		for ad in ad_list:
			ad_union = include(ad_union, ad)

	return ad_union


def intersection2(ad_list1, ad_list2):
	'''Return intersection of two ad_lists. This isn't a strict set
	intersection. If 2 ads are "similar" we include their merge.

	Args:
		ad_list1: List of ad objects.
		ad_list2: List of ad objects.

	Returns:
		ad_int: List of ad objects.
	'''
	ad_int = []

	for ad1 in ad_list1:
		for ad2 in ad_list2:
			if ad1.compare(ad2):
				ad1.merge(ad2)
				ad_int = include(ad_int, ad1)

	return ad_int


def intersection(ad_lists):
	'''Return intersection of a list of ad_lists. This isn't a strict set
	intersection. If 2 ads are "similar" we merge them.

	Args:
		ad_lists: List of lists of ad objects.

	Returns:
		ad_int: List of ad objects.
	'''
	if len(ad_lists) == 0:
		return []

	ad_int = ad_lists[0]

	for i in range(1, len(ad_lists)):
		ad_int = intersection2(ad_int, ad_lists[i])

	return ad_int


def difference(ad_list1, ad_list2):
	'''Return difference between two ad_lists. This isn't a strict set
	difference. If 2 ads are "similar" we consider them as being "equal".

	Args:
		ad_list1: List of ad objects.
		ad_list2: List of ad objects.

	Returns:
		ad_diff: List of ad objects.
	'''
	ad_diff = ad_list1

	for ad in ad_list2:
		ad_diff = exclude(ad_diff, ad)

	return ad_diff


def belongs_to(ad, ad_list):
	'''Return True if ad belongs to ad_list.

	Args:
		ad: Ad object.
		ad_list: List of ad objects.

	Returns:
		True or False
	'''
	for a in ad_list:
		if ad.compare(a):
			return True

	return False
