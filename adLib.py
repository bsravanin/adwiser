#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 9th January, 2013
Purpose: A library of miscellaneous functions.
'''


import os
import adOps
from adObj import AdObj


def true_ds_of_accounts(account_truth_db):
	'''Return a dictionary of Account truth: for each account, its Ds.

	Args:
		account_truth_db: File with account truth, e.g. "dbs/accountTruth.db".

	Returns:
		account_truth: Dictionary with accounts as keys and set of Ds as values.
	'''
	fd = open(account_truth_db, "r")
	all_ds = set()
	account_truth = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			account_truth[words[0]] = frozenset(words[1:])
			all_ds |= account_truth[words[0]]

	fd.close()
	account_truth["ALL"] = frozenset(all_ds)
	return account_truth


def true_accounts_of_ds(account_truth):
	'''Return a dictionary of D truth: for each D, its accounts.

	Args:
		account_truth: Dictionary with accounts as keys and set of Ds as values.

	Returns:
		ds_truth: Dictionary with Ds as keys and set of accounts as values.
	'''
	ds_truth = {"ALL":set()}

	for account in account_truth:
		if account == "ALL":
			continue

		ds_truth["ALL"].add(account)

		for d in account_truth[account]:
			if d in ds_truth:
				ds_truth[d].add(account)
			else:
				ds_truth[d] = set([account])

	return ds_truth


def true_ds_of_ads(ad_truth_db):
	'''Return a dictionary of Ad truth: for each ad, whether it is a D/R/X and
	if D, its set of Ds.

	Args:
		ad_truth_db: File with ad truth, e.g. "dbs/adTruth.db".

	Returns:
		ad_truth_ds: Multi-level dictionary with AdURLs as keys, and types
		and set of Ds as values.
	'''
	fd = open(ad_truth_db, "r")
	ad_truth_ds = {}

	for line in fd.readlines():
		if line.startswith("#"):
			continue

		words = line.strip().split("\t")
		ad_url = words[0]
		ad_type = words[1]
		ad_truth_ds[ad_url] = {"type": ad_type, "d_s": frozenset()}

		if ad_type == "D":
			ad_truth_ds[ad_url]["d_s"] = frozenset(words[2:])

	fd.close()
	return ad_truth_ds


def ad_types_count(ad_list, ad_truth):
	'''Count the number of targeted and untargeted ads in ad_list based on the
	ad_truth dict.

	Args:
		ad_list: List of ad objects.
		ad_truth: Two-level dictionary with AdURLs as keys, types as D/R/X and
		d_s as the (possibly empty) set of Ds.
	
	Return:
		type_counts: Dictionary with T and U as keys and counts as values.
	'''
	type_counts = {"D": 0, "R": 0, "X": 0}

	for ad in ad_list:
		url = ad.ad_urls[0]
		type_counts[ad_truth[url]["type"]] += 1

	return type_counts


def dump_ads(ad_list, filename):
	'''Dump all ads in the ad_list into a file.

	Args:
		ad_list: A collection of ad objects (object or list or list of lists or
		...)
		filename: File where the string format of ads needs to be dumped.
	'''
	fd = open(filename, "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()


def float_range(start, end, step):
	'''A function similar to the regular range function in Python that supports
	floating point steps.
	
	Args:
		start: Floating-point number.
		end: Floating-point number.

	Returns:
		step: Floating-point number.
	'''
	values = []

	while start <= end:
		values.append(start)
		start += step

	return values


def create_ad(ad_dict):
	'''Create an ad object from a dict.

	Args:
		ad_dict: Dictionary with keys and values that could be attributes and
		values of an ad object.

	Returns:
		ad_obj: Ad object.
	'''
	ad_obj = AdObj(ad_dict["ad_urls"][0], ad_dict["texts"][0], ad_dict["accounts"][0][0])

	for (account, count) in ad_dict["accounts"]:
		ad_obj.accounts[account] = int(count)
	ad_obj.ad_urls = ad_dict["ad_urls"]
	ad_obj.texts = ad_dict["texts"]
	ad_obj.displayed_urls = ad_dict["urls"]
	
	return ad_obj


def load_ads(filename):
	'''Read filename containing ads into ad_list.

	Args:
		filename: File containing list of ads dumped in their string format.

	Returns:
		ad_list: List of ad objects.
	'''
	ad_list = []
	ad = {"accounts": [], "ad_urls": [], "urls": [], "texts": []}

	fd = open(filename, "r")
	for line in fd.readlines():
		if "=====AD STARTS=====" in line:
			pass
		elif "=====AD ENDS=====" in line:
			ad_list.append(create_ad(ad))
			ad = {"accounts": [], "ad_urls": [], "urls": [], "texts": []}
		else:
			if line.startswith("Account:"):
				words = line.strip().split()
				ad["accounts"].append((words[1], words[3]))
			elif line.startswith("AdURL:"):
				ad["ad_urls"].append(line.lstrip("AdURL:").strip())
			elif line.startswith("URL:"):
				ad["urls"].append(line.lstrip("URL:").strip())
			elif line.startswith("Text:"):
				ad["texts"].append(line.lstrip("Text:").strip())

	fd.close()
	return ad_list
