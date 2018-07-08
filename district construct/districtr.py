# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:24:07 2018

@author: eion, anna, assaf
"""
import os
import geopandas as gpd
import pandas as pd
import us
import numpy as np
import shapely
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, LassoSelector
from matplotlib.path import Path
import matplotlib.patheffects as path_effects
from descartes import PolygonPatch
pd.options.mode.chained_assignment = None  # default='warn'

data_folder = 'Sample_Data'
counties_shp = os.path.join(data_folder, "tl_2012_13_vtd10/tl_2012_13_vtd10.shp") # GA VTDs
#counties_shp = os.path.join(data_folder, "tl_2012_13_cousub/tl_2012_13_cousub.shp") # GA county sub
#counties_shp = os.path.join(data_folder, "tl_2012_us_county/tl_2012_ga_county.shp") # GA counties
df_cells = gpd.read_file(counties_shp)
#df_cells = gpd.read_file('tl_2016_08_cousub/tl_2016_08_cousub.shp')
#df_vtds = gpd.read_file(os.path.join(data_folder, "MO_data/mo_cleaned_vtds.shp"))
##DistrictConstruct(df_vtds,8,"shape_key.csv",statefp_name='STATEFP10',geoid_name='GEOID10')

class SelectFromCollection(object):
    """Use the lasso selector tool."""
    def __init__(self, ax, collection, alpha_other=0.3):
        """The lasso."""
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other
        self.xys = collection.get_offsets()
        self.fcl = collection.get_facecolors()
        if not self.fcl.any():
            raise ValueError('Collection must have a facecolor')
        elif len(self.fcl) == 1:
            self.fcl = np.tile(self.fcl, (len(self.xys), 1))
        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, verts):
        """Begin lasso."""
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fcl[:, -1] = self.alpha_other
        self.fcl[self.ind, -1] = 1
        self.collection.set_facecolors(self.fcl)
        self.canvas.draw_idle()

    def disconnect(self):
        """End lasso."""
        self.lasso.disconnect_events()
        self.fcl[:, -1] = 1
        self.collection.set_facecolors(self.fcl)
        self.canvas.draw_idle()


class Districtr:
    """Build map with visual for districting plan construction."""
    def __init__(self, df, count, starter='', measure='pp',
                 export_name='key.csv', cd_col_name='CD',
                 geoid_name='GEOID', statefp_name='STATEFP'):
        """
        Keyword arguments:
        df -- the dataframe of census cells
        count -- the count of districts to be drawn
        starter -- the file name of plan to be imported (default '')
        measure -- the compactness score to be used. 'pp' for Polsby-Popper,
                    'ch' for Convex-Hull (default 'pp')
        export_name -- the file name of plan to exported (default 'key.csv')
        cd_col_name -- the column name of districts in Shapefile (default 'CD')
        geoid_name -- the column name of geoID in Shapefile (default 'GEOID')
        statefp_name -- the column name of state FIPS code in Shapefile (default 'STATEFP')
        """
        self.df = df
        self.dim = len(df)
        self.count = count
        self.district_dict = {}
        self.measure = measure
        self.nomen = {'export':export_name,
                      'cd_col':cd_col_name,
                      'geoid':geoid_name,
                      'statefp':statefp_name}
        self.current_district = 1
        self.scores_dict = {}
        self.worst = [0, 1.000]
        self.patches_dict = {}

        fig, axs = plt.subplots(figsize=(10, 10))
        self.axs = fig.gca()
        self.fig = fig
        plt.title(str(us.states.lookup(str(df[self.nomen['statefp']][0]))),
                  fontsize=25,
                  fontweight='bold',
                  family='cursive')
        colors = np.linspace(0.0, 1.0, self.count+1)
        self.rgb = cm.get_cmap(plt.get_cmap('gist_rainbow'))(colors)[np.newaxis, :, :3]
        self.rgb[0][0] = [0.6, 0.6, 0.6]
        self.txt1 = axs.text(0.0, -.02,
                             'Current District:',
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        self.txt2 = axs.text(0.3, -.02,
                             str(self.current_district),
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12,
                             color=self.rgb[0][self.current_district],
                             fontweight='extra bold')
        self.txt2.set_path_effects([path_effects.Stroke(linewidth=1, foreground='black'),
                                    path_effects.Normal()])
        self.txt3 = axs.text(0.4, -.02,
                             'Current Score:   ',
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        self.txt4 = axs.text(0.7, -.02,
                             '0.00000',
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        self.txt5 = axs.text(0.0, -.07,
                             'Worst District:',
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        self.txt6 = axs.text(0.3, -.07,
                             str(self.worst[0]),
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12,
                             color='#D3D3D3',
                             fontweight='extra bold')
        self.txt6.set_path_effects([path_effects.Stroke(linewidth=1, foreground='black'),
                                    path_effects.Normal()])
        self.txt7 = axs.text(0.4, -.07,
                             'Worst Score:',
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        self.txt8 = axs.text(0.7, -.07,
                             str(self.worst[1]),
                             ha='left',
                             va='center',
                             transform=axs.transAxes,
                             fontsize=12)
        plt.axis('off')

        self.scores_dict['0'] = set()
        for dist in range(1, self.count+1):
            self.district_dict[str(dist)] = set()
            self.scores_dict[str(dist)] = 0.00000
            self.scores_dict['0'].add(dist)
        if starter:
            self.import_plan(starter)
        for index in range(self.dim):
            poly = self.df['geometry'][index]
            dist = self.get_district(index)
            patch = PolygonPatch(poly,
                                 fc=self.rgb[0][dist],
                                 ec=self.rgb[0][dist],
                                 alpha=0.3,
                                 zorder=2)
            self.patches_dict.update({index: patch})
            self.axs.add_patch(self.patches_dict[index])
        self.update_scores()

        self.axexport_plan = plt.axes([0.75, 0.920, 0.20, 0.05])
        self.bexport_plan = Button(self.axexport_plan,
                                   'Export Plan',
                                   color='mistyrose')
        self.bexport_plan.on_clicked(self.export_plan)
        fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.axlasso_plan = plt.axes([0.75, 0.865, 0.20, 0.05])
        self.blasso_plan = Button(self.axlasso_plan,
                                  'Lasso (+ \'Enter\')',
                                  color='lightcyan')
        self.blasso_plan.on_clicked(self.lasso_map)
        fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.axdistrict_toggle = plt.axes([0.75, 0.075, 0.20, 0.05])
        self.bdistrict_toggle = Button(self.axdistrict_toggle,
                                       'District Toggle',
                                       color='lemonchiffon')
        self.bdistrict_toggle.on_clicked(self.toggle_district)
        fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.axupdate_scores = plt.axes([0.75, 0.020, 0.20, 0.05])
        self.bupdate_scores = Button(self.axupdate_scores,
                                     'Update Scores',
                                     color='honeydew')
        self.bupdate_scores.on_clicked(self.update_scores)
        fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.axs.axis('scaled')
        plt.show()


    def onclick(self, event):
        """Change map and update text on mouseclick."""
        self.change_district(np.array([event.xdata, event.ydata]))
        self.update_text()

    def import_plan(self, starter):
        """Import a pre-existing districting plan.

        Keyword arguments:
        starter -- the file name of plan to be imported
        """
        print('Importing plan...')
        key = pd.read_csv(starter,
                          delimiter=',',
                          dtype={self.nomen['geoid']:object,
                                 self.nomen['cd_col']:object})
        if self.nomen['cd_col'] in self.df.columns:
            df_key = pd.merge(self.df,
                              key,
                              how='left',
                              on=[self.nomen['geoid'],
                                  self.nomen['cd_col']])
        else:
            df_key = pd.merge(self.df,
                              key,
                              how='left',
                              on=[self.nomen['geoid']])
        df_key[self.nomen['cd_col']] = pd.to_numeric(df_key[self.nomen['cd_col']]).astype(int)
        for index in range(self.dim):
            dist = df_key.loc[index][self.nomen['cd_col']]
            if dist != 0 and dist <= self.count:
                self.district_dict[str(dist)].add(index)

    def export_plan(self, event):
        """Export the current districting plan."""
        print('\nExporting plan...')
        df_key = self.df[[self.nomen['statefp'],
                          self.nomen['geoid']]]
        df_key[self.nomen['cd_col']] = '00'
        for index in range(self.dim):
            df_key.loc[index, self.nomen['cd_col']] = str(self.get_district(index)).zfill(2)
        df_key[[self.nomen['geoid'], self.nomen['cd_col']]].to_csv(self.nomen['export'])
        return df_key

    def lasso_map(self, event):
        """Use a lasso to change multiple cells at once."""
        centroids = self.df.centroid
        pts = [shapely.geometry.Point(pt) for pt in list(zip(centroids.loc[0:].x,
                                                             centroids.loc[0:].y))]
        pts = list(zip(centroids.loc[0:].x, centroids.loc[0:].y))
        cell_cents = self.axs.scatter(*zip(*pts))
        selector = SelectFromCollection(self.axs, cell_cents)
        def accept(event):
            """Define if lasso is valid."""
            if selector.xys.any():
                if event.key == "enter":
                    for cell_loc in selector.xys[selector.ind]:
                        self.change_district(cell_loc)
                selector.xys = []
                selector.disconnect()
                self.fig.canvas.draw()
                cell_cents.remove()
        if selector.xys.any():
            self.fig.canvas.mpl_connect("key_press_event", accept)
        plt.show()

    def toggle_district(self, event):
        """Iterate through districts to manipulate."""
        self.current_district = (self.current_district % self.count) + 1
        self.txt2.set_text(str(self.current_district))
        self.txt2.set_color(self.rgb[0][self.current_district])
        self.txt4.set_text(str(format(self.scores_dict[str(self.current_district)], '.5f')))

    def compute_score(self, dist):
        """Compute the compactness score of desired district.

        Keyword arguments:
        dist -- the number of the district
        """
        df_dist = self.df[list_from_set(self.district_dict[str(dist)], self.dim)]
        if df_dist.empty:
            return 0.00000
        district = df_dist.dissolve(self.nomen['statefp'])
        if self.measure == 'ch': # Convex-Hull
            score = district.iloc[0].geometry.area / district.iloc[0].geometry.convex_hull.area
#        elif self.measure == 'rk': # Reock
#            circ = district.iloc[0].geometry.convex_hull.apply(lambda x: pi * make_circle(list(x.exterior.coords))[2] ** 2)
#            score = district.iloc[0].geometry.area / circ.area
        else: # Polsby-Popper
            score = 4*np.pi * district.iloc[0].geometry.area / (district.iloc[0].geometry.length)**2
        self.scores_dict[str(dist)] = score
        if score < self.worst[1] and score != 0:
            self.worst[0] = dist
            self.worst[1] = score
        return score

    def update_scores(self, event=''):
        """Update compactness scores which have changed and update worst district/score."""
        for dist in self.scores_dict['0']:
            self.scores_dict[str(dist)] = self.compute_score(dist)
        self.worst = [0, 1]
        for dist in range(1, self.count+1):
            score = self.scores_dict[str(dist)]
            if score < self.worst[1] and score != 0:
                self.worst = [dist, score]
        self.scores_dict['0'] = set()
        self.update_text()

    def update_text(self):
        """Update text in UI."""
        self.txt4.set_text(str(format(self.scores_dict[str(self.current_district)], '.5f')))
        self.txt6.set_text(str(self.worst[0]))
        self.txt6.set_color(self.rgb[0][self.worst[0]])
        self.txt8.set_text(str(format(self.worst[1], '.5f')))
        plt.draw()

    def get_district(self, index):
        """Find to which district a given census cell belongs.

        Keyword arguments:
        index -- the row index from the input dataframe of desired census cell
        """
        for dist in range(1, self.count+1):
            if index in self.district_dict[str(dist)]:
                return dist
        return 0

    def change_district(self, coords):
        """Handle a cell selection on map."""
        [lat, lon] = coords[0:2]
        point = shapely.geometry.Point(lat, lon)
        for index in range(self.dim):
            if point.within(self.df['geometry'][index]):
                if self.get_district(index) == self.current_district:
                    self.update_map(index, 0)
                else:
                    self.update_map(index, self.current_district)
                return

    def update_map(self, index, new_dist):
        """Update the plan map and attributes.

        Keyword arguments:
        index -- the row index from the input dataframe of desired census cell
        new_dist -- the district to which the census cell will be assigned
        """
        old_dist = self.get_district(index)
        if old_dist != 0:
            self.district_dict[str(old_dist)].remove(index)
            self.scores_dict['0'].add(old_dist)
        if new_dist != 0:
            self.district_dict[str(new_dist)].add(index)
            self.scores_dict['0'].add(new_dist)
        self.patches_dict[index].remove()
        poly = self.df['geometry'][index]
        new_patch = PolygonPatch(poly,
                                 fc=self.rgb[0][new_dist],
                                 ec=self.rgb[0][new_dist],
                                 alpha=0.3,
                                 zorder=2)
        self.patches_dict[index] = new_patch
        self.axs.add_patch(self.patches_dict[index])
        plt.draw()

def list_from_set(myset, length):
    """Filter pertinent entries with booleans"""
    mylist = [False] * length
    for i in myset:
        mylist[i] = True
    return mylist

def plan_to_shapefile(plan, shp, geoid_name='GEOID', cd_col_name='CD'):
    """Combine saved districting plan with Shapefile as a column"""
    key = pd.read_csv(plan,
                      delimiter=',',
                      dtype={geoid_name: object,
                             cd_col_name: object})
    cells = gpd.read_file(shp)
    if cd_col_name in cells.columns:
        df_key = pd.merge(cells,
                          key,
                          how='left',
                          on=[geoid_name,
                              cd_col_name])
    else:
        df_key = pd.merge(cells,
                          key,
                          how='left',
                          on=[geoid_name])
    df_key.to_file(str('key_' + shp))
    return df_key

def shapefile_to_key(shp, geoid_name='GEOID', cd_col_name='CD', key_name='shape_key.csv'):
    """Extract districting plan from column of Shapefile"""
    df = gpd.read_file(shp)
    df[[geoid_name, cd_col_name]].to_csv(key_name)

#shapefile_to_key("Sample_Data/MO_data/mo_cleaned_vtds.shp",geoid_name='GEOID10')
