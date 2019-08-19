#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Purpose: Moves all the figures and tables to Overleaf
@author: olivergiesecke
"""

###############################################################################
### Import Python packages ###
import os  
import subprocess
import logging
import sys
###############################################################################
### Set the working directory ###

## Clear output and the old version of latex file
#try:
#    os.system('rm  ~/Dropbox/Apps/Overleaf/Firms\ and\ Monetary\ Policy/tables_figures/*')
#    print('Removed all files from Overleaf')
#except:
#    print('No outputs available')

destination = "~/Dropbox/Apps/Overleaf/FOMC_Summer2019/files/"


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
        
        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).
        
        The "answer" return value is True for "yes" or False for "no".
        """
    valid = {"yes": True, "y": True, "ye": True,
        "no": False, "n": False}

    sys.stdout.write(question+" Enter 'yes' or 'no':")
    choice = input().lower()
    if choice in valid:
        return valid[choice]
    else:
        print("Invalid response")


answer=query_yes_no("Remove all files from the Overleaf directory?",None)
if answer==True:
    os.system('rm '+ destination + '/*')
    print('All files cleared')
    
answer=query_yes_no("Push all the files to the Overleaf directory?",None)
if answer==True:
    os.system('cp  ../data/overleaf_manual_files/* '+destination )
    os.system('cp  ../output/overleaf_files/* '+destination )
    print('Files pushed to Overleaf')

    
    