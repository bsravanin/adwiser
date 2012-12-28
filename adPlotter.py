#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 19th December, 2012
Purpose: To draw different kinds of plots.
'''

import pylab


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
	# pylab.axis([0, 1, 0, 1])
	pylab.title(title)
	pylab.legend()
	pylab.savefig(imgpath)
	pylab.clf()


def draw_plots(results_set, fixed_params, x_key, metrics):
	'''Draw plots fixing the keys in fixed_params to their values, plotting all
	possible values of metrics agains values of x_key.'''
	if x_key in fixed_params:
		print "ERROR: Can't fix a parameter and plot a graph against it."
		return

	if "model" not in fixed_params:
		print "ERROR: Can't not fix a model to be plotted."
		return

	x_values = []
	y_values = []
	model = fixed_params["model"]

	if "targeted" in fixed_params:
		title = "Targeted " + model + ". "
	else:
		title = model + ". "

	for trial in results_set:
		label = ""

		if "trial" in fixed_params:
			trial = fixed_params["trial"]
			title += "Trials " + str(trial) + ". "
		elif x_key == "trial":
			x_values.append(trial)
		else:
			title += "All Trials. "
			label += "Trials = " + str(trial) + ". "

		for alpha in results_set[trial][model]:
			if "alpha" in fixed_params:
				alpha = fixed_params["alpha"]
				title += "Alpha " + str(alpha) + ". "
			elif x_key == "alpha":
				x_values.append(alpha)
			else:
				title += "All Alphas. "
				label += "Alpha = " + str(alpha) + ". "

			for beta in results_set[trial][model][alpha]:
				if "beta" in fixed_params:
					beta = fixed_params["beta"]
					title += "Beta " + str(beta) + ". "
				elif x_key == "beta":
					x_values.append(beta)
				else:
					title += "All Betas. "
					label += "Beta = " + str(beta) + ". "

				for threshold in results_set[trial][model][alpha][beta]:
					if "threshold" in fixed_params:
						threshold = fixed_params["threshold"]
						title += "Threshold " + str(threshold)
					elif x_key == "threshold":
						x_values.append(threshold)
					else:
						title += "All Thresholds. "
						label += "Threshold = " + str(threshold) + ". "

					if "targeted" in fixed_params:
						for metric in metrics:
							pass
					else:
						for metric in metrics:
							pass

					if "threshold" in fixed_params:
						break

				if "beta" in fixed_params:
					break

			if "alpha" in fixed_params:
				break

		if "trial" in fixed_params:
			break
