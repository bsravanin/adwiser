#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 5th January, 2013
Purpose: To draw different kinds of plots.
'''


import os, pylab
from adGlobals import *


def make_plot_dirs(dirname):
	'''Create the required directories for plots.

	Args:
		dirname: Root directory of results.
	'''
	targeted_dir = dirname + "/targeted"

	if not os.path.exists(targeted_dir):
		os.makedirs(targeted_dir)

	for model in MODELS:
		for x_key in ["alpha", "beta", "threshold"]:
			dir2 = "/" + model + "/" + x_key

			if not os.path.exists(dirname + dir2):
				os.makedirs(dirname + dir2)
			if not os.path.exists(targeted_dir + dir2):
				os.makedirs(targeted_dir + dir2)


def save_plot(xlabel, ylabel, title, imgpath):
	'''Save the plotted graphs so far as specified path.
	
	Args:
		xlabel: Label for X-axis.
		ylabel: Label for Y-axis.
		title: Title of the plot.
		imgpath: Path where the plot(s) should be saved.
	'''
	pylab.xlabel(xlabel)
	pylab.ylabel(ylabel)
	pylab.axis([0, 0.9, 0, 1])
	pylab.title(title)
	pylab.legend(loc="best", prop={'size':10})
	pylab.savefig(imgpath)
	pylab.clf()


def draw_plots(results_dir, results_set, fixed_params, x_key, metrics):
	'''Draw plots fixing the keys in fixed_params to their values, plotting all
	possible values of metrics agains values of x_key.

	Args:
		results_dir: Root directory to save all plots in.
		results_set: Multi-level dictionary of results with levels models,
		alphas, betas, thresholds, targeted (optional), metrics.
		fixed_params: Dictionary of fixed parameters and their values.
		x_key: Parameter used for the X-axis.
		metrics: An array of "precision", "recall", "accuracy", "tnr", etc. each
		of which is optional.
	'''
	if x_key in fixed_params:
		print "ERROR: Can't fix a parameter and plot a graph against it."
		return

	if "model" not in fixed_params:
		print "ERROR: Can't not fix a model to be plotted."
		return

	x_values = []
	y_values = []
	plot_id = 0
	model = fixed_params["model"]
	title = model + ". "
	labels = []
	imgpath = model + "/" + x_key + "/"

	if "targeted" in fixed_params:
		title = "Targeted " + title
		imgpath = results_dir + "/targeted/" + imgpath
	else:
		imgpath = results_dir + "/" + imgpath

	if "alpha" in fixed_params:
		alphas = [fixed_params["alpha"]]
		title += "Alpha " + str(alphas[0]) + ". "
		imgpath += "a" + str(alphas[0]) + "-"
	elif x_key == "alpha":
		alphas = x_values = ALPHAS
	else:
		title += "All Alphas. "
		alphas = ALPHAS

	if "beta" in fixed_params:
		betas = [fixed_params["beta"]]
		title += "Beta " + str(betas[0]) + ". "
		imgpath += "b" + str(betas[0]) + "-"
	elif x_key == "beta":
		betas = x_values = BETAS
	else:
		title += "All Betas. "
		betas = BETAS

	if "threshold" in fixed_params:
		thresholds = [fixed_params["threshold"]]
		title += "Threshold " + str(thresholds[0]) + "."
		imgpath += "t" + str(thresholds[0])
	elif x_key == "threshold":
		thresholds = x_values = THRESHOLDS
	else:
		title += "All Thresholds. "
		thresholds = THRESHOLDS


	for a in range(0, len(alphas)):
		alpha = alphas[a]

		if "alpha" not in fixed_params and x_key != "alpha":
			labels.append("Alpha=" + str(alpha) + ". ")
			plot_id = a

		for b in range(0, len(betas)):
			beta = betas[b]

			if "beta" not in fixed_params and x_key != "beta":
				labels.append("Beta=" + str(beta) + ". ")
				plot_id = b

			for t in range(0, len(thresholds)):
				threshold = thresholds[t]

				if "threshold" not in fixed_params and x_key != "threshold":
					labels.append("Threshold=" + str(threshold) + ". ")
					plot_id = t

				if plot_id >= len(y_values):
					y_values.append({})
					for metric in metrics:
						y_values[plot_id][metric] = []

				if "targeted" in fixed_params:
					for metric in metrics:
						y_values[plot_id][metric].append(results_set[model][alpha][beta][threshold]["targeted"][metric])
				else:
					for metric in metrics:
						y_values[plot_id][metric].append(results_set[model][alpha][beta][threshold][metric])

	if len(labels) == 0:
		labels.append("")

	plots_in_png = 0

	for l in range(0, len(labels)):
		for metric in metrics:
			pylab.plot(x_values, y_values[l][metric], "o-", label=labels[l] + metric)
			plots_in_png += 1

			if plots_in_png % MAX_PLOTS_PER_PNG == 0:
				save_plot(x_key, "", title, imgpath.strip("-") + \
								str(plots_in_png/MAX_PLOTS_PER_PNG) + ".png")

	save_plot(x_key, "", title, imgpath.strip("-") + ".png")

	plots_in_png = 0

	if "precision" in metrics and "recall" in metrics:
		for l in range(0, len(labels)):
			precision = []
			recall = []

			for i in sorted(enumerate(y_values[l]["precision"]), key=lambda x:x[1]):
				precision.append(y_values[l]["precision"][i[0]])
				recall.append(y_values[l]["recall"][i[0]])

			pylab.plot(precision, recall, "o-", label=labels[l])
			plots_in_png += 1

			if plots_in_png % MAX_PLOTS_PER_PNG == 0:
				save_plot("Precision", "Recall", title, imgpath.strip("-") + \
						"-PvR" + str(plots_in_png/MAX_PLOTS_PER_PNG) + ".png")

		save_plot("Precision", "Recall", title, imgpath.strip("-") + "-PvR.png")


def draw_all_plots(results_dir, results_set):
	'''Draw all possible plots for all models, alphas, betas and thresholds.

	Args:
		results_dir: Root directory to save all plots in.
		results_set: Multi-level dictionary of results with levels models,
		alphas, betas, thresholds, targeted (optional), metrics.
	'''
	make_plot_dirs(results_dir)

	for model in MODELS:
		for alpha in ALPHAS:
			for beta in BETAS:
				fixed_params = {"model": model, "alpha": alpha, "beta": beta, \
															"targeted": True}
				draw_plots(results_dir, results_set, fixed_params, "threshold", \
														["precision", "recall"])

		for alpha in ALPHAS:
			fixed_params = {"model": model, "alpha": alpha, "targeted": True}
			draw_plots(results_dir, results_set, fixed_params, "threshold", \
													["precision", "recall"])

		for alpha in ALPHAS:
			for threshold in THRESHOLDS:
				fixed_params = {"model": model, "alpha": alpha, \
									"threshold": threshold, "targeted": True}
				draw_plots(results_dir, results_set, fixed_params, "beta", \
														["precision", "recall"])

		for beta in BETAS:
			for threshold in THRESHOLDS:
				fixed_params = {"model": model, "beta": beta, \
									"threshold": threshold, "targeted": True}
				draw_plots(results_dir, results_set, fixed_params, "alpha", \
														["precision", "recall"])
