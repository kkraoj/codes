# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 00:17:08 2017

@author: kkrao
"""
from __future__ import division
import arcpy
import os
from dirs import MyDir, Dir_CA
import pandas as pd
import numpy as np
from arcpy.sa import ZonalStatisticsAsTable
os.chdir(MyDir+'/Elevation/')
#arcpy.env.overwriteOutput=True
#inZoneData = Dir_CA+"/grid.shp"
#zoneField = "gridID"
#inRaster='canopy_height.tif'
#outTable='canopy_height_stats.gdb/stats'
#arcpy.CheckOutExtension('Spatial')
#outZSaT = ZonalStatisticsAsTable(inZoneData, zoneField, inRaster, outTable,"DATA","MEAN")
#arcpy.CheckInExtension('Spatial')
####---------------------------------------------------------------------------
## make Df
year_range=range(2005,2016)
arcpy.env.workspace=MyDir+'/Elevation/'
nos=370
scale=1.0
store = pd.HDFStore(Dir_CA+'/data.h5') 
for data_type in ['aspect','elevation']:
    for quantity in ['MEAN','STD']:
        data=pd.DataFrame(np.full((11,nos),np.NaN), \
                           index=[pd.to_datetime(year_range,format='%Y')],\
                                 columns=range(nos))
        fname='elevation.gdb/%s_stats'%data_type
        if  arcpy.Exists(fname):
            cursor = arcpy.SearchCursor(fname)
            for row in cursor:
                data.iloc[:,row.getValue('gridID')]=row.getValue(quantity)*scale               
        Df=data
        Df=Df.rename_axis('gridID',axis='columns')
        Df.index.name='%s_%s'%(data_type,quantity.lower())  
        store[Df.index.name] = Df 
store.close()     

