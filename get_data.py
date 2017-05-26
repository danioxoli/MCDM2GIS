# -*- coding: utf-8 -*-

import os
import csv 
from osgeo import ogr

# Settings
myfold = r"/home/monia/Desktop/TEST/"

# Read shapefile with OGR
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(myfold+"grid/grid.shp", 0) # 0 means read-only. 1 means writeable.
layer = dataSource.GetLayer()
   
#initialize grid by adding pixel id and coordinates
grid = []
for feature in layer:
    geom = feature.GetGeometryRef()
    coords = geom.Centroid().GetPoint_2D()
    fid = feature.GetField('ID')
    grid.append(["ID%s"%fid,coords])


#Get Categories and Sub-categories
tree = {}
#keys=[]#####MIRIAM ho aggiunto la lista 
for f in os.listdir(myfold+"categories"):
    tree[f]={}
    #keys.append(f)#####MIRIAM ho aggiunto la lista delle categorie 
    for item in os.listdir(myfold+"categories/"+f):
        tree[f][item]={}

        
# Get Objects

list_val=[]
for f in tree.keys():
    for item in tree[f].keys():
        for mod in ['cy.csv','dr.csv','wa.csv']:
            x = open(myfold+"categories/"+f+"/"+item+"/"+mod, 'rb')
            reader = csv.reader(x)
            data = (list(list(rec) for rec in csv.reader(x, delimiter=',')))[1::]
            for v in data:
                pixel = "ID%s"%v[0]
                val = sorted(map(float, v[1::]))[0:3]
                sum_val =sum(map(float, v[1::]))
                list_val.append([pixel,sorted(map(float, v[1::]))[0],sorted(map(float, v[1::]))[1],sorted(map(float, v[1::]))[2],sum_val]) 
                tree[f][item][mod] = list_val
            list_val=[]
            
f = open(myfold+"RoutingData.py","w")
f.write("tree="+str(tree))
f.close()
    

