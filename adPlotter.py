#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd January, 2013
Purpose: To draw different kinds of plots.
'''

import os, pylab
from adGlobals import *


def make_plot_dirs(dirname):
	'''Create the required directories for plots.'''
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


def draw_plot_dict_keys(plot_dict, keys, plot_types, labels, targeted=False):
	'''Plot values of plot_dict[x][key] for each key in keys, against each key
	in plot_dict.'''
	x_values = sorted(plot_dict.keys())

	for i in range(0, len(keys)):
		y_values = []

		for x in x_values:
			if targeted:
				y_values.append(plot_dict[x]["targeted"][keys[i]])
			else:
				y_values.append(plot_dict[x][keys[i]])

		pylab.plot(x_values, y_values, plot_types[i], label=labels[i])


def draw_plot_dict_vs(plot_dict, x_key, y_key, plot_type, label, targeted=False):
	'''Plot values of plot_dict[key][y_key] against xy_dict[z][x_key] for each
	key in plot_dict.'''
	x_values = []
	y_values = []

	for z in sorted(plot_dict.keys()):
		if targeted:
			x_values.append(xy_dict[z]["targeted"][x_key])
			y_values.append(xy_dict[z]["targeted"][y_key])
		else:
			x_values.append(xy_dict[z][x_key])
			y_values.append(xy_dict[z][y_key])

	pylab.plot(x_values, y_values, plot_type, label=label)


def save_plot(xlabel, ylabel, title, imgpath):
	'''Save the plotted graphs so far as specified path.'''
	pylab.xlabel(xlabel)
	pylab.ylabel(ylabel)
	pylab.axis([0, 1, 0, 1])
	pylab.title(title)
	pylab.legend()
	pylab.savefig(imgpath)
	pylab.clf()


def draw_plots(results_dir, results_set, fixed_params, x_key, metrics):
	'''Draw plots fixing the keys in fixed_params to their values, plotting all
	possible values of metrics agains values of x_key.'''
	if x_key in fixed_params:
		print "ERROR: Can't fix a parameter and plot a graph against it."
		return

	if "model" not in fixed_params:
		print "ERROR: Can't not fix a model to be plotted."
		return

	x_values = []
	y_values = {}
	model = fixed_params["model"]
	title = model + ". "
	label = ""
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

	if "beta" in fixed_params:
		betas = [fixed_params["beta"]]
		title += "Beta " + str(betas[0]) + ". "
		imgpath += "b" + str(betas[0]) + "-"
	elif x_key == "beta":
		betas = x_values = BETAS

	if "threshold" in fixed_params:
		thresholds = [fixed_params["threshold"]]
		title += "Threshold " + str(thresholds[0]) + "."
		imgpath += "t" + str(thresholds[0])
	elif x_key == "threshold":
		thresholds = x_values = THRESHOLDS

	for metric in metrics:
		y_values[metric] = []

	for alpha in alphas:
		if "alpha" not in fixed_params and x_key != "alpha":
			title += "All Alphas. "
			label += "Alpha = " + str(alpha) + ". "

		for beta in betas:
			if "beta" not in fixed_params and x_key != "beta":
				title += "All Betas. "
				label += "Beta = " + str(beta) + ". "

			for threshold in thresholds:
				if "threshold" not in fixed_params and x_key != "threshold":
					title += "All Thresholds. "
					label += "Threshold = " + str(threshold) + ". "

				if "targeted" in fixed_params:
					for metric in metrics:
						y_values[metric].append(results_set[model][alpha][beta][threshold]["targeted"][metric])
				else:
					for metric in metrics:
						y_values[metric].append(results_set[model][alpha][beta][threshold][metric])

	for metric in metrics:
		pylab.plot(x_values, y_values[metric], "o-", label=metric)
	save_plot(x_key, "", title, imgpath.strip("-") + ".png")

	if "precision" in metrics and "recall" in metrics:
		precision = []
		recall = []

		for i in sorted(enumerate(y_values["precision"]), key=lambda x:x[1]):
			precision.append(y_values["precision"][i[0]])
			recall.append(y_values["recall"][i[0]])

		pylab.plot(precision, recall, "o-")
		save_plot("Precision", "Recall", title, imgpath.strip("-") + "-PvR.png")


def draw_all_plots(results_dir, results_set):
	'''Draw all possible plots for all models, alphas, betas and thresholds.'''
	make_plot_dirs(results_dir)

	for model in MODELS:
		for alpha in ALPHAS:
			for beta in BETAS:
				fixed_params = {"model": model, "alpha": alpha, "beta": beta, \
															"targeted": True}
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
