# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 15:00:37 2018

@author: Mallory
"""


import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import json
from matplotlib import gridspec


def compactness_viz(file1, file2, score='polsby-popper',
                    step=10, statewide='add', inverse=False,
                    name='comp%03d.png'):

    """Generates a png for each step in chain with compactness metrics
    :file 1: a geojson
    :file 2: a json of chain output, formatted as a dictionary where the keys
             are steps in chain and the values are tuples where the first entry
             is an assignment dictionary and the second is a dictionary
             of districts' compactness scores
    :score: compactness score used, for labeling plots
    :step: output a png after every n steps in chain
    :statewide: how to aggregate district level scores (add, min, max)
    :inverse: work with reciprocal of scores?
    :name: what to call pngs
    :returns: a png for each step in the chain. 
    """
    
    
    df = gpd.read_file(file1)
    data_w = json.load(open(file2))

    # number of figures to output (len(data_w.keys())+1 for whole chain)
    num_figs = len(data_w.keys())     # len(data_w.keys())+1
    step = step

    # loop through plans to build lists for district & statewide scores
    for i in range(0, num_figs, step):
        my_dscore = []
        # identifies number of districts
        if i == 0:
            n_dist = len(data_w['0'][1].keys())
        # list of score by district
        for d in range(1, n_dist+1):
            my_dscore.append(data_w[str(i)][1][str(d)])
        # finds statewide score based on inputted statewide method
        if statewide == 'best':
            my_sscore = min(my_dscore)
        if statewide == 'worst':
            my_sscore = max(my_dscore)
        # if inverse, use reciprocals
        if inverse:
            my_dscore = 1/my_dscore
            if statewide == 'best' or statewide == 'worst':
                my_sscore = 1/inverse
        if statewide == 'add':
            my_sscore = sum(my_dscore)
        # save initial values separately
        if i == 0:
            dscore_init = np.array(my_dscore)
            sscore_init = my_sscore
            continue
        # initialize lists of scores for plans
        elif i == 1:
            df["CD"+str(i)] = df["wes_id"].map(data_w[str(i)][0])
            dscore = my_dscore
            sscore = [my_sscore]
            dscore_diff = list(np.array(my_dscore) - dscore_init)
            dist = list(np.random.normal(0, .1, n_dist) +
                        [float(d) for d in data_w['0'][1].keys()])
        # append to lists of scores for plans
        else:
            df["CD"+str(i)] = df["wes_id"].map(data_w[str(i)][0])
            dscore = dscore + my_dscore
            dscore_diff = dscore_diff + list(np.array(my_dscore) - dscore_init)
            dist = dist + list(np.random.normal(0, .1, n_dist) +
                               [float(d) for d in data_w['0'][1].keys()])
            sscore.append(my_sscore)

    # compute parameters for plot limits to keep figure axes static
    h = plt.hist(sscore)
    sscore_min = .99*min(sscore_init, min(sscore))
    sscore_max = 1.01*max(sscore_init, max(sscore))
    dscore_min = .99*min(min(dscore_init), min(dscore))
    dscore_max = 1.01*max(max(dscore_init), max(dscore))

    # output a png for each step in the chain, starting from the 2nd step
    for i in range(2*step, num_figs, step):
        fig = plt.figure(figsize=[20, 20])
        gs = gridspec.GridSpec(4, 2)

        # go up to this index for district plots
        d_ind = int(n_dist * i / step + 1)

        # Plot compactness score by district
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.scatter(dist[1: d_ind], dscore[1:d_ind], alpha=.2,
                    c=np.around(dist[1:d_ind]), cmap='tab20')
        ax1.scatter([int(d) for d in data_w['0'][1].keys()], dscore_init,
                    c='gray', marker='.')
        ax1.set_ylim(ymin=dscore_min, ymax=dscore_max)
        ax1.set_ylabel(score)
        ax1.set_xlabel('District')

        # Plot diff btw per district compactness score for plans & original
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.scatter(dist[1:d_ind], dscore_diff[1:d_ind], alpha=.2,
                    c=np.around(dist[1:d_ind]), cmap='tab20')
        ax2.axhline(y=0, color="black", ls='--')
        ax2.set_ylabel(score)
        ax2.set_xlabel('District')
        ax2.set_ylim(ymin=min(dscore_diff), ymax=max(dscore_diff))

        # line graph of statewide compactness score over plans
        ax3 = fig.add_subplot(gs[1, 0])
        
        ax3.plot(range(step, int(i+step), step), sscore[1:int(i/step+1)])
        ax3.set_xlim(xmax=num_figs)
        ax3.set_ylim(ymax=sscore_max, ymin=sscore_min)
        ax3.plot([1, num_figs], [sscore_init, sscore_init], 'r:')
        ax3.set_xlabel('Plan Index')        
        ax3.set_xlabel('Statewide Score:' + statewide)

        # Histogram over plans
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axvline(x=sscore_init, color="red")
        ax4.hist(sscore[1:int(i/step+1)], bins=h[1])
        ax4.set_ylim(ymax=max(h[0]))
        ax4.set_ylabel('Frequency')
        ax4.set_xlabel('Statewide Score:' + statewide)

        # Make the GeoPandas plot
        ax5 = fig.add_subplot(gs[2:, :])
        df.plot(ax=ax5, column="CD"+str(i), cmap='tab20')
        ax5.axis('equal')
        gs.update(wspace=0.5, hspace=0.5)
        fig = plt.gcf()

        # save png
        plt.savefig(name % (i-1))
        plt.close()

