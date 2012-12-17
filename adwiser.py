#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 16th December, 2012
Purpose: To find relevance and irrelevance of Ds.
'''

import adAnalyzer, adOps, adParser
import os, pylab, sys

if len(sys.argv) > 2:
	adset_file = sys.argv[1]
	results_dir = sys.argv[2]
else:
	print "Usage: python", sys.argv[0], "<adset_file> <results_dir>"
	sys.exit(0)


debug_str = ""


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


def make_dirs(dirname):
	'''Create the required directories for results.'''
	if not os.path.isdir(dirname):
		if os.path.exists(dirname):
			print dirname, "exists and is not a directory."
		else:
			os.makedirs(dirname)


def single_plot(results, results_dir, plot, alphas, betas, thresholds):
	'''Single plots against threshold values for various alphas, betas for
	all models.'''
	x_values = thresholds

	for key in results:
		for alpha in alphas:
			for beta in betas:
				y_values = []

				for threshold in x_values:
					y_values.append(results[key][alpha][beta][threshold][plot])

				pylab.xlabel("Threshold")
				pylab.ylabel(plot)
				pylab.plot(x_values, y_values, "bo-")
				pylab.axis([0, 1, 0, 1])
				fig = key + "-" + plot + "-a" + str(round(alpha, 1)) + "-b" + \
															str(round(beta, 1))
				pylab.title(fig)
				pylab.savefig(results_dir + "/" + fig + ".png")
				pylab.clf()


def double_plot(results, results_dir, plot1, plot2, alphas, betas, thresholds):
	'''Double plots for various alphas, betas for all models.'''
	for key in results:
		for alpha in alphas:
			for beta in betas:
				x_values = []
				y_values = []

				for threshold in thresholds:
					x_values.append(results[key][alpha][beta][threshold][plot1])
					y_values.append(results[key][alpha][beta][threshold][plot2])

				pylab.xlabel(plot1)
				pylab.ylabel(plot2)
				pylab.plot(x_values, y_values, "bo-")
				pylab.axis([0, 1, 0, 1])
				fig = key + "-" + plot1 + "-" + plot2 + "-a" + \
							str(round(alpha, 1)) + "-b" + str(round(beta, 1))
				pylab.title(fig)
				pylab.savefig(results_dir + "/" + fig + ".png")
				pylab.clf()

				x_values = []
				y_values = []

				for threshold in thresholds:
					x_values.append(results[key][alpha][beta][threshold]["targeted"][plot1])
					y_values.append(results[key][alpha][beta][threshold]["targeted"][plot2])

				pylab.xlabel(plot1)
				pylab.ylabel(plot2)
				pylab.plot(x_values, y_values, "bo-")
				pylab.axis([0, 1, 0, 1])
				fig = "targeted" + "-" + key + "-" + plot1 + "-" + plot2 + \
						"-a" + str(round(alpha, 1)) + "-b" + str(round(beta, 1))
				pylab.title(fig)
				pylab.savefig(results_dir + "/" + fig + ".png")
				pylab.clf()


def gen_plots(results, results_dir, alphas, betas, thresholds):
	'''Draw various plots.'''
	# for plot in ("accuracy", "precision", "recall", "tnr"):
		# single_plot(results, results_dir, plot, alphas, betas, thresholds)

	double_plot(results, results_dir, "precision", "recall", alphas, betas, thresholds)
	double_plot(results, results_dir, "recall", "precision", alphas, betas, thresholds)


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

make_dirs(results_dir)
gen_plots(results, results_dir, alphas, betas, thresholds)
debug_logs(ad_list, results_dir)
