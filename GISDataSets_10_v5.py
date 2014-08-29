#######################################################################   
###
#  Functions - General Purpose
###
def Int2Digit(integer):
    if integer < 9:
        strInteger = "0"+str(integer)
    else:
        strInteger = str(integer)
    return strInteger

def TimeStampMaker():
    import datetime
    t = datetime.datetime.now()
    strTmonth = Int2Digit(t.month)
    strTday = Int2Digit(t.day)
    strThour = Int2Digit(t.hour)
    strTminute = Int2Digit(t.minute)
    timeStamp = str(t.year)+strTmonth+strTday+strThour+strTminute
    return timeStamp

#######################################################################   
###
#  Functions - GIS Data Set Procedures
###
def lFields(inFC):
    desc = arcpy.Describe(inFC)
    for items in desc.fields:
        print items.name
#######################################################################
def tbxPrintORI(inStr):
    '''a general purpose function for try/except printing
    inside a toolbox function'''
    try:
        arcpy.AddMessage(inStr)
    except:
        print inStr
#######################################################################
def tbxPrint(fBad,inStr):
    '''a general purpose function for try/except printing
    inside a toolbox function'''
    try:
        arcpy.AddMessage(inStr)
        #fBad.write(inStr)
    except:
        print inStr
    finally:
        fBad.write(inStr+"\n")
        
#######################################################################         
def fileOwner(inFile):
    ''' function for querying off the Active Directory owner.
    input: inFile as a fullPath
    returns: a tuple of (OwnerName, AD Domain,domain\\owner ).
         Templated from http://timgolden.me.uk/python/win32_how_do_i/get-the-owner-of-a-file.html'''
    import win32api
    import win32con
    import win32security   
    
    sd = win32security.GetFileSecurity (inFile, win32security.OWNER_SECURITY_INFORMATION)
    owner_sid = sd.GetSecurityDescriptorOwner ()
    name, domain, Filetype = win32security.LookupAccountSid (None, owner_sid)
    return name,domain,domain+'\\'+name
    
#######################################################################
#  Inventory Functions
####################################################################### 
def InventoryWSs(fullPathWS,listWSs,PathAndNameGDB,arcpy):
    ''' A function to list the workspaces
        f(fullPathWS, objListWSs,PathAndNameGDB, objArcPy) 
        returns the listWS list entry [WorkspacePath,WorkspaceType] '''
    arcpy.env.workspace = fullPathWS
    listTemp = []

    # Personal GDB
    listTemp = arcpy.ListWorkspaces("*","Access")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"PersonalGDB"])
    del listTemp

    # Coverage      
    listTemp = arcpy.ListWorkspaces("*","Coverage")
    if len(listTemp) > 0:
        for items in listTemp:
            #listWSs.append([fullPathWS+"//"+items,"Coverage"])
            listWSs.append([items,"Coverage"])
    del listTemp    

    # FileGDB
    listTemp = arcpy.ListWorkspaces("*","FileGDB")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"FileGDB"])
    del listTemp  

    # Folders: Shapefiles and Layers
    if len( arcpy.ListFiles('*.shp') ) > 0:
        listWSs.append( [fullPathWS,"Folder_Shp"] )
    if len( arcpy.ListFiles('*.lyr') ) > 0: 
        listWSs.append( [fullPathWS, "Folder_Lyr"] )
    if len( arcpy.ListRasters("*") ) > 0 :
        listWSs.append( [fullPathWS, "Folder_Raster"] )

    # SDE dB
    listTemp = arcpy.ListWorkspaces("*","SDE")
    if len(listTemp) > 0:
        for items in listTemp:
            listWSs.append([items,"SDE"])
    del listTemp 

#######################################################################    
def InventoryFCs(spot,listFCs,arcpy):
    arcpy.env.workspace = spot
    localListFCs = arcpy.ListFeatureClasses()
    for items in localListFCs:
        listFCs.append(spot+"\\"+items)
    #if ".mdb" in spot:
    #    print "personal GDB"
#######################################################################
def InventoryFDs(spot, listFDs,arcpy):
    arcpy.env.worksapce = spot
    localListFDs = arcpy.ListDatasets("","Feature")
    for items in localListFDs:
        listFDs.append(spot+"\\"+items)
#######################################################################    
def InventoryTables(spot,listTbl,arcpy):
    arcpy.env.workspace = spot
    localListTbl = arcpy.ListTables()
    for items in localListTbl:
        listTbl.append(spot+"\\"+items)
#######################################################################   
def InventoryRasters(spot,listRas,arcpy):
    arcpy.env.workspace = spot
    localListRas = arcpy.ListRasters()
    for items in localListRas:
        listRas.append(spot+"\\"+items)        
#######################################################################
def InventoryMXDs(spot,listMXD,arcpy,os):
    #arcpy.env.workspace = spot
    localListMXD= os.listdir( spot )
    for items in localListMXD:
        if ".mxd" in items:
            listMXD.append(spot+"\\"+items)        
#######################################################################
#  Write Functions
#######################################################################   
def Write_tblWorkspaceTypes(listWSs,PathAndNameGDB,arcpy,listErrors,fBad):    
    # Now - write to the tblWorkspaces
    in_dataset = PathAndNameGDB+"\\"+"tblWorkspaceTypes"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listWSs:
        row = rows.newRow()
        try:
            row.workspace = items[0]
            row.WSType = items[1]
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblWorkspaces')
            listErrors.append([items,"WorkspaceType_Error"])
        finally:
            rows.insertRow(row)
    del rows
#######################################################################   
def Write_tblWorkspaces(listWSs,PathAndNameGDB,arcpy,listErrors,fBad):    
    # Now - write to the tblWorkspaces
    in_dataset = PathAndNameGDB+"\\"+"tblWorkspaces"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listWSs:
        row = rows.newRow()
        try:
            row.workspace = items
        except:
            tbxPrint(fBad,"Workspace "+items+" does not exist or is not supported")
            listErrors.append([items,"Workspace_Error"])
        finally:
            rows.insertRow(row)
    del rows

#######################################################################   
def Write_tblRasters(listRas,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblRasters"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listRas:
        row = rows.newRow()
        try:
            print items, "-->",sys.getrefcount(None)
            
            row.FullPath = items
            row.RasterName = os.path.basename(items)
            row.workspace = os.path.dirname(items)            
            thisRaster = arcpy.Raster(items)
            row.FullPath = thisRaster.catalogPath
            row.UncompressedSize = thisRaster.uncompressedSize
            row.SpatialReference = thisRaster.spatialReference.name
            row.Raster_Format = thisRaster.format
            row.BandCount = thisRaster.bandCount
            row.PixelType = thisRaster.pixelType
            row.NumRows = thisRaster.height
            row.NumColumns = thisRaster.width
            row.CellWidth = thisRaster.meanCellWidth
            row.CellHeight = thisRaster.meanCellHeight
            row.CellValue_Min = thisRaster.minimum
            row.CellValue_Max = thisRaster.maximum
            row.CellValue_Max = thisRaster.maximum
            row.CellValue_Mean = thisRaster.mean
            row.CellValue_StDev = thisRaster.standardDeviation
        except:
            tbxPrint(fBad,"Raster "+items+" does not exist or is not supported")
            listErrors.append([items,"RasterObject_Error"])
        finally:
            rows.insertRow(row)
            
    if 'thisRaster' in locals():
        del thisRaster
    else:
        pass
    del rows

#######################################################################
def Write_tblRasters_v2(listRas,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    rowCursor = False
    
    in_dataset = PathAndNameGDB+"\\"+"tblRasters"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listRas:
        
        try:
            rowCursor = False
            row = rows.newRow()
            rowCursor = True
            #print items, "-->",sys.getrefcount(None)
            
            row.FullPath = items
            row.RasterName = os.path.basename(items)
            row.workspace = os.path.dirname(items)            
            thisRaster = arcpy.Raster(items)
            row.FullPath = thisRaster.catalogPath
            row.UncompressedSize = thisRaster.uncompressedSize
            row.SpatialReference = thisRaster.spatialReference.name
            row.Raster_Format = thisRaster.format
            row.BandCount = thisRaster.bandCount
            row.PixelType = thisRaster.pixelType
            row.NumRows = thisRaster.height
            row.NumColumns = thisRaster.width
            row.CellWidth = thisRaster.meanCellWidth
            row.CellHeight = thisRaster.meanCellHeight
            row.CellValue_Min = thisRaster.minimum
            row.CellValue_Max = thisRaster.maximum
            #row.CellValue_Max = thisRaster.maximum
            row.CellValue_Mean = thisRaster.mean
            row.CellValue_StDev = thisRaster.standardDeviation
        except:
            tbxPrint(fBad,"Raster "+items+" does not exist or is not supported")
            listErrors.append([items,"RasterObject_Error"])
        finally:
            if rowCursor:
                rows.insertRow(row)
                del row
            
    if 'thisRaster' in locals():
        del thisRaster
    else:
        pass
    del rows

#######################################################################  
def Write_tblVectors(listVect,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblVectors

    in_dataset = PathAndNameGDB+"\\"+"tblVectors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listVect:
        row = rows.newRow()
        try:
            row.FullPath = items
            thisVector = arcpy.Describe(items)           
            row.FCName = thisVector.file
            row.workspace = os.path.dirname(items)
            row.SpatialReference = thisVector.spatialReference.name
            row.Vector_DataType = thisVector.dataType
            row.NumFeatures = int(arcpy.GetCount_management(items)[0])
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblVectors')
            listErrors.append([items,"VectorObject_Error"])
        finally:
            rows.insertRow(row)
    del rows
####################################################################### 
def Write_tblErrors(listErrors,PathAndNameGDB,arcpy,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblErrors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listErrors:
        #try:
        #thisVector = arcpy.Describe(items)
        row = rows.newRow()
        try:
            row.DataSet = items[0]
            row.Workspace = os.path.dirname(items[0])
            row.DataSet_name = os.path.basename(items[0])
            row.ErrorType = items[1]
        except:
            tbxPrint(fBad,'problem with writing '+items[0]+' to tblErrors')
        finally:
            rows.insertRow(row)
    del rows
#######################################################################
def Write_tblExtentErrors(listExtErrors,PathAndNameGDB,arcpy,fBad):
    import os.path
    #pass
    # Now - write to the tblRasters

    in_dataset = PathAndNameGDB+"\\"+"tblExtentErrors"
    rows = arcpy.InsertCursor(in_dataset)

    for items in listExtErrors:
        #try:
        #thisVector = arcpy.Describe(items)
        row = rows.newRow()
        try:
            row.DataSet = items
            row.Workspace = os.path.dirname(items)
            row.DataSet_name = os.path.basename(items)
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblExtentErrors')
        finally:
            rows.insertRow(row)
    del rows
#######################################################################
def Write_tblTables(listTbl,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblTables

    in_dataset = PathAndNameGDB+"\\"+"tblTables"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listTbl:
        row = rows.newRow()
        try:
            row.FullPath = items
            row.TableName = os.path.basename(items)
            row.workspace = os.path.dirname(items)
            thisTable = arcpy.Describe(items)
            row.NumRows   = int(arcpy.GetCount_management(items)[0])
            row.TableType = thisTable.datasetType            
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblTables')
            listErrors.append([items,"Table_Error"])
        finally:
            rows.insertRow(row)
    del rows    
####################################################################### 
def Write_tblMXDs(listMXD,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblMXDs

    in_dataset = PathAndNameGDB+"\\"+"tblMXDs"
    rows = arcpy.InsertCursor(in_dataset)
    for items in listMXD:
        row = rows.newRow()
        try:
            mapDoc = arcpy.mapping.MapDocument(items)
            row.author = mapDoc.author
            row.adOwner = fileOwner(items)[2]
            row.dateSaved = mapDoc.dateSaved
            row.filepath = mapDoc.filePath
            #row.filepath = os.path.dirname(items)  <-- path to Parent Dir
            #thisTable = arcpy.Describe(items)
            row.description   = mapDoc.description
            #row.TableType = thisTable.datasetType            
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblMXDs')
            listErrors.append([items,"MXD_Error"])
        finally:
            rows.insertRow(row)
    del rows    
####################################################################### 
def Write_tblMXDs_v2(listMXD,PathAndNameGDB,arcpy,listErrors,fBad):
    import os.path
    #pass
    # Now - write to the tblMXDs
    dictMXD = {}
    
    in_dataset = PathAndNameGDB+"\\"+"tblMXDs"
    rows = arcpy.InsertCursor(in_dataset)
    
    for items in listMXD:
        row = rows.newRow()
        try:
            mapDoc = arcpy.mapping.MapDocument(items)
            row.author = mapDoc.author
            row.adOwner = fileOwner(items)[2]
            row.dateSaved = mapDoc.dateSaved
            row.filepath = mapDoc.filePath
            #row.filepath = os.path.dirname(items)  <-- path to Parent Dir
            #thisTable = arcpy.Describe(items)
            row.description   = mapDoc.description
            #row.TableType = thisTable.datasetType            
        except:
            tbxPrint(fBad,'problem with writing '+items+' to tblMXDs')
            listErrors.append([items,"MXD_Error"])
        finally:
            rows.insertRow(row)
    del rows 
####################################################################### 
def Write_tblMXDLayers(listMXD,PathAndNameGDB,arcpy,listErrors,fBad,dictMXDs):
    import os.path
    # Now - write to the tblMXDs
        
    in_dataset = PathAndNameGDB+"\\"+"tblMXDLayers"
    
    rows = arcpy.InsertCursor(in_dataset)
    
    for items in listMXD:
        #row = rows.newRow()
        try:
            mapDoc = arcpy.mapping.MapDocument(items)
            
            thisMXD = items
            listLocalLyr = []
            listLocalDF = arcpy.mapping.ListDataFrames(mapDoc)
            for DFs in listLocalDF:
                for Lyrs in arcpy.mapping.ListLayers(mapDoc,"*",DFs):
                    listLocalLyr.append( (Lyrs,DFs) )
            print "Done Makign listLocalLyr"
            for items in listLocalLyr:
                skipWrite = False
                row = rows.newRow()
                try:
                    if items[0].isGroupLayer:
                        skipWrite = True
                        pass
                    else:
                        print items
                        print items[0].longName #Testing Line
                        row.layerName = items[0].longName
                        row.SourceMXD = thisMXD
                        if thisMXD in dictMXDs:
                            row.SourceMXDGUID = dictMXDs[thisMXD]
                        else:
                            pass
                        try:
                            row.datasetName = items[0].datasetName
                        except:
                            row.datasetName = "NOT_AVAILABLE"
                        try:
                            row.dataSource = items[0].dataSource
                        except:
                            row.dataSource = "webservice_or_basemap?"
                        #row.fullPath = items[0].workspacePath+items[0].datasetName
                        row.GroupLayer = (items[0].name != items[0].longName)
                        row.DataFrameName = items[1].name
                except:
                    tbxPrint(fBad,'problem with writing MXDLayer'+items[0].longName+' to tblMXDs')
                    listErrors.append([items[0].longName,"MXDLayer_Error"])  
                    
                if skipWrite:
                    pass
                else:
                    rows.insertRow(row)
            #row.layerName = mapDoc.author
           
        except:
            tbxPrint(fBad,'problem with writing '+items[0].longName+' to tblMXDs')
            listErrors.append([items[0].longName,"MXD_Error"])
#        finally:
#            rows.insertRow(row)
    del rows    
#######################################################################
def MakeMXDGUIDDict(tblMXDs,arcpy):
    ''' Returns a dictionary of {pathMXD,GUID} '''
    dictMXDs = {}
	
    rows = arcpy.SearchCursor(tblMXDs)
    for row in rows:
        dictMXDs[row.filePath] = row.GlobalID
    
    return dictMXDs

#######################################################################
#  Write Extent
#######################################################################
def Write_vectExtentFC(listFCs,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad):
    for FCs in listFCs:
        try:
            
            Write_simpleExtent_v2(FCs,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad)
        except:
            tbxPrint(fBad, "  Problem with "+FCs+"; no Extent Generated")
            listErrors.append(FCs)            
####################################################################### 
def Write_rasExtentFC(listRas,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad):
    for Ras in listRas:
        try:
            Write_simpleRasExtent_v3(Ras,PathAndNameExtentFC,arcpy,listErrors,flagUnknownExtent,fBad)
        except:
            tbxPrint(fBad, "  Problem with "+Ras+"; no Extent Generated")
            listErrors.append(Ras)
#######################################################################

####################################################################### 
def Write_simpleRasExtent_v3(inRas,extentPoly,arcpy,listErrors,flagUnknownExtent,fBad):    
    # Feature extent
    #
    #arcpy.Delete_management("in_memory")
    import os.path
    tbxPrint(fBad,"Creating Extent for "+inRas)
    objRas = arcpy.Raster(inRas)

    extent = objRas.extent
    objSpatialRef = objRas.spatialReference
    SpatialRef = objRas.spatialReference.name

    thisRaster = objRas
    workspace = os.path.dirname(objRas.catalogPath)
    UncompressedSize = thisRaster.uncompressedSize
    SpatialReference = thisRaster.spatialReference.name
    Raster_Format = thisRaster.format
    BandCount = thisRaster.bandCount
    PixelType = thisRaster.pixelType
    NumRows = thisRaster.height
    NumColumns = thisRaster.width
    CellWidth = thisRaster.meanCellWidth
    CellHeight = thisRaster.meanCellHeight
    CellValue_Min = thisRaster.minimum
    CellValue_Max = thisRaster.maximum
    CellValue_Max = thisRaster.maximum
    CellValue_StDev = thisRaster.standardDeviation
    
    # Array to hold points
    array = arcpy.Array()
    # Create the bounding box
    array.add(extent.lowerLeft)
    array.add(extent.lowerRight)
    array.add(extent.upperRight)
    array.add(extent.upperLeft)
    # ensure the polygon is closed
    array.add(extent.lowerLeft)
    # Create the polygon object
    polygon = arcpy.Polygon(array)
    array.removeAll()

    # Insert Cursor, insert new shape
    featDesc = arcpy.Describe( extentPoly )
    srWGS84 = arcpy.Describe(extentPoly).SpatialReference

    flagAssumedSpatialRef = False
    flagAssumedProjOrGCS = ""

    if SpatialRef == "Unknown":
        if not flagUnknownExtent:
            #print "UNKNOWN FLAG"
            return # Give up on the geometry

        if extent.XMax > 180:
            tbxPrint(fBad,desc.file+" has an unknown spatial reference, but seems to be in projected units ")
            flagAssumedProjOrGCS = "Projected"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_Projected"
        else:
            tbxPrint(fBad,desc.file+" has an unknown spatial reference, but seems to be in GCS ")
            flagAssumedProjOrGCS = "GCS"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_GCS"

    cur = arcpy.InsertCursor(extentPoly, thisRaster.spatialReference )
    
    feat = cur.newRow()
    # Populate the fields
    inDesc = arcpy.Describe(extentPoly)    
    feat.setValue(inDesc.shapeFieldName,polygon)
    feat.data_model = "raster"	
    feat.spatial_ref = SpatialReference
    feat.data_type = "Raster__"+Raster_Format+"_"+str(BandCount)+"x"+PixelType
    feat.path = thisRaster.catalogPath
    feat.name = thisRaster.name
    feat.workspace = os.path.dirname(inRas)
    cur.insertRow(feat)

    del feat,cur
    del polygon
#######################################################################   
def Write_simpleExtent_v2(inFC,extentPoly,arcpy,listErrors,flagUnknownExtent,fBad):
    import os.path
    tbxPrint(fBad,"Creating Extent for "+inFC)
    #try: 
    desc = arcpy.Describe(inFC)
    extent = desc.extent
    objSpatialRef = desc.SpatialReference
    SpatialRef = desc.SpatialReference.name
    data_type = desc.shapeType+"__"+desc.featureType
    
    # Array to hold points
    array = arcpy.Array()
    # Create the bounding box
    array.add(extent.lowerLeft)
    array.add(extent.lowerRight)
    array.add(extent.upperRight)
    array.add(extent.upperLeft)
    # ensure the polygon is closed
    array.add(extent.lowerLeft)
    # Create the polygon object
    polygon = arcpy.Polygon(array)
    array.removeAll()
    
    # Insert Cursor, insert new shape
    featDesc = arcpy.Describe( extentPoly )
    srWGS84 = arcpy.Describe(extentPoly).SpatialReference

    flagAssumedSpatialRef = False
    flagAssumedProjOrGCS = ""

    if SpatialRef == "Unknown":
        if not flagUnknownExtent:
            #print "UNKNOWN FLAG"
            return # Give up on the geometry

        if extent.XMax > 180:
            tbxPrint(fBad, desc.file+" has an unknown spatial reference, but seems to be in projected units ")
            flagAssumedProjOrGCS = "Projected"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_Projected"
        else:
            tbxPrint(desc.file+" has an unknown spatial reference, but seems to be in GCS ")
            flagAssumedProjOrGCS = "GCS"
            flagAssumedSpatialRef = True
            SpatialRef = SpatialRef+"__assumed_GCS"

    cur = arcpy.InsertCursor(extentPoly, desc.SpatialReference )
    feat = cur.newRow()

    #print "here"
    inDesc = arcpy.Describe(extentPoly)    
    feat.setValue(inDesc.shapeFieldName,polygon)

    
    feat.path = inFC
    feat.workspace = os.path.dirname(inFC)
    feat.spatial_ref = SpatialRef
    feat.data_type = data_type
    feat.data_model = "vector"
    feat.name = desc.file


    cur.insertRow(feat)

    del feat,cur
    del polygon
#######################################################################   

