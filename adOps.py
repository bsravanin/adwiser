#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 12th November, 2012
Purpose: A library to do operations on sets (lists) of ads.
'''

from adGlobals import *
from adObj import AdObj


def include(ad_list, ad):
	'''Add ad to ad_list, if possible by merging into a similar ad.'''
	for i in range(0, len(ad_list)):
		comparison = ad_list[i].compare(ad)

		if comparison == EQUAL:
			return ad_list
		elif comparison == SIMILAR:
			ad_list[i] = ad_list[i].merge(ad)
			return ad_list

	ad_list.append(ad)
	return ad_list


def exclude(ad_list, ad):
	'''Remove ad or a similar ad from ad_list if possible.'''
	for i in range(0, len(ad_list)):
		comparison = ad_list[i].compare(ad)

		if comparison == EQUAL or comparison == SIMILAR:
			ad_list.pop(i)
			break

	return ad_list


def union(ad_lists):
	'''Return union of lists of ads.'''
	ad_union = []

	for ad_list in ad_lists:
		for ad in ad_list:
			ad_union = include(ad_union, ad)

	return ad_union


def intersection2(ad_list1, ad_list2):
	'''Return intersection of two ad_lists. This isn't a strict set
	intersection. If 2 ads are "similar" we include their merge.'''
	ad_int = []

	for ad1 in ad_list1:
		for ad2 in ad_list2:
			comparison = ad1.compare(ad2)
			if comparison == EQUAL:
				ad_int = include(ad_int, ad1)
			elif comparison == SIMILAR:
				ad_int = include(ad_int, ad1.merge(ad2))

	return ad_int


''' Return intersection of a list of ad_lists. This isn't a strict set
intersection. If 2 ads are "similar" we consider them as being "equal". '''
def intersection(ad_lists):
	if len(ad_lists) == 0:
		return []

	ad_int = ad_lists[0]

	for i in range(1,len(ad_lists)):
		ad_int = intersection2(ad_int, ad_lists[i])

	return ad_int


def difference(ad_list1, ad_list2):
	'''Return difference between two ad_lists. This isn't a strict set
	difference. If 2 ads are "similar" we consider them as being "equal".'''
	ad_diff = ad_list1

	for ad in ad_list2:
		ad_diff = exclude(ad_diff, ad)

	return ad_diff
