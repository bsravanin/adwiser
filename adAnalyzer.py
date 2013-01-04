#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd January, 2013
Purpose: To try out different heuristics to predict which Ds the ads are being
targeted on.
'''

from adObj import AdObj
from adGlobals import *
import os


def true_ds_of_ad_list(ad_list):
	'''Find the true Ds of an ad list, using the overall Ad truth.'''
	true_ds_of_ads = []

	for ad in ad_list:
		true_ds = set()

		for url in set(ad.ad_urls) & set(AD_TRUTH):
			true_ds |= AD_TRUTH[url]

		true_ds_of_ads.append(true_ds)

	return true_ds_of_ads


def calculate_scores(ad_d_dict):
	'''Compute confidence scores for an ad for different values of alpha and
	beta when using:
	p_agg = (1*tps) + (alpha*fps) + (1*tns) + (beta*fns)
	p_exp = (1**tps) * (alpha**fps) * (1**tns) * (beta**fns)
	p_harmonic = (2 + alpha + beta) / [(1/tps) + (alpha/fps) + (1/tns) + (beta/fns)]
	p_r_agg = (alpha*tps) + ((1-alpha)*fps) + (beta*tns) + ((1-beta)*fns)
	p_r_exp = (alpha**tps) * ((1-alpha)**fps) * (beta**tns) * ((1-beta)**fns)
	p_r_harmonic = 2 / [(alpha/tps) + ((1-alpha)/fps) + (beta/tns) + ((1-beta)/fns)]
	'''
	# TODO: Harmonic means pending. Cases where denominators are 0.
	scores = {}

	for model in MODELS:
		scores[model] = {}

	for alpha in ALPHAS:
		for model in MODELS:
			scores[model][alpha] = {}

		for beta in BETAS:
			scores["p_agg"][alpha][beta] = \
					(1*ad_d_dict["tps"]) + (alpha*ad_d_dict["fps"]) + \
					(beta*ad_d_dict["fns"]) + (1*ad_d_dict["tns"])
			scores["p_exp"][alpha][beta] = \
					(1**ad_d_dict["tps"]) * (alpha**ad_d_dict["fps"]) * \
					(beta**ad_d_dict["fns"]) * (1**ad_d_dict["tns"])
			scores["p_r_agg"][alpha][beta] = \
					(alpha*ad_d_dict["tps"]) + ((1-alpha)*ad_d_dict["fps"]) + \
					(beta*ad_d_dict["tns"]) + ((1-beta)*ad_d_dict["fns"])
			scores["p_r_exp"][alpha][beta] = \
					(alpha**ad_d_dict["tps"]) * ((1-alpha)**ad_d_dict["fps"]) *\
					(beta**ad_d_dict["tns"]) * ((1-beta)**ad_d_dict["fns"])
			scores["wt_p_agg"][alpha][beta] = \
					(1*ad_d_dict["wt_tps"]) + (alpha*ad_d_dict["wt_fps"]) + \
					(beta*ad_d_dict["fns"]) + (1*ad_d_dict["tns"])
			scores["wt_p_exp"][alpha][beta] = \
					(1**ad_d_dict["wt_tps"]) * (alpha**ad_d_dict["wt_fps"]) * \
					(beta**ad_d_dict["fns"]) * (1**ad_d_dict["tns"])
			scores["wt_p_r_agg"][alpha][beta] = \
					(alpha*ad_d_dict["wt_tps"]) + \
					((1-alpha)*ad_d_dict["wt_fps"]) + \
					(beta*ad_d_dict["tns"]) + ((1-beta)*ad_d_dict["fns"])
			scores["wt_p_r_exp"][alpha][beta] = \
					(alpha**ad_d_dict["wt_tps"]) * \
					((1-alpha)**ad_d_dict["wt_fps"]) * \
					(beta**ad_d_dict["tns"]) * ((1-beta)**ad_d_dict["fns"])

	return scores


def normalize_scores(ad_dict):
	'''Normalize scores for Ds of an ad to be between 0 and 1.'''
	normal = {}

	for model in MODELS:
		normal[model] = {}

		for alpha in ALPHAS:
			normal[model][alpha] = {}

			for beta in BETAS:
				normal[model][alpha][beta] = {}
				total = 0

				for d in ad_dict:
					total += ad_dict[d][model][alpha][beta]

				if total > 0:
					for d in ad_dict:
						normal[model][alpha][beta][d] = \
								ad_dict[d][model][alpha][beta] / float(total)
				else:
					for d in ad_dict:
						normal[model][alpha][beta][d] = -1

	return normal


def max_score(ad_dict):
	'''Find the Ds with various maximum scores in an ad.'''
	maxes = {}

	for model in MODELS:
		maxes[model] = {}

		for alpha in ALPHAS:
			maxes[model][alpha] = {}

			for beta in BETAS:
				max_score = 0
				total_score = 0

				for d in ad_dict:
					total_score += ad_dict[d][model][alpha][beta]

					if ad_dict[d][model][alpha][beta] >= max_score:
						max_score = ad_dict[d][model][alpha][beta]

				max_ds = set()

				for d in ad_dict:
					if ad_dict[d][model][alpha][beta] == max_score:
						max_ds.add(d)

				if total_score > 0:
					maxes[model][alpha][beta] = {"ds": max_ds, \
										"score": max_score / float(total_score)}
				else:
					maxes[model][alpha][beta] = {"ds": max_ds, "score": -1}

	return maxes


def analyze_ad(ad):
	'''For each D, calcuate various scores about the probability that an ad may
	be targeted on D.'''
	ad_accounts = set(ad.accounts.keys())
	all_accounts = DS_TRUTH["ALL"]
	ad_accounts_not = all_accounts - ad_accounts
	analysis = {}

	for d in DS_TRUTH:
		if d == "ALL":
			continue

		analysis[d] = {"tps": 0, "wt_tps": 0, "fps": 0, "wt_fps": 0}

		for account in ad_accounts & DS_TRUTH[d]:
			analysis[d]["tps"] += 1
			analysis[d]["wt_tps"] += ad.accounts[account]

		for account in ad_accounts & (all_accounts - DS_TRUTH[d]):
			analysis[d]["fps"] += 1
			analysis[d]["wt_fps"] += ad.accounts[account]

		analysis[d]["fns"] = len(ad_accounts_not & DS_TRUTH[d])
		analysis[d]["tns"] = len(ad_accounts_not & (all_accounts - DS_TRUTH[d]))

		analysis[d] = calculate_scores(analysis[d])

	# return max_score(analysis)
	return normalize_scores(analysis)


def analyze_ads(ad_list):
	'''For each Ad in a list, make various predictions and calcuate confidence
	scores under various alphas and betas.'''
	analyzed_ads = []

	for ad in ad_list:
		analyzed_ads.append(analyze_ad(ad))

	return analyzed_ads


def verify_pred(predicted_ds_of_ad, true_ds_of_ad, threshold):
	'''Verify a particular prediction made about an ad given a threshold of
	confidence score.'''
	all_ds = ACCOUNT_TRUTH["ALL"]
	prediction = set()

	for d in predicted_ds_of_ad:
		if predicted_ds_of_ad[d] >= threshold:
			prediction.add(d)

	'''
	# Predicting only max_confidence Ds. Needs max_score function to be used.
	if predicted_ds_of_ad["score"] >= threshold:
		prediction = predicted_ds_of_ad["ds"]
	'''

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


def verify_prediction(analyzed_ad, true_ds_of_ad):
	'''Verify the predictions made about an ad under various alphas, betas
	considering various thresholds for various scores.'''
	verification = {}

	for model in analyzed_ad:
		verification[model] = {}

		for alpha in analyzed_ad[model]:
			verification[model][alpha] = {}

			for beta in analyzed_ad[model][alpha]:
				verification[model][alpha][beta] = {}

				for threshold in THRESHOLDS:
					verification[model][alpha][beta][threshold] = \
								verify_pred(analyzed_ad[model][alpha][beta], \
													true_ds_of_ad, threshold)

	return verification


def verify_predictions(adwiser):
	'''Verify the predictions made about a list of ads under various alphas,
	betas considering various thresholds for various scores.'''
	verifications = []

	for i in range(0, len(adwiser["ads"])):
		verifications.append(verify_prediction(adwiser["prediction"][i], \
														adwiser["truth"][i]))

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


def aggregate_verifications(verifications):
	'''Aggregate the verifications made about a list of ads for various alphas,
	betas and thresholds.'''
	aggregates = {}

	for model in MODELS:
		aggregates[model] = {}

		for alpha in ALPHAS:
			aggregates[model][alpha] = {}

			for beta in BETAS:
				aggregates[model][alpha][beta] = {}

				for threshold in THRESHOLDS:
					aggregate = {}

					for key in ("tps", "fps", "fns", "tns"):
						aggregate[key] = 0
	
						for ad in verifications:
							aggregate[key] += \
										ad[model][alpha][beta][threshold][key]

					targeted = {"tps": 0, "fps": 0, "fns": 0, "tns": 0}

					for ad in verifications:
						key = ad[model][alpha][beta][threshold]["targeted"]
						targeted[key] += 1

					aggregate["targeted"] = compute_stats(targeted)
					aggregates[model][alpha][beta][threshold] = \
													compute_stats(aggregate)

	return aggregates
