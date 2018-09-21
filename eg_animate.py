# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 11:45:35 2018
Parameters:
    -vd: visual dictionary output by viz_dict script
    -gj: geojson containing all VTD-CD pairings at each step
    -filename: name of PNG files (step number will be appended to filename)
    -step: output a PNG for every nth step in the dictionary 

Output: 
    -dictionary with various attributes relevant to plotting
    -if no state geojson is input, will convert chain_run of flips to contain 
    all VTD-CD pairings at each step (stored as expanded_chain_run.json) and 
    state goejson with the desired format (stored as state_final.geojson)
@author: Mallory
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import pandas as pd
import geopandas as gpd

def eg_animate(vd, gj, filename, step=1):
    df = gpd.read_file(gj)

    num_figs = len(vd['eg']['m'])
    N = len(vd['dist']['d_init'])
    dist_num = np.around(vd['dist']['d'])
    
    #initialize horizontal lines on barplots
    x_min = dist_num-.2
    x_max = dist_num+.2
    

    # Preprocessing for top left plot
    rwaste_prop_init = vd['rwaste']['d_init'] / vd['tout']['d_init']
    rwaste_prop = vd['rwaste']['d'] / vd['tout']['d']
    dwaste_prop_init = vd['dwaste']['d_init'] / vd['tout']['d_init']
    dwaste_prop = vd['dwaste']['d'] / vd['tout']['d']
    lose = np.array(['blue'] * len(vd['win']['d']))
    
    win_waste_init = rwaste_prop_init * 1
    lose_waste_init = dwaste_prop_init * 1
    win_waste_init[vd['win']['d_init'] == 'blue'] = dwaste_prop_init[vd['win']['d_init'] == 'blue']
    lose_waste_init[vd['win']['d_init'] == 'blue'] = rwaste_prop_init[vd['win']['d_init'] == 'blue']
    bottom_space_init = .5-lose_waste_init
    
    win_waste = rwaste_prop * 1
    lose_waste = dwaste_prop * 1
    win_waste[vd['win']['d'] == 'blue'] = dwaste_prop[vd['win']['d'] == 'blue']
    lose_waste[vd['win']['d'] == 'blue'] = rwaste_prop[vd['win']['d'] == 'blue']
    lose[vd['win']['d'] == 'blue'] = 'red'
    bottom_space = .5 - lose_waste
    
    tout_max = 1.05 * max(np.append(vd['tout']['d'], vd['tout']['d_init']))
    tout_min = .95 * min(np.append(vd['tout']['d'], vd['tout']['d_init']))
    eg_max =  1.05 * max(np.append(vd['eg']['init'], vd['eg']['m']))
    eg_min =  .95 * min(np.append(vd['eg']['init'], vd['eg']['m']))
    h = plt.hist(vd['eg']['m'])
    
    # Preprocessing for two histograms
    rho_bins = plt.hist(vd['rho']['m'])[1]
    rho_index = np.digitize(vd['rho']['m'], rho_bins)
    
    for i in range(0, num_figs, step):
        fig = plt.figure(figsize=[30, 20])
        gs = gridspec.GridSpec(2, 3)
    
        # go up to this index for district plots
        beg = int(N * (i - 1))
        end = int(N * i + 1)
    
        # Wasted Vote Proportion Barplot
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.bar(dist_num[beg:end], bottom_space[beg:end], color = 'white')
        ax1.bar(dist_num[beg:end], lose_waste[beg:end], bottom = bottom_space[beg:end], color = lose[beg:end])
        ax1.bar(dist_num[beg:end], .5, bottom = .5, color = vd['win']['d'][beg:end])
        ax1.bar(dist_num[beg:end], win_waste[beg:end], bottom = 1, color = vd['win']['d'][beg:end])
        ax1.hlines(bottom_space_init, x_min, x_max, color='green')
        ax1.hlines(1+win_waste_init, x_min, x_max, color='green')
        ax1.axhline(y=.5, color='white')
        ax1.axhline(y=1,color='white')
        ax1.set_xlabel('District')
        ax1.set_ylabel('Wasted Vote Proportion')
        ax1.set_ylim(ymax=1.5)
        ax1.set_yticks(np.array([0,.1,.2,.3,.4,.5,1,1.1,1.2,1.3,1.4,1.5]))
        ax1.set_yticklabels(['.5','.4', '.3','.2','.1','0','0','.1','.2','.3','.4','.5'])
    
        # Turnout by District
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.bar(dist_num[beg:end], vd['tout']['d'][beg:end], color=vd['win']['d'][beg:end])
        ax2.set_ylabel('Turnout')
        ax2.set_xlabel('District')
        ax2.hlines(vd['tout']['d_init'], x_min, x_max, color='green')
        ax2.set_ylim(ymax=tout_max, ymin=tout_min)
        
        #State Map
        ax3 = fig.add_subplot(gs[0, 2], frameon=False)
        df.plot(ax=ax3, column="CD"+str(int(i)), cmap='Dark2')
        ax3.axis('equal')
        ax3.set_xticks([])
        ax3.set_yticks([])
        
        # Histogram over plans by seat share 
        ax4 = fig.add_subplot(gs[1, 0])
        eg_by_seats = []
        for s in np.unique(vd['win']['m']):
            eg_by_seats.append([vd['eg']['m'][n] for n in range(int(i)) if vd['win']['m'][n]==s])         
        ax4.hist(eg_by_seats, stacked=True, bins=h[1])
        ax4.axvline(x=vd['eg']['init'], ls=':')
        ax4.set_ylim(ymax=1.05*max(h[0]))
        ax4.set_title('Efficiency Gap by Seats')
        
        #histogram over plans by rho
        ax5 = fig.add_subplot(gs[1, 1])
        eg_by_rho = []
        for r in np.unique(rho_index):
            eg_by_rho.append([vd['eg']['m'][n] for n in range(int(i)) if rho_index[n]==r])         
        ax5.hist(eg_by_rho, stacked=True, bins=h[1])
        ax5.axvline(x=vd['eg']['init'], c='r', ls=':')
        ax5.set_ylim(ymax=1.05*max(h[0]))
        ax5.set_title('Efficiency Gap by Rho')
        
        # Line graph of efficiency gap over plans
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.plot(range(i), vd['eg']['m'][:i])
        ax6.set_xlim(xmax=num_figs)
        ax6.set_ylim(ymin = eg_min, ymax = eg_max)
        ax6.plot([1, num_figs], [vd['eg']['init'], vd['eg']['init']], c='r', ls=':')
        ax6.set_ylabel('Statewide Efficiency Gap')
        ax6.set_xlabel('Plan Index')
        
        # Make the GeoPandas plot
        gs.update(wspace=0.5, hspace=0.5)
        fig = plt.gcf()
        # save png
        plt.savefig(filename % i)
        plt.close()


