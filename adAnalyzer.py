#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 1st February, 2013
Purpose: To try out different heuristics to predict which Ds the ads are being
targeted on.
'''


from adObj import AdObj
from adGlobals import *
import os


def true_ds_of_ad_list(ad_list):
	'''Find the true Ds of an ad list, using the overall Ad truth.

	Args:
		ad_list: List of ad objects.

	Returns:
		true_ds_of_ads: List of set of Ds.
	'''
	true_ds_of_ads = []

	for ad in ad_list:
		true_type = ""
		true_ds = set()

		for url in set(ad.ad_urls) & set(AD_TRUTH):
			if true_type == "":
				true_type = AD_TRUTH[url]["type"]
			elif true_type != AD_TRUTH[url]["type"]:
				print "WARNING: Ad type mismatch."

			true_ds |= AD_TRUTH[url]["d_s"]

		true_ds_of_ads.append({"type": true_type, "d_s": frozenset(true_ds)})

	return true_ds_of_ads


def calculate_scores(ad_d_dict):
	'''Compute confidence scores for an ad for different values of alpha and
	beta when using:
		p_agg = - (alpha*fps) - (beta*fns)
		p_exp = (alpha**fps) * (beta**fns)
		p_r_agg = (alpha*tps) - ((1-alpha)*fps) + (beta*tns) - ((1-beta)*fns)
		p_r_agg2 = (alpha*tps) - ((1-beta)*fps) + (beta*tns) - ((1-alpha)*fns)
		p_r_exp = ((1-alpha)**fps) * ((1-beta)**fns) / ((alpha**tps) * (beta**tns))
		p_r_exp2 = ((1-beta)**fps) * ((1-alpha)**fns) / ((alpha**tps) * (beta**tns))
		p1_r1_agg = (alpha*tps) - (beta*fps)
		p1_r1_exp = (alpha**tps) * (beta**fps)
		p1_r2_agg = (alpha*tps) - (beta*fns)
		p1_r2_exp = (alpha**tps) * (beta**fns)
		p2_r1_agg = (alpha*tns) - (beta*fps)
		p2_r1_exp = (beta**fps) * (alpha**tns)
		p2_r2_agg = (alpha*tns) - (beta*fns)
		p2_r2_exp = (alpha**tns) * (beta**fns)
		r_agg = (alpha*tps) + (beta*tns)
		r_exp = 1 / ((alpha**tps) * (beta**tns))

	Args:
		ad_d_dict: Dictionary of a M(Ad) and M(D) combinations and counts.

	Returns:
		scores: Multi-level dictionary of models, alphas, betas as keys and
		corresponding confidence scores calculated for ad_d_dict.
	'''
	# TODO: Harmonic means pending. Cases where denominators are 0.
	scores = {}

	for model in MODELS:
		scores[model] = {}

	for alpha in ALPHAS:
		for model in MODELS:
			scores[model][alpha] = {}

		for beta in BETAS:
			if "p_agg" in MODELS:
				scores["p_agg"][alpha][beta] = -(alpha*ad_d_dict["fps"]) - \
													(beta*ad_d_dict["fns"])

			if "p_exp" in MODELS:
				scores["p_exp"][alpha][beta] = \
						(alpha**ad_d_dict["fps"]) * (beta**ad_d_dict["fns"])

			if "p_r_agg" in MODELS:
				scores["p_r_agg"][alpha][beta] = (alpha*ad_d_dict["tps"]) - \
						((1-alpha)*ad_d_dict["fps"]) + (beta*ad_d_dict["tns"]) \
						- ((1-beta)*ad_d_dict["fns"])

			if "p_r_agg2" in MODELS:
				scores["p_r_agg2"][alpha][beta] = (alpha*ad_d_dict["tps"]) - \
						((1-beta)*ad_d_dict["fps"]) + (beta*ad_d_dict["tns"]) \
						- ((1-alpha)*ad_d_dict["fns"])

			if "p_r_exp" in MODELS:
				scores["p_r_exp"][alpha][beta] = (alpha**ad_d_dict["tps"]) * \
														(beta**ad_d_dict["tns"])
				if scores["p_r_exp"][alpha][beta] > 0:
					scores["p_r_exp"][alpha][beta] = \
									((1-alpha)**ad_d_dict["fps"]) *	\
										((1-beta)**ad_d_dict["fns"]) / \
												scores["p_r_exp"][alpha][beta]

			if "p_r_exp2" in MODELS:
				scores["p_r_exp2"][alpha][beta] = (alpha**ad_d_dict["tps"]) * \
														(beta**ad_d_dict["tns"])
				if scores["p_r_exp2"][alpha][beta] > 0:
					scores["p_r_exp2"][alpha][beta] = \
									((1-beta)**ad_d_dict["fps"]) *	\
										((1-alpha)**ad_d_dict["fns"]) / \
												scores["p_r_exp2"][alpha][beta]

			if "p1_r1_agg" in MODELS:
				scores["p1_r1_agg"][alpha][beta] = (alpha*ad_d_dict["tps"]) - \
														(beta*ad_d_dict["fps"])

			if "p1_r1_exp" in MODELS:
				scores["p1_r1_exp"][alpha][beta] = alpha**ad_d_dict["tps"]
				if scores["p1_r1_exp"][alpha][beta] > 0:
					scores["p1_r1_exp"][alpha][beta] = beta**ad_d_dict["fps"] /\
												scores["p1_r1_exp"][alpha][beta]

			if "p1_r2_agg" in MODELS:
				scores["p1_r2_agg"][alpha][beta] = (alpha*ad_d_dict["tps"]) - \
														(beta*ad_d_dict["fns"])

			if "p1_r2_exp" in MODELS:
				scores["p1_r2_exp"][alpha][beta] = alpha**ad_d_dict["tns"]
				if scores["p1_r2_exp"][alpha][beta] > 0:
					scores["p1_r2_exp"][alpha][beta] = beta**ad_d_dict["fps"] /\
												scores["p1_r2_exp"][alpha][beta]

			if "p2_r1_agg" in MODELS:
				scores["p2_r1_agg"][alpha][beta] = (alpha*ad_d_dict["tns"]) - \
														(beta*ad_d_dict["fps"])

			if "p2_r1_exp" in MODELS:
				scores["p2_r1_exp"][alpha][beta] = alpha**ad_d_dict["tps"]
				if scores["p2_r1_exp"][alpha][beta] > 0:
					scores["p2_r1_exp"][alpha][beta] = beta**ad_d_dict["fns"] /\
												scores["p2_r1_exp"][alpha][beta]

			if "p2_r2_agg" in MODELS:
				scores["p2_r2_agg"][alpha][beta] = (alpha*ad_d_dict["tns"]) - \
														(beta*ad_d_dict["fns"])

			if "p2_r2_exp" in MODELS:
				scores["p2_r2_exp"][alpha][beta] = alpha**ad_d_dict["tns"]
				if scores["p2_r2_exp"][alpha][beta] > 0:
					scores["p2_r2_exp"][alpha][beta] = beta**ad_d_dict["fns"] /\
												scores["p2_r2_exp"][alpha][beta]

			if "r_agg" in MODELS:
				scores["r_agg"][alpha][beta] = (alpha*ad_d_dict["tps"]) + \
														(beta*ad_d_dict["tns"])

			if "r_exp" in MODELS:
				scores["r_exp"][alpha][beta] = \
						(alpha**ad_d_dict["tps"]) * (beta**ad_d_dict["tns"])
				if scores["r_exp"][alpha][beta] > 0:
					scores["r_exp"][alpha][beta] = \
												1 / scores["r_exp"][alpha][beta]

			if "wt_p_agg" in MODELS:
				scores["wt_p_agg"][alpha][beta] = -(alpha*ad_d_dict["wt_fps"]) - \
													(beta*ad_d_dict["fns"])

			if "wt_p_exp" in MODELS:
				scores["wt_p_exp"][alpha][beta] = \
						(alpha**ad_d_dict["wt_fps"]) * (beta**ad_d_dict["fns"])

			if "wt_p_r_agg" in MODELS:
				scores["wt_p_r_agg"][alpha][beta] = \
					(alpha*ad_d_dict["wt_tps"]) - \
					((1-alpha)*ad_d_dict["wt_fps"]) + (beta*ad_d_dict["tns"]) -\
					((1-beta)*ad_d_dict["fns"])

			if "wt_p_r_agg2" in MODELS:
				scores["wt_p_r_agg2"][alpha][beta] = \
					(alpha*ad_d_dict["wt_tps"]) - \
					((1-beta)*ad_d_dict["wt_fps"]) + (beta*ad_d_dict["tns"]) - \
					((1-alpha)*ad_d_dict["fns"])

			if "wt_p_r_exp" in MODELS:
				scores["wt_p_r_exp"][alpha][beta] = \
						(alpha**ad_d_dict["wt_tps"]) * (beta**ad_d_dict["tns"])
				if scores["wt_p_r_exp"][alpha][beta] > 0:
					scores["wt_p_r_exp"][alpha][beta] = \
									((1-alpha)**ad_d_dict["wt_fps"]) *	\
										((1-beta)**ad_d_dict["fns"]) / \
											scores["wt_p_r_exp"][alpha][beta]

			if "wt_p_r_exp2" in MODELS:
				scores["wt_p_r_exp2"][alpha][beta] = \
						(alpha**ad_d_dict["wt_tps"]) * (beta**ad_d_dict["tns"])
				if scores["wt_p_r_exp2"][alpha][beta] > 0:
					scores["wt_p_r_exp2"][alpha][beta] = \
									((1-beta)**ad_d_dict["wt_fps"]) *	\
										((1-alpha)**ad_d_dict["fns"]) / \
											scores["wt_p_r_exp2"][alpha][beta]

			if "wt_p1_r1_agg" in MODELS:
				scores["wt_p1_r1_agg"][alpha][beta] = \
						(alpha*ad_d_dict["wt_tps"]) - (beta*ad_d_dict["wt_fps"])

			if "wt_p1_r1_exp" in MODELS:
				scores["wt_p1_r1_exp"][alpha][beta] = alpha**ad_d_dict["wt_tps"]
				if scores["wt_p1_r1_exp"][alpha][beta] > 0:
					scores["wt_p1_r1_exp"][alpha][beta] = \
											beta**ad_d_dict["wt_fps"] / \
											scores["wt_p1_r1_exp"][alpha][beta]

			if "wt_p1_r2_agg" in MODELS:
				scores["wt_p1_r2_agg"][alpha][beta] = \
						(alpha*ad_d_dict["tns"]) - (beta*ad_d_dict["wt_fps"])

			if "wt_p1_r2_exp" in MODELS:
				scores["wt_p1_r2_exp"][alpha][beta] = alpha**ad_d_dict["tns"]
				if scores["wt_p1_r2_exp"][alpha][beta] > 0:
					scores["wt_p1_r2_exp"][alpha][beta] = \
											beta**ad_d_dict["wt_fps"] / \
											scores["wt_p1_r2_exp"][alpha][beta]

			if "wt_p2_r1_agg" in MODELS:
				scores["wt_p2_r1_agg"][alpha][beta] = \
						(alpha*ad_d_dict["wt_tps"]) - (beta*ad_d_dict["fns"])

			if "wt_p2_r1_exp" in MODELS:
				scores["wt_p2_r1_exp"][alpha][beta] = alpha**ad_d_dict["wt_tps"]
				if scores["wt_p2_r1_exp"][alpha][beta] > 0:
					scores["wt_p2_r1_exp"][alpha][beta] = \
											beta**ad_d_dict["fns"] / \
											scores["wt_p2_r1_exp"][alpha][beta]

			if "wt_p2_r2_agg" in MODELS:
				scores["wt_p2_r2_agg"][alpha][beta] = \
							(alpha*ad_d_dict["tns"]) - (beta*ad_d_dict["fns"])

			if "wt_p2_r2_exp" in MODELS:
				scores["wt_p2_r2_exp"][alpha][beta] = alpha**ad_d_dict["tns"]
				if scores["wt_p2_r2_exp"][alpha][beta] > 0:
					scores["wt_p2_r2_exp"][alpha][beta] = \
											beta**ad_d_dict["fns"] / \
											scores["wt_p2_r2_exp"][alpha][beta]

			if "wt_r_agg" in MODELS:
				scores["wt_r_agg"][alpha][beta] = \
						(alpha*ad_d_dict["wt_tps"]) + (beta*ad_d_dict["tns"])

			if "wt_r_exp" in MODELS:
				scores["wt_r_exp"][alpha][beta] = \
						(alpha**ad_d_dict["wt_tps"]) * (beta**ad_d_dict["tns"])
				if scores["wt_r_exp"][alpha][beta] > 0:
					scores["wt_r_exp"][alpha][beta] = \
											1 / scores["wt_r_exp"][alpha][beta]

	return scores


def normalize_scores(ad_dict):
	'''Normalize scores for Ds of an ad to be between 0 and 1.
	NORMALIZATION DISABLED.

	Args:
		ad_dict: Multi-level dictionary of Ds, models, alphas, betas with values
		as corresponding confidence scores.

	Returns:
		normal: Multi-level dictionary of models, alphas, betas, Ds with values
		as corresponding confidence scores normalized between 0 and 1.
	'''
	normal = {}

	for model in MODELS:
		normal[model] = {}

		for alpha in ALPHAS:
			normal[model][alpha] = {}

			for beta in BETAS:
				normal[model][alpha][beta] = {}

				for d in ad_dict:
					normal[model][alpha][beta][d] = \
												ad_dict[d][model][alpha][beta]

	return normal


def max_score(ad_dict):
	'''Find the Ds with various maximum scores in an ad.

	Args:
		ad_dict: Multi-level dictionary of Ds, models, alphas, betas with values
		as corresponding confidence scores.

	Returns:
		maxes: Multi-level dictionary of models, alphas, betas with possible
		set of max_Ds and corresponding max confidence score normalized between
		0 and 1.
	'''
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
	be targeted on D.

	Args:
		ad: Ad object.

	Returns:
		normal: Multi-level dictionary of models, alphas, betas, Ds with values
		as corresponding confidence scores normalized between 0 and 1.
	'''
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
	scores under various alphas and betas.

	Args:
		ad_list: List of ad objects.

	Returns:
		analyzed_ads: List of score dicts for corresponding ad_list.
	'''
	analyzed_ads = []

	for ad in ad_list:
		analyzed_ads.append(analyze_ad(ad))

	return analyzed_ads


def get_scores(predictions):
	'''Get all the scores for a model, alpha, beta combination so that they can
	be used as thresholds.

	Args:
		predictions: List of score dicts for corresponding ad_list.
	
	Return:
		scores: Set of scores for each model, alpha, beta combination.
	'''
	scores = {}

	for model in MODELS:
		scores[model] = {}

		for alpha in ALPHAS:
			scores[model][alpha] = {}

			for beta in BETAS:
				scores[model][alpha][beta] = set()

				for ad in predictions:
					scores[model][alpha][beta] |= \
											set(ad[model][alpha][beta].values())

	return scores


def verify_pred(predicted_ds_of_ad, true_ds_of_ad, threshold):
	'''Verify a particular prediction made about an ad given a threshold of
	confidence score.

	Args:
		predicted_ds_of_ad: Dictionary of Ds and their confidence scores.
		true_ds_of_ad: Set of Ds on which an ad is actually targeted.
		threshold: Minimum threshold of the confidence score for a prediction
		to be made.

	Returns:
		result: Dictionary of TPs, FPs, FNs and TNs.
	'''
	all_ds = ACCOUNT_TRUTH["ALL"]
	prediction = set()

	for d in predicted_ds_of_ad:
		if predicted_ds_of_ad[d] >= threshold:
			prediction.add(d)

	# print "DEBUG", len(prediction)
	'''
	# Predicting only max_confidence Ds. Needs max_score function to be used.
	if predicted_ds_of_ad["score"] >= threshold:
		prediction = predicted_ds_of_ad["ds"]
	'''

	result = {"tps": 0, "fps": 0, "fns": 0, "tns": 0}

	'''
	result["tps"] = len(prediction & true_ds_of_ad["d_s"])
	result["fps"] = len(prediction & (all_ds - true_ds_of_ad["d_s"]))
	result["fns"] = len((all_ds - prediction) & true_ds_of_ad["d_s"])
	result["tns"] = len((all_ds - prediction) & (all_ds - true_ds_of_ad["d_s"]))
	'''
	right = len(prediction & true_ds_of_ad["d_s"])
	wrong = len(prediction & (all_ds - true_ds_of_ad["d_s"]))
	missed = len((all_ds - prediction) & true_ds_of_ad["d_s"])

	if right > 0:
		result["tps"] = 1
	elif (wrong + missed) == 0:
		result["tns"] = 1
	else:
		result["fps"] = float(wrong) / (wrong + missed)
		result["fns"] = float(missed) / (wrong + missed)

	if len(prediction) > 0 and true_ds_of_ad["type"] == "D":
		result["targeted"] = "tps"
	elif len(prediction) > 0 and true_ds_of_ad["type"] != "D":
		result["targeted"] = "fps"
	elif len(prediction) == 0 and true_ds_of_ad["type"] != "D":
		result["targeted"] = "tns"
	elif len(prediction) == 0 and true_ds_of_ad["type"] == "D":
		result["targeted"] = "fns"

	return result


def verify_prediction(analyzed_ad, true_ds_of_ad, thresholds):
	'''Verify the predictions made about an ad under various alphas, betas
	considering various thresholds for various scores.

	Args:
		analyzed_ad: Multi-level dictionary of models, alphas, betas, Ds with
		values as corresponding confidence scores normalized between 0 and 1.
		true_ds_of_ad: Set of Ds on which an ad is actually targeted.

	Returns:
		verification: Multi-level dictionary of models, alphas, betas,
		thresholds, with number of TPs, FPs, FNs and TNs.
	'''
	verification = {}

	for model in analyzed_ad:
		verification[model] = {}

		for alpha in analyzed_ad[model]:
			verification[model][alpha] = {}

			for beta in analyzed_ad[model][alpha]:
				verification[model][alpha][beta] = {}

				if type(thresholds) == list:
					ths = thresholds
				else:
					ths = thresholds[model][alpha][beta]

				for threshold in ths:
					verification[model][alpha][beta][threshold] = \
								verify_pred(analyzed_ad[model][alpha][beta], \
													true_ds_of_ad, threshold)

	return verification


def verify_predictions(adwiser):
	'''Verify the predictions made about a list of ads under various alphas,
	betas considering various thresholds for various scores.

	Args:
		adwiser: Multi-level dictionary with predictions, scores (optional) and
		truth for a list of ads.

	Results:
		verifications: List of multi-level dictionaries of models, alphas,
		betas, thresholds, with number of TPs, FPs, FNs and TNs.
	'''
	verifications = []

	if "scores" in adwiser:
		for i in range(0, len(adwiser["ads"])):
			verifications.append(verify_prediction(adwiser["prediction"][i], \
										adwiser["truth"][i], adwiser["scores"]))
	else:
		for i in range(0, len(adwiser["ads"])):
			verifications.append(verify_prediction(adwiser["prediction"][i], \
											adwiser["truth"][i], THRESHOLDS))

	return verifications


def compute_stats(result):
	'''Given a dict containing TPs, FPs, TNs, FNs, compute basic statistics
	about them.

	Args:
		result: Dictionary of TPs, FPs, TNs, FNs and their counts.

	Returns:
		result: Dictionary of TPs, FPs, TNs, FNs, accuracy, precision, recall
		and TNR, and their values.
	'''
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


def aggregate_verifications(adwiser, pr=False):
	'''Aggregate the verifications made about a list of ads for various alphas,
	betas and thresholds.

	Args:
		adwiser: List of multi-level dictionaries of models, alphas, betas,
		thresholds, with number of TPs, FPs, FNs and TNs.
		pr: Boolean about whether to print precision and recall, which is used
		to determine optimal combinations of model, alpha, beta, threshold.
	
	Returns:
		aggregates: Multi-level dictionary of models, alphas, betas, thresholds
		with dictionaries of TPs, FPs, TNs, FNs, accuracy, precision, recall and
		TNR, and their values.
	'''
	aggregates = {}

	for model in MODELS:
		aggregates[model] = {}

		for alpha in ALPHAS:
			aggregates[model][alpha] = {}

			for beta in BETAS:
				aggregates[model][alpha][beta] = {}

				if "scores" in adwiser:
					thresholds = adwiser["scores"][model][alpha][beta]
				else:
					thresholds = THRESHOLDS

				for threshold in thresholds:
					aggregate = {}

					for key in ("tps", "fps", "fns", "tns"):
						aggregate[key] = 0

						for ad in adwiser["verification"]:
							aggregate[key] += \
										ad[model][alpha][beta][threshold][key]

					targeted = {"tps": 0, "fps": 0, "fns": 0, "tns": 0}

					for ad in adwiser["verification"]:
						key = ad[model][alpha][beta][threshold]["targeted"]
						targeted[key] += 1

					aggregate["targeted"] = compute_stats(targeted)
					aggregates[model][alpha][beta][threshold] = \
													compute_stats(aggregate)
					if pr:
						print model, alpha, beta, threshold, aggregate

	return aggregates
