#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th December, 2012
Purpose: To try out different heuristics to predict which Ds the ads are being
targeted on.
'''

from adObj import AdObj
import os


AD_TRUTH = "dbs/adTruth.db"
ACCOUNT_TRUTH = "dbs/accountTruth.db"


def true_ds_of_accounts():
	'''Return a dictionary of Account truth: for each account, its Ds.'''
	fd = open(ACCOUNT_TRUTH, "r")
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


def true_accounts_of_ds():
	'''Return a dictionary of D truth: for each D, its accounts.'''
	account_truth = true_ds_of_accounts()
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


def true_ds_of_ads():
	'''Return a dictionary of Ad truth: for each ad, its Ds.'''
	fd = open(AD_TRUTH, "r")
	ad_truth_ds = {}

	for line in fd.readlines():
		if not line.startswith("#"):
			words = line.strip().split("\t")

			if len(words) > 1:
				ad_truth_ds[words[0]] = frozenset(words[1:])

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


def true_ds_of_ad(ad, ad_truth_ds):
	'''Find the true Ds of an ad, given the Ad truth.'''
	true_ds = set()

	for url in set(ad.ad_urls) & set(ad_truth_ds):
		true_ds |= ad_truth_ds[url]

	return true_ds


def true_ds_of_ad_list(ad_list, ad_truth_ds):
	'''Find the true Ds of an ad list, given the Ad truth.'''
	true_ds_of_ads = []

	for ad in ad_list:
		true_ds_of_ads.append(true_ds_of_ad(ad, ad_truth_ds))

	return true_ds_of_ads


def predict(ds, ds_truth):
	'''Predict the most probably targeted Ds for an ad based on a dict of
	Ds, their corresponding accounts and their counts.'''
	if len(ds.keys()) == len(ds_truth.keys()):
		ds["prediction"] = set()
		ds["prediction_confidence"] = 1
		return ds

	max_ds = set()

	for d in ds:
		ds[d]["confidence"] = ds[d]["accounts"] / float(len(ds_truth[d]))

	max_confidence = max(ds[d]["confidence"] for d in ds)

	for d in ds:
		if ds[d]["confidence"] == max_confidence:
			max_ds.add(d)

	ds["prediction"] = max_ds
	ds["confidence"] = max_confidence
	return ds


def predict2(ds, ds_truth, ad_accounts, alpha, beta):
	'''Predict the most probably targeted Ds for an ad based on a dict of
	Ds, their corresponding accounts and their counts.'''
	if len(ds.keys()) == len(ds_truth.keys()):
		ds["prediction"] = set()
		ds["prediction_confidence"] = 1
		return ds

	max_ds = set()

	for d in ds:
		ds[d]["confidence"] = (alpha * ds[d]["accounts"] / float(len(ds_truth[d]))) + \
			(beta * (1 - ((ad_accounts - ds[d]["accounts"]) / float(len(ds_truth["ALL"]) - len(ds_truth[d])))))

	return ds


def ds_of_ad(ad, account_truth, ds_truth):
	'''Find the Ds, their frequencies, and confidence levels of being targeted
	by an ad, based on the account truth.'''
	ds = {}

	for account in ad.accounts:
		for d in account_truth[account]:
			if d in ds:
				ds[d]["accounts"] += 1
				ds[d]["count"] += ad.accounts[account]
			else:
				ds[d] = {"accounts":1, "count":ad.accounts[account]}

	# return predict(ds, ds_truth)
	return predict2(ds, ds_truth, len(ad.accounts), 1, 0.5)


def ds_of_ad_list(ad_list, account_truth, ds_truth):
	'''Find the Ds, their frequencies, and confidence levels of being targeted
	by an ad for all ads in a list, based on the account truth.'''
	ds_of_ads = []

	for ad in ad_list:
		ds_of_ads.append(ds_of_ad(ad, account_truth, ds_truth))

	return ds_of_ads


def compute_stats(result):
	'''Given a dict containing TPs, FPs, TNs, FNs, compute basic statistics
	about them.'''
	result["accuracy"] = 0
	result["precision"] = 0
	result["recall"] = 0
	result["tnr"] = 0

	if (result["tps"] + result["fps"] + result["tns"] + result["fns"]) > 0:
		result["accuracy"] = (result["tps"] + result["tns"]) / \
			float(result["tps"] + result["fps"] + result["tns"] + result["fns"])

	if (result["tps"] + result["fps"]) > 0:
		result["precision"] = result["tps"] / float(result["tps"] + result["fps"])

	if (result["tps"] + result["fns"]) > 0:
		result["recall"] = result["tps"] / float(result["tps"] + result["fns"])

	if (result["tns"] + result["fps"]) > 0:
		result["tnr"] = result["tns"] / float(result["tns"] + result["fps"])

	return result
