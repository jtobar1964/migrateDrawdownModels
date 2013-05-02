#!/usr/local/bin/python
# =========================================================================================
# Script : migrateWDL.py
# -----------------------------------------------------------------------------------------
# Purpose : This script migrates grids and shapefiles created by Drawdown into a File
#           Geodatabase
# -----------------------------------------------------------------------------------------
# Suppliment Info:
# -----------------------------------------------------------------------------------------
# Supervisor : Juan Tobar, Regulatio GIS, SFWMD, (561)682-6687
# Create date: 29 April 2013
#------------------------------------------------------------------------------------------

# Import system modules
import sys
import os
import arcpy
import time
import re
from arcpy import env

# set variables
inFolder = '//ad.sfwmd.gov/dfsroot/data/err_gis/applications/prd/cs/reggss/dataSystem/wdl/'
outFolder = 'C:/Workspace/'

def listFolders(folder):
    return [d for d in os.listdir(folder) if os.path.isdir(os.path.join(folder, d))]

def listFiles(folder):
    # grids created with ArcGIS v9.1 or lower do not have *.aux.xml files
    # ArcGIS v10.1 requires *aux.xml files in order to copy to fgdb
    # this code returns the *.aux.xml files in a directory
    return [f for f in os.listdir(folder) if re.search('xml', f)]

def main():
    # create a list of folders to turn into fgdbs
    listAppFolders = list(listFolders('%s' %inFolder))
    listAppFolders.sort()
    
    for fgdb in listAppFolders:
        env.workspace = '%s/%s' %(inFolder, fgdb)
        # get a list ofthe grids
        rasterList = arcpy.ListRasters("*", "GRID")
        # get a list of the contours
        shapeList = arcpy.ListFeatureClasses()

        # create a list of *.xml files in the directory
        fileList = list(listFiles('%s%s' %(inFolder, fgdb)))               

        # making sure this is not an empty folder
        if len(rasterList) >= 1 or len(shapeList) >= 1:
            # in case the program fails and we have to restart dont over-write
            if not os.path.isdir('%s%s.gdb' %(outFolder, fgdb)):
                arcpy.CreateFileGDB_management("C:/Workspace", fgdb, "10.0")

                # process the grids
                for raster in rasterList:
                    # make a nice name for the inRaster
                    inRaster = inFolder + fgdb + "/" + raster

                    # make a nice name for the outRaster
                    # convert dashes to underscores 
                    outRaster = outFolder + fgdb + ".gdb/g" + raster.replace("-", "_")
                    
                    for file in fileList:
                        # if the raster does not have a matching aux.xml calculate statistics
                        if not re.match(file, '%s.aux.xml' %fgdb):
                            arcpy.CalculateStatistics_management(inRaster) 

                    # CopyRaster exception fixed by sleep
                    # it takes longer but corrects the exception most of the time
                    time.sleep(2)
                    arcpy.CopyRaster_management('%s' %(inRaster), '%s' %(outRaster))
                
                # process the contours
                for contour in shapeList:
                    inShapefile = inFolder + fgdb + "/" + contour

                    # convert dashes to underscores
                    outShapefile = outFolder + fgdb + ".gdb/" + contour.replace(".shp", "").replace("-", "_")

                    # CopyFeature exception fixed by sleep
                    # it takes longer but corrects the exception most of the time
                    time.sleep(2)
                    arcpy.CopyFeatures_management('%s' %(inShapefile), '%s' %(outShapefile))

try:
    main()
    
except NameError, e:
    print e