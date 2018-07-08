#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 6 10:30:41 2018

@author: hannah + eion
"""
import requests
import pandas as pd

# constants
CENSUS_API_KEY = "36ff0f593ede962a47e6e53c530380589a969aad"
HOST = "https://api.census.gov/data"

#set year for data and acs5 or sf1
year = "2010"
dataset = "sf1"
base_url = "/".join([HOST, year, dataset])

county_count = 36
state_fips = 41

#p5_vars = ["P005" + str(i + 1).zfill(4) for i in range(17)]
#get_vars = ["NAME"] + p5_vars
#get_vars = ["NAME", "P0050003", "P0050004"]
get_vars = ["NAME",
            "P0010001", #total population
            "P0030002", #white alone
            "P0030003", #Black/Afr. Am. alone
            "P0030004", #Asian alone
            "P0040003"#Hispanic or Latino
            ]

data = []
#loop over the 102 counties in IL
for i in range(1,2*county_count,2): 
    predicates = {}         
    predicates["get"] = ",".join(get_vars)
#    predicates["for"] = "block group:*"
    predicates["for"] = "block:*"
    predicates["in"] = "state:"+str(state_fips)+"+county:"+str(i)
    predicates["key"] = CENSUS_API_KEY

# Write the result to a response object:
    response = requests.get(base_url, params=predicates)
    try:
        col_names = response.json()[0]
        data = data + response.json()[1:]
    except :
        print(response.url)

census_df = pd.DataFrame(columns=col_names, data=data)
census_df.set_index(["state", "county", "tract", "block"], drop=False, inplace=True)
census_df['geoid'] = census_df['state'].astype(str) + census_df['county'].astype(str) + census_df['tract'].astype(str) + census_df['block'].astype(str)
census_df.to_csv("oregon_data.csv")
