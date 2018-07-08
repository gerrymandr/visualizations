#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 11:00:14 2018

@author: hannah
"""
from qgis.utils import iface
from PyQt4.QtCore import QVariant
import numpy
import csv

# Replace the values below with values from your layer.
# For example, if your identifier field is called 'XYZ', then change the line
# below to _NAME_FIELD = 'XYZ'
LAYER_NAME = "Lowell_Blocks"
FILEPATH='./Lowell/'
_NAME_FIELD = 'BLOCKID10'
_NEIGHBORS_FIELD = 'NEIGHBORS'
_POP_FIELDS = {'tot_pop': 'mass_census_blocks_2010_POP_2010_TOT', 'white' : 'mass_census_blocks_2010_POP_WHITE' , 'black' : 'mass_census_blocks_2010_POP_BLACK' , 'asian' : 'mass_census_blocks_2010_POP_ASN'}
ADJ_LAYER_NAME = LAYER_NAME+"_Adj"

# choose a layer
layers = qgis.utils.iface.legendInterface().layers()
for layerQ in layers:
    if layerQ.name() == LAYER_NAME:
        layer=layerQ

#start editing layer
layer.startEditing()
if not _NEIGHBORS_FIELD in [field.name() for field in layer.pendingFields()]:
    layer.dataProvider().addAttributes([QgsField(_NEIGHBORS_FIELD, QVariant.String),])
    layer.updateFields()
    
## Create a dictionary of all nodes
nodes = [node for node in layer.getFeatures()]
map = {node.id(): node for node in nodes}


# Build a spatial index
index = QgsSpatialIndex()
for node in nodes:
    index.insertFeature(node)

# create a new memory layer
v_layer = QgsVectorLayer("LineString", ADJ_LAYER_NAME, "memory")
pr = v_layer.dataProvider()
for node in nodes:
    geom = node.geometry()
    rad = numpy.sqrt(geom.area())/5
    start_pt = geom.centroid().asPoint()
    # Find all features that intersect the bounding box of the current feature.
    # We use spatial index to find the features intersecting the bounding box
    # of the current feature. This will narrow down the features that we need
    # to check neighboring features.
    neighbor_ids = index.intersects(geom.buffer(rad,2).boundingBox())
    # Initalize neighbors list and sum
    edges = []
    neighbors = []
    for id in neighbor_ids:
        # Look up the feature from the dictionary
        neighbor = map[id]
        neighborhood = neighbor.geometry().buffer(rad,2)

        # For our purpose we consider a feature as 'neighbor' if it touches or
        # intersects a feature. We use the 'disjoint' predicate to satisfy
        # these conditions. So if a feature is not disjoint, it is a neighbor.
        #if (f != intersecting_f and myAdj(intersecting_f.geometry(),geom)):
        if (node != neighbor and neighborhood.intersects(geom)):
            neighbors.append(int(neighbor[_NAME_FIELD]))
            edges.append([int(node[_NAME_FIELD]),int(neighbor[_NAME_FIELD])])
            end_pt=neighbor.geometry().centroid().asPoint()
            edge=QgsGeometry.fromPolyline([start_pt,end_pt])
            # create a new feature
            seg = QgsFeature()
            # add the geometry to the feature, 
            seg.setGeometry(edge)
            # ...it was here that you can add attributes, after having defined....
            # add the geometry to the layer
            pr.addFeatures( [ seg ] )
            # update extent of the layer (not necessary)
            v_layer.updateExtents()
    node[_NEIGHBORS_FIELD] = ','.join(str(x) for x in neighbors)
    #_NEIGHBORS_FIELD.append(neighbors)
    # Update the layer with new attribute values.
    layer.updateFeature(node)
layer.commitChanges()
print ('Processing complete.')

QgsMapLayerRegistry.instance().addMapLayers([v_layer])
