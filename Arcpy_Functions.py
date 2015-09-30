def MaskBelowZero(inputRas):
    '''   Produces a masked output for any input raster 
    '''
    import arcpy
    
    oldWS = arcpy.env.workspace
    inRas = arcpy.Raster(inputRas)
    
    arcpy.env.snapRaster = inRas
    arcpy.env.workspace = "in_memory"
    arcpy.env.extent = inRas
    
    rasMask = inRas > 0.
    
    arcpy.env.workspace = oldWS
    newFN = inputRas + "_GT0"
    rasOut = inRas * rasMask
    rasOut.save(newFN)
    
    mxd = arcpy.mapping.MapDocument("CURRENT")
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0] 
    newFNP = rasOut.path+newFN
    print newFNP
    addLayer = arcpy.mapping.Layer(newFNP)
    arcpy.mapping.AddLayer(dataFrame, addLayer)
    
 def MaskBelow_N(inputRas, num = 0.0, inputKeepSign = "GT" ):
    '''   Produces a masked output for any input raster 
             >  takes inputRas (Raster Layer from TOC)
             >  takes num (floating point cut off values
             >  takes inputKeepSign : "GT" or "LT"
    '''
    import arcpy
    
    oldWS = arcpy.env.workspace
    inRas = arcpy.Raster(inputRas)
    
    arcpy.env.snapRaster = inRas
    arcpy.env.workspace = "in_memory"
    arcpy.env.extent = inRas
    
    try:
        if inputKeepSign == "LT":  rasMask = inRas < num
        else:  rasMask = inRas > num
    except:
        raise

    
    arcpy.env.workspace = oldWS
    newFN = inputRas + "_GT0"
    rasOut = inRas * rasMask
    rasOut.save(newFN)
    
    mxd = arcpy.mapping.MapDocument("CURRENT")
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0] 
    newFNP = rasOut.path+newFN
    print newFNP
    addLayer = arcpy.mapping.Layer(newFNP)
    arcpy.mapping.AddLayer(dataFrame, addLayer)