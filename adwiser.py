#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 18th January, 2013
Purpose: To find whether ads are targeted or not, and on what if targeted.
'''


import adAnalyzer, adLib, adOps, adParser, adPlotter
import os, pylab, sys
from adGlobals import *


'''
adwiser = {"ads": adLib.load_ads(sys.argv[1])}
adwiser["prediction"] = adAnalyzer.analyze_ads(adwiser["ads"])
ad_truth = adLib.true_ds_of_ads("dbs/adTruth.db")
print adLib.ad_types_count(adwiser["ads"], ad_truth)

adwiser["truth"] = adAnalyzer.true_ds_of_ad_list(adwiser["ads"])
adwiser["verification"] = adAnalyzer.verify_predictions(adwiser)

# aggregates = adAnalyzer.aggregate_verifications(adwiser)
# adPlotter.draw_all_plots("tests/results", aggregates)
'''
