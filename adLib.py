#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd January, 2013
Purpose: A library of miscellaneous functions.
'''

import os
import adOps
from adObj import AdObj


def true_ds_of_accounts(account_truth_db):
	'''Return a dictionary of Account truth: for each account, its Ds.'''
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
	'''Return a dictionary of D truth: for each D, its accounts.'''
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
	'''Return a dictionary of Ad truth: for each ad, its Ds.'''
	fd = open(ad_truth_db, "r")
	ad_truth_ds = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")

			if len(words) > 1:
				ad_truth_ds[words[0]] = frozenset(words[1:])
			else:
				ad_truth_ds[words[0]] = frozenset([])

	fd.close()
	return ad_truth_ds


def true_accounts_of_ads():
	'''DEPRECATED: Return a dictionary of Ad truth: for each ad, its
	accounts.'''
	account_truth = accounts_of_ds()

	fd = open(AD_TRUTH, "r")
	ad_truth_accounts = {"ALL":account_truth["ALL"]}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")
			ad_truth_accounts[words[0]] = set()

			if len(words) > 1:
				for d in words[1:]:
					ad_truth_accounts[words[0]] |= account_truth[d]

	fd.close()
	return ad_truth_accounts


def dump_ads(ad_list, filename):
	'''Dump all ads in the ad_list into a file.'''
	fd = open(filename, "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()


def float_range(start, end, step):
	'''A function similar to the regular range function in Python that supports
	floating point steps.'''
	values = []

	while start <= end:
		values.append(start)
		start += step

	return values


def create_ad(ad_dict):
	'''Create an ad object from a dict.'''
	ad_obj = AdObj(ad_dict["ad_urls"][0], ad_dict["texts"][0], ad_dict["accounts"][0][0])

	for (account, count) in ad_dict["accounts"]:
		ad_obj.accounts[account] = int(count)
	ad_obj.ad_urls = ad_dict["ad_urls"]
	ad_obj.texts = ad_dict["texts"]
	ad_obj.displayed_urls = ad_dict["urls"]
	
	return ad_obj


def load_ads(filename):
	'''Read filename containing ads into ad_list.'''
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
