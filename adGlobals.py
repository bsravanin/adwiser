#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 14th January, 2013
Purpose: Global variables used throughout.
'''


import adLib
import os


ACCOUNT_TRUTH_DB = "dbs/accountTruth.db"
AD_TRUTH_DB = "dbs/adTruth.db"

ACCOUNT_TRUTH = adLib.true_ds_of_accounts(ACCOUNT_TRUTH_DB)
DS_TRUTH = adLib.true_accounts_of_ds(ACCOUNT_TRUTH)
AD_TRUTH = adLib.true_ds_of_ads(AD_TRUTH_DB)

MODELS = ["p_agg", "p_exp", "p_r_agg", "p_r_agg2", "p_r_exp", "p_r_exp2", \
			"p1_r1_agg", "p1_r1_exp", "p1_r2_agg", "p1_r2_exp", "p2_r1_agg", \
			"p2_r1_exp", "p2_r2_agg", "p2_r2_exp", "r_agg", "r_exp", \
			"wt_p_agg", "wt_p_exp",	"wt_p_r_agg", "wt_p_r_agg2", "wt_p_r_exp", \
			"wt_p_r_exp2", "wt_p1_r1_agg", "wt_p1_r1_exp", "wt_p1_r2_agg", \
			"wt_p1_r2_exp", "wt_p2_r1_agg", "wt_p2_r1_exp", "wt_p2_r2_agg", \
			"wt_p2_r2_exp", "wt_r_agg", "wt_r_exp"]
# TODO: p_harmonic, pr_harmonic, wt_p_harmonic, wt_pr_harmonic

ALPHAS = adLib.float_range(0, 1, 0.1)
BETAS = adLib.float_range(0, 1, 0.1)
THRESHOLDS = adLib.float_range(0, 1, 0.1)

MAX_PLOTS_PER_PNG = 6
