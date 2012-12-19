#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 19th December, 2012
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


debug_str = ""

import datetime
ts = datetime.datetime

def parse_conf(filename):
	'''Read the config file containing a new-line separated list of files or
	directories and return the set of files. The files are expected to be Gmail
	HTML files.'''
	fd = open(filename, "r")
	file_set = set()

	for line in fd.readlines():
		if not line.startswith("#") and line != "\n":
			root_dir = line.strip()
			if not root_dir.startswith("/"):
				root_dir = os.getcwd() + "/" + root_dir
	
			if os.path.isfile(root_dir):
				file_set.add(root_dir)
			elif os.path.isdir(root_dir):
				for root, dirnames, filenames in os.walk(root_dir, followlinks=True):
					for filename in filenames:
						file_set.add(os.path.join(root, filename))

	fd.close()
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
		break


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


def debug_logs(ad_list, dirname):
	'''Save debug logs.'''
	fd = open(dirname + "/ads.txt", "w")
	fd.write(adOps.get_ads_str(ad_list))
	fd.flush()
	fd.close()

	fd = open(dirname + "/debug.txt", "w")
	fd.write(debug_str)
	fd.flush()
	fd.close()


account_truth = adAnalyzer.true_ds_of_accounts()
ds_truth = adAnalyzer.true_accounts_of_ds()
ad_truth_ds = adAnalyzer.true_ds_of_ads()
# ad_truth_accounts = adAnalyzer.true_accounts_of_ads()

alphas = float_range(0.5, 1, 0.1)
betas = float_range(0.5, 1, 0.1)
thresholds = float_range(0, 1, 0.1)

ad_list = adParser.parse_html_set(parse_conf(adset_file))
true_ds_of_ads = adAnalyzer.true_ds_of_ad_list(ad_list, ad_truth_ds)
analyzed_ads = adAnalyzer.analyze_ads(ad_list, ds_truth, alphas, betas)
verifications = adAnalyzer.verify_predictions(analyzed_ads, true_ds_of_ads, \
								account_truth["ALL"], alphas, betas, thresholds)
results = adAnalyzer.aggregate_verifications(verifications, alphas, betas, \
																	thresholds)

make_dirs(results, results_dir)
gen_plots(results, results_dir, alphas, betas, thresholds)
debug_logs(ad_list, results_dir)
