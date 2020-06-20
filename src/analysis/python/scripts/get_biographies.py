#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
READ IN: 
    1) Angrist Kuersteiner Jorda Data "../data/speaker_biographies.xlsx"

EXPORT:
    "../output/biographydata.csv"
    
@author: olivergiesecke
"""


import pandas as pd
import numpy as np
import os
import re



df = pd.read_excel("../data/speaker_biographies.xlsx")

df.to_csv("../output/biographydata.csv")