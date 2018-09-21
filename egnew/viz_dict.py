# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 11:49:19 2018

Parameters:
    -chain_run: json of chain run. Either matchings of vtds to districts at each
    step or VTDs and the district they flip to at each step. If the latter, will
    need to input voting_shp and adj_graph to get json of desired format.
    -rvotecol: name of column containing Republican votes
    -dvotecol: name of column containing Democratic votes
    -voting_shp: shapefile of VTDs with voting data
    -adj_graph: adjacency graph with initial Congressional Districts 
    -state_geojson: geojson file with voting data and initial Congressional Districts
    for VTDs
    -step: generate a png every nth step of the chain
 

Output: 
    -dictionary with various attributes relevant to plotting
    -if no state geojson is input, will convert chain_run of flips to contain 
    all VTD-CD pairings at each step (stored as expanded_chain_run.json) and 
    state goejson with the desired format (stored as state_final.geojson)
@author: Mallory
"""

import geopandas as gpd
import os
import numpy as np
import json
import shapefile
from json import dumps



def viz_dict(chain_run, rvotecol, dvotecol, voting_shp=None, adj_graph=None,
             state_geojson=None, step=1):          
    if state_geojson is None:
        # convert your prorated voting data shapefile to a geojson, code taken
        # from here: https://gist.github.com/frankrowe/6071443#file-shp2gj-py-L6
        # read the shapefile
        reader = shapefile.Reader(voting_shp)
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []
        for sr in reader.shapeRecords():
           atr = dict(zip(field_names, sr.record))
           geom = sr.shape.__geo_interface__
           buffer.append(dict(type="Feature", geometry=geom, properties=atr)) 

       # write the GeoJSON file
        geojson = open("state_intermediate.geojson", "w")
        geojson.write(dumps({"type": "FeatureCollection",\
                      "features": buffer}, indent=2) + "\n")
        geojson.close()    
        df = gpd.read_file("state_intermediate.geojson")
        df['CD'] = df['NAME10']
        
        # change json of flips to json of steps containing all
        # vtd-congresional district pairs
        data_w = json.load(open(chain_run))   
        adj = json.load(open(adj_graph))   
 
        dd = {}
        for vtd in adj['nodes']:
            my_id = vtd['id']
            dd[my_id] = vtd['CD']            
            df['CD'][df['GEOID10'] == my_id] = vtd['CD']
            
        lod=[dd,dd,dd,dd]
        
        for i in range(len(data_w.keys())):
            if (data_w[str(i)][0] is not None):
                lod.append(lod[-1].copy())
                tempd=data_w[str(i)][0]
                lod[i + 1][list(data_w[str(i)][0].keys())[0]] = tempd[list(data_w[str(i)][0].keys())[0]]
        df.to_file("state_final.geojson", driver='GeoJSON')
        data_w.to_file("expanded_chain_run.json", driver='JSON')
    
    else:
        df = gpd.read_file(state_geojson)
        data_w = json.load(open(chain_run)) 
 
   
#dd: {node: CD}A
    
    # number of figures to output (len(data_w.keys())+1 for whole chain)
    num_figs = len(data_w.keys())     # len(data_w.keys())+1

    df['rvotes'] = df[rvotecol]
    df['dvotes'] = df[dvotecol]
    
    dist = []
    deg = []
    tout = []
    deg_diff = []
    dcomp = []
    dshare = []
    dwaste = []
    rwaste = []
    rho = []
    vs = []
    win = []
    seats = []
    shares = []
    ss = []
    dpp = []
    dipp = []
    eg = []
    dgi = []
    mm = []
    mt = []
    pp_avg = []
    pp_min = []
    pp_max = []
    ipp_avg = []
    ipp_min = []
    ipp_max = []
    
    for i in range(0, num_figs, step):
    # calculate metrics for original map
        if i == 0:
            cd = df.groupby(by=['CD']).sum()
            N = np.shape(cd)[0]
            dist_init = range(1, N+1)
            
            rvotes = np.array(cd['rvotes'])
            dvotes = np.array(cd['dvotes'])
            tout_init = rvotes+dvotes
            
            shares_init = dvotes / tout_init
            win_init = np.array(['blue'] * N)
            win_init[shares_init < .5] = 'red'
            seats_init = sum(win_init == 'blue')
            rho_init = np.mean(tout_init[win_init=='red']) / np.mean(tout_init[win_init=='blue'])           
            
            #calculate waste vote at district level
            dwaste_init = dvotes * 1
            rwaste_init = rvotes - tout_init/2 
            for i in range(N):
                if win_init[i]=='blue':
                    dwaste_init[i] = dvotes[i] - tout_init[i]/2
                    rwaste_init[i] = rvotes[i]
            deg_init = (dwaste_init-rwaste_init)/tout_init
            eg_init = (sum(dwaste_init)-sum(rwaste_init))/sum(tout_init)
     
     #       vs_init = .5 + shares_init - np.mean(shares_init)
     #       vs_init = np.append(np.append(0, vs_init), 1)
     #       ss_init = sum(dvotes > rvotes) / N
     #       mm_init = np.median(shares_init) - np.mean(shares_init)
     #       mt_init = np.quantile(shares_init, 33) - np.mean(shares_init)
     #   
     #  NEEDS WORK...formatting for compactness scores. This can currently be
     #  outputted manually through the partitions class but not through the GUI
     #       dpp_init = []
     #       dipp_init = []
     #       for d in range(1, N+1):
     #           dpp_init.append(data_w[str(i)][1][str(d)])
     #           dipp_init.append(1/data_w[str(i)][1][str(d)])
     #       
     #       pp_sum_init = np.sum(dpp_init)
     #       pp_min_init = np.min(dpp_init)
     #       pp_max_init = np.max(dpp_init)
     #       ipp_sum_init = np.sum(dipp_init)
     #       ipp_min_init = np.min(dipp_init)
     #       ipp_max_init = np.max(dipp_init)     
            

        # each step in chain
        else:
            df["CD"+str(i)] = df["GEOID10"].map(data_w[str(i)])
            cd = df.groupby(by=["CD"+str(i)]).sum()
            #district numbers with random noise added for district (useful for
            # scatterplots)
            dist = np.append(dist, np.random.normal(0, .1, N) + range(1, N+1))
            
            rvotes = np.array(cd['rvotes'])
            dvotes = np.array(cd['dvotes'])
            this_tout = rvotes + dvotes
            tout = np.append(tout, this_tout)
            
            this_shares = dvotes / this_tout
            shares = np.append(shares, this_shares)
            shares_diff = np.append(shares, this_shares - shares_init)
            this_dgi = np.sum((np.sort(this_shares) - np.sort(shares_init))**2)**.5
            dgi.append(this_dgi)
           
            this_win = np.array(['blue'] * N)
            this_win[this_shares < .5] = 'red'
            win = np.append(win, this_win)
            seats = np.append(seats, sum(this_win == 'blue'))
            this_dwaste = dvotes * 1
            this_rwaste = rvotes - this_tout/2
            rho = np.append(rho, np.mean(this_tout[this_win=='red']) / np.mean(this_tout[this_win=='blue']))
            
            #calculate wasted votes in each district
            for i in range(N):
                if this_win[i]=='blue':
                    this_dwaste[i] = dvotes[i] - (this_tout[i])/2
                    this_rwaste[i] = rvotes[i]
                    
                    
            this_deg = (this_dwaste-this_rwaste)/this_tout
            dwaste = np.append(dwaste, this_dwaste)
            rwaste = np.append(rwaste, this_rwaste)
            deg = np.append(deg, this_deg)
            deg_diff = np.append(deg_diff, this_deg - deg_init)
            eg.append((sum(this_dwaste)-sum(this_rwaste))/sum(this_tout))
 
  #      this_vs = .5 + this_shares - np.mean(this_shares)
  #      this_vs = np.append(np.append(0, this_vs), 1)
  #      vs.append(this_vs)
  #      ss.append(sum(dvotes > rvotes) / N)
  #      mm.append(np.median(this_shares) - np.mean(this_shares))
  #      mt.append(np.quantile(this_shares, 33) - np.mean(this_shares))
  #  
  #      this_dpp = []
  #      this_dpp = []
  #      for d in range(1, N+1):
  #          dpp.append(data_w[str(i)][1][str(d)])
  #          dipp.append(1/data_w[str(i)][1][str(d)])
  #      
  #      pp_sum = np.sum(dpp)
  #      pp_min = np.min(dpp)
  #      pp_max = np.max(dpp)
  #      ipp_sum = np.sum(dipp)
  #      ipp_min = np.min(dipp)
  #      ipp_max = np.max(dipp)
      
    #df.to_file("state_final.geojson", driver='GeoJSON')
    
    
    return {'dist': {'d_init': dist_init, 'd': dist},
            'shares': {'d_init': shares_init, 'd': shares, 'diff': shares_diff},
            'win': {'d_init': win_init, 'd': win, 
                    'init': seats_init, 'm': seats},
            'dwaste' : {'d_init': dwaste_init, 'd': dwaste},
            'rwaste': {'d_init': rwaste_init, 'd': rwaste},
            'tout': {'d_init': tout_init, 'd': tout},
            'rho': {'init': rho_init, 'm': rho},
            'eg': {'d_init': deg_init, 'd': deg, 'diff': deg_diff,
                   'init': eg_init, 'm': eg}}
            
    #       'pp': {'init': dpp_init, 'd': dpp, 
    #              'sum': {'init': pp_sum_init, 'm': pp_sum},
    #              'min': {'init': pp_min_init, 'm': pp_min},
    #              'max': {'init': pp_max_init, 'm': pp_max}},
    #       'ipp': {'init': dipp_init, 'd': dipp, 
    #               'sum': {'init': ipp_sum_init, 'm': ipp_sum},
    #               'min': {'init': ipp_min_init, 'm': ipp_min},
    #               'max': {'init': ipp_max_init, 'm': ipp_max}},
    #        'vs': {'init': vs_init, 'm': vs},
    #        'ss': {'init': ss_init, 'm': ss},
    #        'mm': {'init': mm_init, 'm': mm},
    #        'mt': {'init': mt_init, 'm': mt}

