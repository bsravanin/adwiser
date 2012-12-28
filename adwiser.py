#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 27th December, 2012
Purpose: To find relevance and irrelevance of Ds.
'''

import adAnalyzer, adOps, adParser, adPlotter
import os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


def get_file_set(file_sets, trials):
	'''Get a cumulative fileset from all user filesets for the specified number
	of trials.'''
	file_set = set()

	for user in file_sets:
		for i in range(0, trials):
			max_trials = len(file_sets[user])

			if i < max_trials:
				file_set |= file_sets[user][i]
			else:
				print "WARNING:", user, "only has", max_trials, " trials."

	return file_set


def float_range(start, end, step):
	'''A function similar to the regular range function in Python.'''
	values = []

	while start <= end:
		values.append(start)
		start += step

	return values


def make_dirs(results, results_dir):
	'''Create the required directories for results.'''
	if not os.path.isdir(results_dir):
		if os.path.exists(results_dir):
			print dirname, "exists and is not a directory."
		else:
			os.makedirs(results_dir + "/targeted")
			for key in results:
				os.makedirs(results_dir + "/" + key)
				os.makedirs(results_dir + "/targeted/" + key)


def y_plots(results, plot, results_dir):
	'''Single plots against threshold values for various alphas, betas for
	all models.'''
	plot_keys = [plot]

	for key in results:
		alphas = sorted(results[key].keys())
		betas = sorted(results[key].keys())

		for alpha in alphas:
			for beta in betas:
				adPlotter.draw_plot_dict_keys(results[key][alpha][beta], \
													plot_keys, ["bo-"], [None])
				title = key + ", Alpha " + str(round(alpha, 1)) + ", Beta " + \
							str(round(beta, 1))
				imgpath = results_dir + "/" + key + "/" + plot + "-a" + \
					str(round(alpha, 1)) + "-b" + str(round(beta, 1)) + ".png"
				adPlotter.save_plot("Threshold", plot, title, imgpath)

		for alpha in alphas:
			for beta in betas:
				adPlotter.draw_plot_dict_keys(results[key][alpha][beta], \
							plot_keys, ["o-"], ["beta=" + str(round(beta, 1))])

			title = key + ", Alpha " + str(round(alpha, 1)) + ", All Betas"
			imgpath = results_dir + "/" + key + "/" + plot + "-a" + \
								str(round(alpha, 1)) + ".png"
			adPlotter.save_plot("Threshold", plot, title, imgpath)

		for beta in betas:
			for alpha in alphas:
				adPlotter.draw_plot_dict_keys(results[key][alpha][beta], \
						plot_keys, ["o-"], ["alpha=" + str(round(alpha, 1))])

			title = key + ", Beta " + str(round(beta, 1)) + ", All Alphas"
			imgpath = results_dir + "/" + key + "/" + plot + "-b" + \
								str(round(beta, 1)) + ".png"
			adPlotter.save_plot("Threshold", plot, title, imgpath)


def xy_plots(results, results_dir, plot1, plot2, alphas, betas, thresholds):
	'''x Vs y plots for various alphas, betas for all models.'''
	for key in results:
		for alpha in alphas:
			for beta in betas:
				draw_plot2(results[key][alpha][beta], thresholds, plot1, \
							plot2, "bo-")
				title = key + ", Alpha " + str(round(alpha, 1)) + ", Beta " + \
							str(round(beta, 1))
				imgpath = results_dir + "/" + key + "/" + plot1 + "-" + plot2 \
								+ "-a" + str(round(alpha, 1)) + "-b" + \
								str(round(beta, 1)) + ".png"
				save_plot(plot1, plot2, title, imgpath)

				draw_targeted_plot2(results[key][alpha][beta], thresholds, \
							plot1, plot2, "bo-")
				title = "Targeted, " + key + ", Alpha " + str(round(alpha, 1)) \
									+ ", Beta " + str(round(beta, 1))
				imgpath = results_dir + "/targeted/" + key + "/" + plot1 + "-" \
								+ plot2 + "-a" + str(round(alpha, 1)) + "-b" + \
								str(round(beta, 1)) + ".png"
				save_plot(plot1, plot2, title, imgpath)

		for alpha in alphas:
			for beta in betas:
				draw_plot2(results[key][alpha][beta], thresholds, plot1, \
							plot2, "o-")
			title = key + ", Alpha " + str(round(alpha, 1)) + ", All Betas"
			imgpath = results_dir + "/" + key + "/" + plot1 + "-" + plot2 \
								+ "-a" + str(round(alpha, 1)) + ".png"
			save_plot(plot1, plot2, title, imgpath)

			for beta in betas:
				draw_targeted_plot2(results[key][alpha][beta], thresholds, \
							plot1, plot2, "o-")
			title = "Targeted, " + key + ", Alpha " + str(round(alpha, 1)) \
									+ ", All Betas"
			imgpath = results_dir + "/targeted/" + key + "/" + plot1 + "-" + \
							plot2 + "-a" + str(round(alpha, 1)) + ".png"
			save_plot(plot1, plot2, title, imgpath)

		for beta in betas:
			for alpha in alphas:
				draw_plot2(results[key][alpha][beta], thresholds, plot1, \
							plot2, "o-")
			title = key + ", Beta " + str(round(beta, 1)) + ", All Alphas"
			imgpath = results_dir + "/" + key + "/" + plot1 + "-" + plot2 \
								+ "-b" + str(round(beta, 1)) + ".png"
			save_plot(plot1, plot2, title, imgpath)

			for alpha in alphas:
				draw_targeted_plot2(results[key][alpha][beta], thresholds, \
							plot1, plot2, "o-")
			title = "Targeted, " + key + ", Beta " + str(round(beta, 1)) \
									+ ", All Alphas"
			imgpath = results_dir + "/targeted/" + key + "/" + plot1 + "-" + \
							plot2 + "-b" + str(round(beta, 1)) + ".png"
			save_plot(plot1, plot2, title, imgpath)


def x_y_plots(results, results_dir, plot1, plot2, alphas, betas, thresholds):
	'''x plots and y plots for various alphas, betas for all models.'''
	for key in results:
		for alpha in alphas:
			for beta in betas:
				draw2_plot(results[key][alpha][beta], thresholds, plot1, \
							plot2, "bo-", "ro-")
				title = key + ", Alpha " + str(round(alpha, 1)) + ", Beta " + \
							str(round(beta, 1))
				imgpath = results_dir + "/" + key + "/" + plot1 + "&" + plot2 \
							+ "-a" + str(round(alpha, 1)) + "-b" + \
							str(round(beta, 1)) + ".png"
				save_plot(plot1, plot2, title, imgpath)


def gen_plots(results, results_dir, alphas, betas, thresholds):
	'''Draw various plots.'''
	# for plot in ("accuracy", "precision", "recall", "tnr"):
		# y_plots(results, plot, results_dir)

	# xy_plots(results, results_dir, "precision", "recall", alphas, betas, thresholds)
	# xy_plots(results, results_dir, "recall", "precision", alphas, betas, thresholds)
	# x_y_plots(results, results_dir, "precision", "recall", alphas, betas, thresholds)
	pass


def debug_logs(ad_list, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()


file_sets = adParser.parse_conf(adset_file)
'''
result_sets will be a mult-level dictionary of the following structure:
result_sets[trial][model][alpha][beta][threshold]{targeted}[metric], where
{targeted} is optional.
'''
result_sets = []

account_truth = adAnalyzer.true_ds_of_accounts()
ds_truth = adAnalyzer.true_accounts_of_ds()
ad_truth_ds = adAnalyzer.true_ds_of_ads()
# ad_truth_accounts = adAnalyzer.true_accounts_of_ads()

trials = range(1, 100)
alphas = betas = thresholds = float_range(0, 1, 0.1)

for t in [int(sys.argv[2])]:	# DEBUG AD COMPARING
# for t in trials:
	file_set = get_file_set(file_sets, t)
	ad_list = adParser.parse_html_set(file_set)
	print adOps.get_ads_str(ad_list)	# DEBUG AD COMPARING
	continue	# DEBUG AD COMPARING
	true_ds_of_ads = adAnalyzer.true_ds_of_ad_list(ad_list, ad_truth_ds)
	analyzed_ads = adAnalyzer.analyze_ads(ad_list, ds_truth, alphas, betas)
	verifications = adAnalyzer.verify_predictions(analyzed_ads, \
									true_ds_of_ads,	account_truth["ALL"])
	results = adAnalyzer.aggregate_verifications(verifications, alphas, betas, \
																	thresholds)
	result_sets.append(results)

sys.exit(0)	# DEBUG AD COMPARING
make_dirs(results, results_dir)
gen_plots(results, results_dir, alphas, betas, thresholds)
debug_logs(ad_list, results_dir)
