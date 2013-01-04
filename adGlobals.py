#! /usr/bin/python
'''
Name: Sravan Bhamidipati
Date: 3rd January, 2013
Purpose: Global variables used throughout.
'''

import adLib
import os


AD_TRUTH_DB = "dbs/adTruth.db"
ACCOUNT_TRUTH_DB = "dbs/accountTruth.db"
MODELS = ["p_agg", "p_exp", "p_r_agg", "p_r_exp", "wt_p_agg", "wt_p_exp", \
			"wt_p_r_agg", "wt_p_r_exp"]
# TODO: p_harmonic, pr_harmonic, wt_p_harmonic, wt_pr_harmonic

ALPHAS = BETAS = THRESHOLDS = adLib.float_range(0, 0.9, 0.1)
# ALPHAS = BETAS = [0.5]
# THRESHOLDS = adLib.float_range(0, 1, 0.1)
ACCOUNT_TRUTH = adLib.true_ds_of_accounts(ACCOUNT_TRUTH_DB)
DS_TRUTH = adLib.true_accounts_of_ds(ACCOUNT_TRUTH)
AD_TRUTH = adLib.true_ds_of_ads(AD_TRUTH_DB)
