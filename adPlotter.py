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
