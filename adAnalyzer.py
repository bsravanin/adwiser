#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 17th December, 2012
Purpose: To try out different heuristics to predict which Ds the ads are being
targeted on.
'''

from adObj import AdObj
import os


AD_TRUTH = "dbs/adTruth.db"
ACCOUNT_TRUTH = "dbs/accountTruth.db"
MODELS = ["aggregation", "exponentiation", "weighted_aggregation", \
			"weighted_exponentiation"]

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


def calculate_scores(ad_d_dict, alphas, betas):
	'''Compute confidence scores for an ad for different values of alpha and
	beta when using:
	aggregation = (alpha*tps) + ((1-alpha)*fps) + (beta*tns) + ((1-beta)*fns)
	exponentiation = (alpha**tps) * ((1-alpha)**fps) * (beta**tns) * ((1-beta)**fns)
	'''
	scores = {}

	for key in MODELS:
		scores[key] = {}

	for alpha in alphas:
		for key in scores:
			scores[key][alpha] = {}

		for beta in betas:
			scores["aggregation"][alpha][beta] = \
					(alpha*ad_d_dict["tps"]) + ((1-alpha)*ad_d_dict["fps"]) + \
					(beta*ad_d_dict["tns"]) + ((1-beta)*ad_d_dict["fns"])
			scores["exponentiation"][alpha][beta] = \
					(alpha**ad_d_dict["tps"]) * ((1-alpha)**ad_d_dict["fps"]) *\
					(beta**ad_d_dict["tns"]) * ((1-beta)**ad_d_dict["fns"])
			scores["weighted_aggregation"][alpha][beta] = \
					(alpha*ad_d_dict["weighted_tps"]) + \
					((1-alpha)*ad_d_dict["weighted_fps"]) + \
					(beta*ad_d_dict["tns"]) + ((1-beta)*ad_d_dict["fns"])
			scores["weighted_exponentiation"][alpha][beta] = \
					(alpha**ad_d_dict["weighted_tps"]) * \
					((1-alpha)**ad_d_dict["weighted_fps"]) * \
					(beta**ad_d_dict["tns"]) * ((1-beta)**ad_d_dict["fns"])

	return scores


def max_score(ad_dict, alphas, betas):
	'''Find the Ds with various maximum scores in an ad.'''
	maxes = {}

	for key in MODELS:
		maxes[key] = {}

		for alpha in alphas:
			maxes[key][alpha] = {}

			for beta in betas:
				max_score = 0
				total_score = 0

				for d in ad_dict:
					total_score += ad_dict[d][key][alpha][beta]

					if ad_dict[d][key][alpha][beta] >= max_score:
						max_score = ad_dict[d][key][alpha][beta]

				max_ds = set()

				for d in ad_dict:
					if ad_dict[d][key][alpha][beta] == max_score:
						max_ds.add(d)

				maxes[key][alpha][beta] = {"ds": max_ds, \
										"score": max_score / float(total_score)}

	return maxes


def analyze_ad(ad, ds_truth, alphas, betas):
	'''For each D, calcuate various scores about the probability that an ad may
	be targeted on D. Based on the scores predict the most probable set of Ds'''
	ad_accounts = set(ad.accounts.keys())
	all_accounts = ds_truth["ALL"]
	ad_accounts_not = all_accounts - ad_accounts
	analysis = {}

	for d in ds_truth:
		if d == "ALL":
			continue

		analysis[d] = {"tps": 0, "weighted_tps": 0, "fps": 0, "weighted_fps": 0}

		for account in ad_accounts & ds_truth[d]:
			analysis[d]["tps"] += 1
			analysis[d]["weighted_tps"] += ad.accounts[account]

		for account in ad_accounts & (all_accounts - ds_truth[d]):
			analysis[d]["fps"] += 1
			analysis[d]["weighted_fps"] += ad.accounts[account]

		analysis[d]["fns"] = len(ad_accounts_not & ds_truth[d])
		analysis[d]["tns"] = len(ad_accounts_not & (all_accounts - ds_truth[d]))

		scores = calculate_scores(analysis[d], alphas, betas)

		for key in MODELS:
			analysis[d][key] = scores[key]

	return max_score(analysis, alphas, betas)


def analyze_ads(ad_list, ds_truth, alphas, betas):
	'''For each Ad in a list, make various predictions and calcuate confidence
	scores under various alphas and betas.'''
	analyzed_ads = []

	for ad in ad_list:
		analyzed_ads.append(analyze_ad(ad, ds_truth, alphas, betas))

	return analyzed_ads


def verify_pred(predicted_ds_of_ad, true_ds_of_ad, all_ds, threshold):
	'''Verify a particular prediction made about an ad given a threshold of
	confidence score.'''
	if predicted_ds_of_ad["score"] >= threshold:
		prediction = predicted_ds_of_ad["ds"]
	else:
		prediction = set()

	result = {}
	result["tps"] = len(prediction & true_ds_of_ad)
	result["fps"] = len(prediction & (all_ds - true_ds_of_ad))
	result["fns"] = len((all_ds - prediction) & true_ds_of_ad)
	result["tns"] = len((all_ds - prediction) & (all_ds - true_ds_of_ad))

	if len(prediction) > 0 and len(true_ds_of_ad) > 0:
		result["targeted"] = "tps"
	elif len(prediction) > 0 and len(true_ds_of_ad) == 0:
		result["targeted"] = "fps"
	elif len(prediction) == 0 and len(true_ds_of_ad) == 0:
		result["targeted"] = "tns"
	elif len(prediction) == 0 and len(true_ds_of_ad) > 0:
		result["targeted"] = "fns"
	return result


def verify_prediction(analyzed_ad, true_ds_of_ad, \
						all_ds, alphas, betas, thresholds):
	'''Verify the predictions made about an ad under various alphas, betas
	considering various thresholds for various scores.'''
	verification = {}

	for key in MODELS:
		verification[key] = {}

		for alpha in alphas:
			verification[key][alpha] = {}

			for beta in betas:
				verification[key][alpha][beta] = {}

				for threshold in thresholds:
					verification[key][alpha][beta][threshold] = \
									verify_pred(analyzed_ad[key][alpha][beta], \
										true_ds_of_ad, all_ds, threshold)

	return verification


def verify_predictions(analyzed_ads, true_ds_of_ads, \
						all_ds, alphas, betas, thresholds):
	'''Verify the predictions made about a list of ads under various alphas,
	betas considering various thresholds for various scores.'''
	verifications = []

	for i in range(0, len(analyzed_ads)):
		verifications.append(verify_prediction(analyzed_ads[i], \
						true_ds_of_ads[i], all_ds, alphas, betas, thresholds))

	return verifications


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


def aggregate_verifications(verifications, alphas, betas, thresholds):
	'''Aggregate the verifications made about a list of ads for various alphas,
	betas and thresholds.'''
	aggregates = {}

	for key in MODELS:
		aggregates[key] = {}

		for alpha in alphas:
			aggregates[key][alpha] = {}

			for beta in betas:
				aggregates[key][alpha][beta] = {}

				for threshold in thresholds:
					aggregate = {}

					for key2 in ("tps", "fps", "fns", "tns"):
						aggregate[key2] = 0
					
						for ad in verifications:
							aggregate[key2] += \
										ad[key][alpha][beta][threshold][key2]

					targeted = {"tps": 0, "fps": 0, "fns": 0, "tns": 0}

					for ad in verifications:
						key2 = ad[key][alpha][beta][threshold]["targeted"]
						targeted[key2] += 1

					aggregate["targeted"] = compute_stats(targeted)
					aggregates[key][alpha][beta][threshold] = \
													compute_stats(aggregate)

	return aggregates
