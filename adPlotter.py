#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 15th January, 2013
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
			for plot_type in ["default", "RvP"]:
				dir2 = "/" + model + "/" + x_key + "/" + plot_type

				if not os.path.exists(dirname + dir2):
					os.makedirs(dirname + dir2)
				if not os.path.exists(targeted_dir + dir2):
					os.makedirs(targeted_dir + dir2)


def save_plot(xlabel, ylabel, title, imgpath, plot_type="default"):
	'''Save the plotted graphs so far as specified path.
	
	Args:
		xlabel: Label for X-axis.
		ylabel: Label for Y-axis.
		title: Title of the plot.
		imgpath: Path where the plot(s) should be saved.
	'''
	pylab.xlabel(xlabel)
	pylab.ylabel(ylabel)

	if plot_type == "default":
		pylab.axis([0, 0.9, 0, 1])
		pylab.axhline(y=0.7, color="black", ls="dotted")
		pylab.annotate("y=0.7", xy=(0.9, 0.7))
	else:
		pylab.axis([0, 1, 0, 1])
		pylab.axvline(x=0.7, ymin=0.7, ymax=1, color="black", ls="dotted")
		pylab.annotate("r=0.7", xy=(0.7, 1))
		pylab.axhline(y=0.7, xmin=0.7, xmax=1, color="black", ls="dotted")
		pylab.annotate("p=0.7", xy=(1, 0.7))

	pylab.title(title)
	pylab.legend(loc="best", prop={'size':10})
	pylab.savefig(imgpath)
	pylab.clf()


def area(x_values, y_values):
	'''Find the area common to both curves related to the metrics, by splitting
	it into trapezoids.

	Args:
		x_values: List of x-coordinates.
		y_values: Dictionary of lists of y-coordinates.

	Return:
		Area: A non-negative floating point number.
	'''
	area = 0

	for i in range(1, len(x_values)):
		h = x_values[i] - x_values[i-1]
		a = min([y_values[metric][i-1] for metric in y_values])
		b = min([y_values[metric][i] for metric in y_values])
		area += (0.5 * h * (a+b))

	return area


def draw_single_plots(results_dir, results_set, plot_params):
	'''Draw a single plot per PNG based on the plot_params.

	Args:
		results_dir: Root directory to save all plots in.
		results_set: Multi-level dictionary of results with levels models,
		alphas, betas, thresholds, targeted (optional), metrics.
		plot_params: Dictionary of plot parameters and their values. Should
		specify model, metrics, x_key and fixed parameters.
	'''
	if "model" in plot_params:
		model = plot_params["model"]
	else:
		print "ERROR: Can't not fix a model to be plotted."
		return

	if "x_key" in plot_params:
		x_key = plot_params["x_key"]
	else:
		print "ERROR: No x_key specified."
		return

	if "metrics" not in plot_params or len(plot_params["metrics"]) == 0:
		print "ERROR: No metrics to be plotted."
		return
	else:
		metrics = plot_params["metrics"]


	x_values = []
	y_values = {}
	title = model + ". "
	imgpath = model + "/" + x_key + "/"
	imgname = ""

	if "targeted" in plot_params:
		title = "Targeted " + title
		imgpath = results_dir + "/targeted/" + imgpath
	else:
		imgpath = results_dir + "/" + imgpath

	if "alpha" in plot_params:
		alphas = [plot_params["alpha"]]
		title += "Alpha " + str(alphas[0]) + ". "
		imgname += "a" + str(alphas[0]) + "-"
	else:
		alphas = x_values = ALPHAS

	if "beta" in plot_params:
		betas = [plot_params["beta"]]
		title += "Beta " + str(betas[0]) + ". "
		imgname += "b" + str(betas[0]) + "-"
	else:
		betas = x_values = BETAS

	if "threshold" in plot_params:
		thresholds = [plot_params["threshold"]]
		title += "Threshold " + str(thresholds[0]) + "."
		imgname += "t" + str(thresholds[0])
	else:
		thresholds = x_values = THRESHOLDS

	for metric in metrics:
		y_values[metric] = []

	for a in range(0, len(alphas)):
		alpha = alphas[a]

		for b in range(0, len(betas)):
			beta = betas[b]

			for t in range(0, len(thresholds)):
				threshold = thresholds[t]

				if "targeted" in plot_params:
					for metric in metrics:
						y_values[metric].append(results_set[model][alpha][beta][threshold]["targeted"][metric])
				else:
					for metric in metrics:
						y_values[metric].append(results_set[model][alpha][beta][threshold][metric])

	if "precision" in metrics and "recall" in metrics \
		and not plot_params["plot"]:
		print title, area(x_values, y_values)

	if not plot_params["plot"]:
		return

	for metric in metrics:
		pylab.plot(x_values, y_values[metric], "-", label=metric)
	save_plot(x_key, "", title, imgpath + "default/" + imgname.strip("-") + \
																		".png")

	if "precision" in metrics and "recall" in metrics:
		precision = []
		recall = []

		# Recall is a monotonic function. Precision is not.
		for i in sorted(enumerate(y_values["recall"]), key=lambda x:x[1]):
			if y_values["precision"][i[0]] == 0 \
				and y_values["recall"][i[0]] == 0:
				continue

			precision.append(y_values["precision"][i[0]])
			recall.append(y_values["recall"][i[0]])

		pylab.plot(recall, precision, "-")
		save_plot("Recall", "Precision", title, imgpath + "RvP/" + \
											imgname.strip("-") + ".png", "RvP")


def draw_multi_plots(results_dir, results_set, plot_params):
	'''Draw a single plot per PNG based on the plot_params.

	Args:
		results_dir: Root directory to save all plots in.
		results_set: Multi-level dictionary of results with levels models,
		alphas, betas, thresholds, targeted (optional), metrics.
		plot_params: Dictionary of plot parameters and their values. Should
		specify model, metrics, x_key and fixed parameters.
	'''
	if "model" in plot_params:
		model = plot_params["model"]
	else:
		print "ERROR: Can't not fix a model to be plotted."
		return

	if "x_key" in plot_params:
		x_key = plot_params["x_key"]
	else:
		print "ERROR: No x_key specified."
		return

	if "z_key" in plot_params:
		z_key = plot_params["z_key"]
	else:
		print "ERROR: No z_key specified."
		return

	if "metrics" not in plot_params or len(plot_params["metrics"]) == 0:
		print "ERROR: No metrics to be plotted."
		return
	else:
		metrics = plot_params["metrics"]


	x_values = []
	y_values = {}
	title = model + ". "
	imgpath = model + "/" + x_key + "/"
	imgname = ""

	if "targeted" in plot_params:
		title = "Targeted " + title
		imgpath = results_dir + "/targeted/" + imgpath
	else:
		imgpath = results_dir + "/" + imgpath

	if "alpha" in plot_params:
		alphas = [plot_params["alpha"]]
		title += "Alpha " + str(alphas[0]) + ". "
		imgname += "a" + str(alphas[0]) + "-"
	else:
		alphas = x_values = ALPHAS

	if "beta" in plot_params:
		betas = [plot_params["beta"]]
		title += "Beta " + str(betas[0]) + ". "
		imgname += "b" + str(betas[0]) + "-"
	else:
		betas = x_values = BETAS

	if "threshold" in plot_params:
		thresholds = [plot_params["threshold"]]
		title += "Threshold " + str(thresholds[0]) + "."
		imgname += "t" + str(thresholds[0])
	else:
		thresholds = x_values = THRESHOLDS

	if z_key == "alpha":
		z_values = ALPHAS
	elif z_key == "beta":
		z_values = BETAS
	elif z_key == "threshold":
		z_values = THRESHOLDS
	else:
		print "ERROR: Unknown z_key", z_key
		return

	for z_value in z_values:
		y_values[z_value] = {}

		for metric in metrics:
			y_values[z_value][metric] = []

	for a in range(0, len(alphas)):
		alpha = alphas[a]

		if z_key == "alpha":
			z_value = alpha

		for b in range(0, len(betas)):
			beta = betas[b]

			if z_key == "beta":
				z_value = beta

			for t in range(0, len(thresholds)):
				threshold = thresholds[t]

				if z_key == "threshold":
					z_value = threshold

				if "targeted" in plot_params:
					for metric in metrics:
						y_values[z_value][metric].append(results_set[model][alpha][beta][threshold]["targeted"][metric])
				else:
					for metric in metrics:
						y_values[z_value][metric].append(results_set[model][alpha][beta][threshold][metric])

	plots_per_png = 0
	plot = 0
	for z_value in sorted(z_values):
		for metric in metrics:
			pylab.plot(x_values, y_values[z_value][metric], "-", \
							label=metric + ". " + z_key + " " + str(z_value))

			plots_per_png += 1
			div = str(plots_per_png / MAX_PLOTS_PER_PNG)

			if plots_per_png % MAX_PLOTS_PER_PNG == 0:
				save_plot(x_key, "", title, imgpath + "default/" + \
								imgname.strip("-") + "-" + str(plot) + ".png")
				plot += 1
	save_plot(x_key, "", title, imgpath + "default/" + imgname.strip("-") + \
													"-" + str(plot) + ".png")

	plots_per_png = 0
	plot = 0
	if "precision" in metrics and "recall" in metrics:
		for z_value in sorted(z_values):
			precision = []
			recall = []

			# Recall is a monotonic function. Precision is not.
			for i in sorted(enumerate(y_values[z_value]["recall"]), \
															key=lambda x:x[1]):
				if y_values[z_value]["precision"][i[0]] == 0 \
					and y_values[z_value]["recall"][i[0]] == 0:
					continue

				precision.append(y_values[z_value]["precision"][i[0]])
				recall.append(y_values[z_value]["recall"][i[0]])

			pylab.plot(recall, precision, "-", label=z_key + " " + str(z_value))
			plots_per_png += 1

			if plots_per_png % MAX_PLOTS_PER_PNG == 0:
				save_plot("Recall", "Precision", title, imgpath + "RvP/" + \
						imgname.strip("-") + "-" + str(plot) + ".png", "RvP")
				plot += 1
		save_plot("Recall", "Precision", title, imgpath + "RvP/" + \
						imgname.strip("-") + "-" + str(plot) + ".png", "RvP")


def draw_all_plots(results_dir, results_set):
	'''Draw all possible plots for all models, alphas, betas and thresholds.

	Args:
		results_dir: Root directory to save all plots in.
		results_set: Multi-level dictionary of results with levels models,
		alphas, betas, thresholds, targeted (optional), metrics.
	'''
	make_plot_dirs(results_dir)
	plot = False

	for model in MODELS:
		for alpha in ALPHAS:
			for beta in BETAS:
				plot_params = {"model": model, "x_key": "threshold", \
								"alpha": alpha, "beta": beta, "targeted": True,\
								"plot": plot, \
								"metrics": ["precision", "recall"]}
				draw_single_plots(results_dir, results_set, plot_params)
														
		
		for alpha in ALPHAS:
			for threshold in THRESHOLDS:
				plot_params = {"model": model, "x_key": "beta", \
								"alpha": alpha,	"threshold": threshold, \
								"targeted": True, "plot": plot, \
								"metrics": ["precision", "recall"]}
				draw_single_plots(results_dir, results_set, plot_params)

		for beta in BETAS:
			for threshold in THRESHOLDS:
				plot_params = {"model": model, "x_key": "alpha", "beta": beta, \
								"threshold": threshold, "targeted": True, \
								"plot": plot, \
								"metrics": ["precision", "recall"]}
				draw_single_plots(results_dir, results_set, plot_params)
		'''

		for alpha in ALPHAS:
			plot_params = {"model": model, "x_key": "threshold", \
							"z_key": "beta", "alpha": alpha, "targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)

			plot_params = {"model": model, "x_key": "beta", \
							"z_key": "threshold", "alpha": alpha, \
							"targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)

		for beta in BETAS:
			plot_params = {"model": model, "x_key": "threshold", \
							"z_key": "alpha", "beta": beta, "targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)

			plot_params = {"model": model, "x_key": "alpha", \
							"z_key": "threshold", "beta": beta, \
							"targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)

		for threshold in THRESHOLDS:
			plot_params = {"model": model, "x_key": "alpha", "z_key": "beta", \
							"threshold": threshold, "targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)

			plot_params = {"model": model, "x_key": "beta", "z_key": "alpha", \
							"threshold": threshold, "targeted": True, \
							"metrics": ["precision", "recall"]}
			draw_multi_plots(results_dir, results_set, plot_params)
		'''
