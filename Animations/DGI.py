#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 16:17:58 2018

@author: everettmeike
"""
#This script plots Democratic Vote Percent by district for each step of chain,
#Duke Gerrymandering Index (DGI) for each step of chain, using average democratic vote percent across the ensemble,
#and DGI using a cumulative average, i.e. showing how DGI changes from the initial plan with each step of chain.
#Also plots map of state with each run of chain (needs to be animated)
#Districts color coded between map and democratic vote percent plot

import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import json
import pandas as pd

#Open json and geojson files from chain
data_w = json.load(open("mo_chain_run.json"))
df = gpd.read_file("mo_dists.geojson")

#Rename rep and dem vote columns
df["rvotes"] = df['GOV_RV08']
df['dvotes'] = df['GOV_DV08']

#Since data is read in terms of VTDs, we need to create new DataFrame that 
#groups voting data by district
cd = df.groupby(by = ['CD'])['rvotes','dvotes'].sum()

#Initialize dem vote percent DataFrame
d_vote = pd.DataFrame(index = list(cd.index))

#This creates a d_vote DataFrame with rows for each district and columns for
#each step in chain
for i in range(1, len(data_w) + 1): 
    df["CD"+str(i)] = df["GEOID10"].map(data_w[str(i)])
    cd = df.groupby(by = ['CD' + str(i)])['rvotes','dvotes'].sum()
    
    cd['CD' + str(i)] = list(cd.index)
    
    cd['dvotepercent'] = cd['dvotes'] / (cd['dvotes'] + cd['rvotes'])
    d_vote["CD"+str(i)] = cd['dvotepercent']


#Initialize Duke Gerrymandering Index Array to be plotted
dukegi = np.zeros(len(data_w))    

#Creates array of numbers representing each district
num = len(d_vote['CD1'])
num_dist = np.arange(num)

#Initialize plots
fig, axs = plt.subplots(2, 2, 'none',figsize=(10,10))
#This will be x-axis for dem vote percent plot.
#distjit adds noise for better data visualization
district = list(cd.index)
distjit = np.random.normal(0, .05, len(cd.index))+range(1,len(cd.index)+1)

for i in range(1,1000):
    #plots democratic vote percent by district for each step of chain
    district = list(cd.index)
    distjit = np.random.normal(0, .05, len(cd.index))+range(1,len(cd.index)+1)
    axs[0,0].scatter(distjit, d_vote["CD"+str(i)], alpha = .05, s = [5], c = np.around(num_dist), cmap='Dark2')
    axs[0,0].set_xticks(num_dist)
    axs[0,0].set_ylabel('Dem Vote %')
    axs[0,0].set_xlabel('District')
    #Calculates and plots DGI for each step of chain
    vote_by_district = d_vote.iloc[:,i]
    dukegi[i] = np.std(vote_by_district) 
    axs[1,0].scatter(i, dukegi[i], s = [2], c = 'black')
    axs[1,0].plot([1,1000], [dukegi[1],dukegi[1]], color = 'orange') #Draws line to compare to initial DGI
    axs[1,0].set_ylabel('Duke Gerrymandering Index')
    axs[1,0].set_xlabel('D')
    #Calculates and plots DGI with cumulative average
    rolling_average = [d_vote.iloc[row_number,0:i].mean() for row_number in range(num)]
    rolling_difference_from_start = rolling_average - d_vote.iloc[:,0]
    dgi_moving_deviation = (sum([x**2 for x in rolling_difference_from_start]))**.5
    axs[0,1].scatter(i, dgi_moving_deviation, s = [2], color = 'green')
    axs[0,1].set_xlabel('D')
    axs[0,1].set_ylabel('DGI Moving Avg')
    # Make the GeoPandas plot
    df.plot(ax=axs[1,1], column="CD"+str(i), cmap='Dark2')
    #Saves figures to be made into movie
    plt.savefig("MO_eg%03d.png"%i)
