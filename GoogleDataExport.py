""" This tool will connect to Google Places & seearch a specific location
provided by the user for POI (of types selected by user from a list)
It will get the information of each alongside the location & create
features of thge locations. The features are stored in Feature Classes
in a Geodatabase, or in SHP files

GIS Programming Course Final Project by Mahdi Al Qateefi, 2016, Dec 6
Developed by : Mahdi AL Qateefi
mahdiswe@gmail.com
Instructor: Dr. Brian Chastain



 Copyright (C) <2016>  <Mahdi Al Qateefi>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
__author__ = "Mahdi Al Qateefi <mia150330@utdallas.edu>"

import json
import urllib.request
import socket
import arcpy
import os
import time
from tkinter import *
from tkinter.simpledialog import *
from tkinter.messagebox import *
from tkinter import filedialog
from tkinter.filedialog import *
from tkinter import messagebox
from tkinter import simpledialog


''' getLocations_json() will get the json of all locations of a specific type.
    Variable "type" must be a single string value
    Each type is called with a new URL request to accommodate the upcoming
    change in Google Places API ('types' parameter is deprecated
    thus each call to this method is for one type only

    requestPart#1 = "https://maps.googleapis.com/maps/api/place/nearbysearch/"
    + "json?location="
    requestPart#2 = location_Y + "," + location_X
    requestPart#3 = "&radius="
    requestPart#4 = radius
    requestPart#5 = "&type="
    requestPart#6 = types[i]
    requestPart#7 = "&key=" + googleKey
    '''


'''Variables:
'''
root = None # GUI root
googleKey = ""
typesList = list()  # All types
checkbuttons_vars = list()  # values of selection
selectedTypes = list() # selected of the types
createSHP_var = None
createGDB_var = None
duplicatesFromGDB_var = None
outGDB_url = "Not selected"
txt_outName = None # The text field for fc name
txt_locX, txt_locY, txt_raduis = None, None, None  # txt field for X & Y & radius
createdFcToFix = None # Used to store the fc url after creating the fc to remove its duplicates

'''Fonts
'''
header1_font = ("Times", "14", "bold")
desc_font = ("Times", "10", "bold italic")
title_font = ("Times", "15", "bold")

def getLocations_json(poiType, location_X, location_Y, radius):
    global googleKey
    try:
        request ="https://maps.googleapis.com/maps/api/place/nearbysearch/j" \
                 "son?location=" + location_Y + "," + location_X +\
                 "&radius=" + radius + "&type=" + poiType + "&key=" +\
                 googleKey
        response = urllib.request.urlopen(request)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        #print(data)
        ''' Data got under data.result:
            - name (str)
            - types
            - location:
                -lat (float)
                -lng (float)
        '''
        return data
    except urllib.error.URLError as e:
        print('\nERROR Occurred: %r' % e)
    except socket.timeout as e:
        print('\nERROR Occurred#2: %r' % e)


def getLocations(types, loc_x, loc_y, radius, fcName):
    if len(types) > 0:
        # Get user selection for data export type (shp, GDB)
        global createGDB_var
        global createSHP_var
        global outGDB_url
        if int(createGDB_var.get()) == 1:
            outGDB_url = filedialog.askdirectory(title="Select the GDB to st"
                                                       "ore the Feature "
                                                       "Class in")
            if arcpy.Exists(outGDB_url) and ".gdb" in outGDB_url:
                setCursorBusy()
                # Create the fc in GDB
                fc = fcName
                mySpatialRef = arcpy.SpatialReference(4326)
                arcpy.env.workspace = outGDB_url
                print(arcpy.env.workspace)
                arcpy.CreateFeatureclass_management(arcpy.env.workspace, fc,
                                                    "Point",
                                                    "", "", "", mySpatialRef)
                arcpy.AddField_management(fc, "Name", "TEXT")
                arcpy.AddField_management(fc, "Type", "TEXT")

                insrtCursor = arcpy.da.InsertCursor(fc, ["Name", "Type", "SHAPE@"])

                print("Types available are: ")
                for t in types:
                    print("type: " + t)
                    # Get the json for the type
                    jsonData = getLocations_json(t, loc_x, loc_y, radius)

                    # iterate over each result in json
                    for store in jsonData["results"]:
                        # store the result
                        name = str(store["name"])
                        lat = store["geometry"]["location"]["lat"]
                        long = float(store["geometry"]["location"]["lng"])
                        point = arcpy.Point(long, lat)

                        insrtCursor.insertRow((name, t, point))

                del insrtCursor
                print("DONE Creating GDB Data")
                # Clean it from duplicates
                removeDuplicates_fromCreate(arcpy.env.workspace + "/" + fc)
                # Create buffer to know area
                createBuffer(arcpy.env.workspace + "/" + fc, loc_x, loc_y,
                             radius)
                notbusy()
            else:
                print("ERROR: The selected GDB is probably incorrect!")

        if int(createSHP_var.get()) == 1:
            setCursorBusy()
            # Create the SHP
            fc = "out_" + fcName + ".shp"
            mySpatialRef = arcpy.SpatialReference(4326)
            arcpy.env.workspace = os.getcwd() + r"\out"
            print(arcpy.env.workspace)
            arcpy.CreateFeatureclass_management(arcpy.env.workspace, fc,
                                                "Point",
                                                "", "", "", mySpatialRef)
            arcpy.AddField_management(fc, "Name", "TEXT")
            arcpy.AddField_management(fc, "Type", "TEXT")

            insrtCursor = arcpy.da.InsertCursor(fc, ["Name", "Type", "SHAPE@"])

            print("Types available are: ")
            for t in types:
                print("type: " + t)
                # Get the json for the type
                jsonData = getLocations_json(t, loc_x, loc_y, radius)

                # iterate over each result in json
                for store in jsonData["results"]:
                    # store the result
                    name = str(store["name"])
                    # print("Name: " + name)
                    # print("Location:")
                    lat = store["geometry"]["location"]["lat"]
                    # print("Lat: " + str(lat))
                    long = float(store["geometry"]["location"]["lng"])
                    # print("Long: " + str(long))
                    # print("Type: " + t)
                    point = arcpy.Point(long, lat)

                    insrtCursor.insertRow((name, t, point))

            del insrtCursor
            print("DONE Creating .shp Data")
            # Clean it from duplicates
            removeDuplicates_fromCreate(arcpy.env.workspace + "\\" + fc)
            # Create buffer to know area
            createBuffer(arcpy.env.workspace + "\\" + fc, loc_x, loc_y, radius)

    else:
        print("No Types are selected!")

    notbusy()
    messagebox.showinfo("Done", "Process is Done")


def about():
    imprtntNote = "\n\nImportant Notes:\n\t1. This tool is developed using " \
                  "arcpy python module, thus ArcGIS Pro is needed. It stil" \
                  "l could work with certain versions of ArcGIS Desktop, " \
                  "but it was not tested nor designed to.\n\t2. When usi" \
                  "ng 'Duplicate Data Rem" \
                  "oval Tool' you must make sure that the target data " \
                  "to be cleaned is NOT in a folder that auto-sync (s" \
                  "uch as Google Drive or Dropbox) as this will cause " \
                  "locks over the file & will break the process."
    messagebox.showinfo("About", "This tool will export the stores of the se"
                                 "lected types into .shp file or a feature cl"
                                 "ass in a GDB\n\nDeveloped By:\n\tMahdi Al Q"
                                 "ateefi\n\tmahdiswe@gmail.com" + imprtntNote)

def createBuffer(fc, x, y, rad):
    print("Creating Search Area polygon")
    buffTargetName = fc
    mySRef = arcpy.SpatialReference(4326)

    myPoint = arcpy.PointGeometry(arcpy.Point(x, y), mySRef)
    # use x & y & r to create a buffer
    if ".shp" in fc:
        buffTargetName = fc.rstrip(".shp") + "_SearchArea.shp"
    else:
        buffTargetName = buffTargetName + "_SearchArea"

    arcpy.Buffer_analysis(myPoint, buffTargetName, rad + " meters")


def selectAllTypes():
    global checkbuttons_vars
    for v in checkbuttons_vars:
        v.set(1)

def selectNoneTypes():
    global checkbuttons_vars
    for v in checkbuttons_vars:
        v.set(0)

def startUI(types):
    global root
    root = Tk(className=" Google Data Export Tool - by Mahdi Al Qateefi")
    appIcon = Image("photo", file="resource\\icon.png")
    root.call('wm', 'iconphoto', root._w, appIcon)

    typesColor = "gainsboro"

    global header1_font
    global desc_font
    global title_font

    f1_frame = Frame(root, bd=3, bg=typesColor, relief=GROOVE)
    f2_frame = Frame(root, bd=3, relief=GROOVE) # RIDGE
    f10_frame = Frame(f1_frame, bg=typesColor)
    f11_frame = Frame(f1_frame, bg=typesColor)
    f12_frame = Frame(f1_frame, bg=typesColor)
    f13_frame = Frame(f1_frame, bg=typesColor)
    f14_frame = Frame(f1_frame, bg=typesColor)
    f15_frame = Frame(f1_frame, bg=typesColor)
    f21_frame = Frame(f2_frame)
    f211_frame = Frame(f21_frame)
    f2111_frame = Frame(f211_frame)
    f2112_frame = Frame(f211_frame)
    f22_frame = Frame(f2_frame)
    f212_frame = Frame(f21_frame, bd=4, relief=RAISED)
    f221_frame = Frame(f21_frame)
    f222_frame = Frame(f21_frame)
    f2221_frame = Frame(f222_frame)
    f2222_frame = Frame(f222_frame)


    label_outName = Label(f2221_frame, text="Export File Name: ")
    label_outName.pack(side=LEFT)
    global txt_outName
    txt_outName = Entry(f2221_frame)
    txt_outName.pack(side=LEFT)
    space_label = Label(f2221_frame, text=" ")
    space_label.pack(side=LEFT)

    button_extract = Button(f2222_frame, text="Extract Data", width=20, command=getSelectedTypes)
    button_extract.pack(side=TOP, fill=X, expand=True)


    space_label2 = Label(f2222_frame, text=" ")
    space_label2.pack(side=TOP)



    label_types = Label(f1_frame, text="Types", font=header1_font)
    label_types.pack(side=TOP, fill=X, expand=True)
    label_types_desc = Label(f1_frame, text="Select from below types:", font=desc_font)
    label_types_desc.pack(side=TOP, fill=X, expand=True)
    button_selectAll = Button(f10_frame, text="Select All", command=selectAllTypes)
    button_selectAll.pack(side=LEFT)
    button_selectNone = Button(f10_frame, text="Select None",
                              command=selectNoneTypes)
    button_selectNone.pack(side=LEFT)

    checkbuttons = list()
    global checkbuttons_vars
    currFrame = f11_frame
    rowCount = 0
    for t in types:
        var_tmp = IntVar()
        cBox_tmp = Checkbutton(currFrame, text=t, variable=var_tmp, bg=typesColor)
        checkbuttons.append(cBox_tmp)
        checkbuttons_vars.append(var_tmp)
        cBox_tmp.pack(side=TOP, anchor=W)
        rowCount = rowCount + 1
        if rowCount < 20:
            currFrame = currFrame
        elif rowCount < 40:
            currFrame = f12_frame
        elif rowCount < 60:
            currFrame = f13_frame
        elif rowCount < 80:
            currFrame = f14_frame
        elif rowCount < 100:
            currFrame = f15_frame


    banner_img = Image("photo", file="resource\\banner.png", master=f2_frame)
    banner_label = Label(f2_frame, image=banner_img, text="Googl Places Export Tool", font=title_font)
    banner_label.pack(side=TOP)
    # The Location frame
    label_location = Label(f211_frame, text="Location", width=20, font=header1_font, anchor=W)
    label_location.pack(side=TOP, fill=X)
    label_locationDesc = Label(f211_frame, text="Enter X, Y & radius below", font=desc_font)
    label_locationDesc.pack(side=TOP)
    label_locationDesc2 = Label(f211_frame, text="(radius max is: 50000)")
    label_locationDesc2.pack(side=TOP)

    global txt_locX
    global txt_locY
    global txt_raduis
    label_long = Label(f2111_frame, text="Longitude (X): ")
    label_long.pack(side=TOP, anchor=E)
    label_lat = Label(f2111_frame, text="Latitude (Y): ")
    label_lat.pack(side=TOP, anchor=E)
    label_radius = Label(f2111_frame, text="Radius (in m): ")
    label_radius.pack(side=TOP, anchor=E)

    txt_locX = Entry(f2112_frame)
    txt_locX.insert(0, "-96.7903963")
    txt_locX.pack(side=TOP)
    txt_locY = Entry(f2112_frame)
    txt_locY.insert(0, "33.0010647")
    txt_locY.pack(side=TOP)
    txt_raduis = Entry(f2112_frame)
    txt_raduis.insert(0, "500")
    txt_raduis.pack(side=TOP)

    global duplicatesFromGDB_var
    duplicatesFromGDB_var = IntVar()

    button_removeDuplicates = Button(f212_frame,
                                     text="Remove Duplicates",
                                     command=removeDuplicates)
    button_removeDuplicates.pack(side=BOTTOM)
    duplicateFromGDB_cBox = Checkbutton(f212_frame,
                                        text="Removing duplicates from GDB?",
                                        variable=duplicatesFromGDB_var)
    duplicateFromGDB_cBox.pack(side=BOTTOM)
    duplicateRem__desc_label = Label(f212_frame, text="dataset of (.shp) or a feature class in a (.gdb)", font=desc_font)
    duplicateRem__desc_label.pack(side=BOTTOM)
    duplicateRem__desc2_label = Label(f212_frame,
                                     text="This tool will remove duplicates existing in any",
                                     font=desc_font)
    duplicateRem__desc2_label.pack(side=BOTTOM)
    duplicateRem_label = Label(f212_frame, text="Duplicate Data Removal Tool", font=header1_font)
    duplicateRem_label.pack(side=BOTTOM)



    # Get user selection for data export type (shp, GDB)
    label_exportTypes = Label(f221_frame, text="Export Type", width=20,
                              font=header1_font, anchor=W)
    label_exportTypes.pack(side=TOP, fill=X, expand=True)
    global createSHP_var
    createSHP_var = IntVar()
    shpOutType_cBox = Checkbutton(f221_frame, text="Shape File (.shp)", variable=createSHP_var)
    shpOutType_cBox.pack(side=TOP)
    # Get user selection for data export type (shp, GDB)
    global createGDB_var
    createGDB_var = IntVar()
    gdbOutType_cBox = Checkbutton(f221_frame, text="Geodatabase file", variable=createGDB_var)
    gdbOutType_cBox.pack(side=TOP)

    # About
    button_about = Button(f2_frame, text="About", width=10, command=about)
    button_about.pack(side=BOTTOM, expand=False)

    f1_frame.pack(side=LEFT)
    f2_frame.pack(side=LEFT, fill=Y)
    f10_frame.pack(side=TOP)
    f11_frame.pack(side=LEFT)
    f12_frame.pack(side=LEFT)
    f13_frame.pack(side=LEFT)
    f14_frame.pack(side=LEFT)
    f15_frame.pack(side=LEFT)
    f21_frame.pack(side=LEFT, expand=True)
    f22_frame.pack(side=LEFT)
    f211_frame.pack(side=TOP)
    f221_frame.pack(side=TOP)
    f222_frame.pack(side=TOP)
    f212_frame.pack(side=TOP)
    f2111_frame.pack(side=LEFT)
    f2112_frame.pack(side=LEFT)
    f2221_frame.pack(side=TOP)
    f2222_frame.pack(side=TOP)


    root.mainloop()

def getSelectedTypes():
    setCursorBusy()
    global checkbuttons_vars
    global typesList
    global selectedTypes
    global createSHP_out
    global createGDB_out
    selectedTypes = list()
    # now I should copy both lists & pop each one at the same time
    # & for each pop (they are the same), thus check if '1' then select the type
    # but if '0' then leave it in the search

    typesList_copy = typesList.copy()
    checkbuttons_vars_copy = checkbuttons_vars.copy()
    typesIndx = 0

    while typesIndx < len(typesList):
        curr_type = typesList_copy.pop()
        curr_typeVar = checkbuttons_vars_copy.pop()
        if int(curr_typeVar.get()) == 1:
            selectedTypes.append(curr_type)
        typesIndx = typesIndx + 1
    print("Done getting selected types")

    notbusy()
    # Start the process
    global txt_outName
    global txt_locX
    global txt_locY
    global txt_raduis

    getLocations(selectedTypes, txt_locX.get(), txt_locY.get(), str(int(txt_raduis.get())), txt_outName.get())


def getOutGDB():
    global outGDB_url
    outGDB_url = filedialog.askdirectory()
    print(outGDB_url)

def copyFC(fcToCopy):
    arcpy.Copy_management(fcToCopy.name, fcToCopy.name.rstrip(".shp") + "_copy.shp")


def removeDuplicates_fromCreate(targetFc):
    global createdFcToFix
    createdFcToFix = targetFc
    removeDuplicates()
def removeDuplicates():
    global duplicatesFromGDB_var
    fcToFix = None
    fidName = None
    global createdFcToFix

    if createdFcToFix == None: # the call is from user
        # Get the src for the dataset to fix
        if duplicatesFromGDB_var.get() == 1:
            fcToFix = simpledialog.askstring("Path",
                                             "Please enter the full path for the feature class")
            fidName = "OBJECTID"
        else:
            fcToFixFile = filedialog.askopenfile("r", filetypes=(
            ("Shape Files", "*.shp"),
            ("All files", "*.*")))
            if fcToFixFile is not None:
                fcToFix = fcToFixFile.name
                fidName = "FID"
        setCursorBusy()
    else: # call is from app after creation of FC
        fcToFix = createdFcToFix
        if ".shp" in fcToFix:
            fidName = "FID"
        else:
            fidName = "OBJECTID"

    print(fcToFix)
    demandRerun = False
    # Start
    if fcToFix is not None:
        if arcpy.Exists(fcToFix):
            # Create a structure of list of list, will hold the types that need to be added alongside the FID
            # The order is (FID, Types)
            typesToAdd = {}
            # Build the dict with FIDs and "" string
            with arcpy.da.SearchCursor(fcToFix, [fidName, "Name", "SHAPE@XY",
                                                 "Type"]) as dictCur:
                for dicItem in dictCur:
                    typesToAdd[dicItem[0]] = ""


            # use da.SearchCursor to iterate through fc call it A
            with arcpy.da.SearchCursor(fcToFix, [fidName, "Name", "SHAPE@XY",
                                                 "Type"]) as searchCur:

                try:
                    for itemA in searchCur:
                        # for each item, iterate using d.UpdateCursor call it B
                        with arcpy.da.UpdateCursor(fcToFix,
                                                   [fidName, "Name",
                                                    "SHAPE@XY",
                                                    "Type"]) as upCur:
                            for itemB in upCur:
                                # print("A: " + str(itemA))
                                # print("B: " + str(itemB))
                                # print(itemB[2] == itemA[2])
                                # if A.name == B.name and A.X == B.X and A.Y == B.Y
                                if itemB[0] != itemA[0] and itemB[1] == itemA[
                                    1] and \
                                                itemB[2] == itemA[2]:
                                    # capture the type of B into the list in the dict
                                    typesToAdd[itemA[0]] = typesToAdd[
                                                               itemA[
                                                                   0]] + ", " + \
                                                           itemB[3]
                                    # Delete B
                                    print("Deleting a duplicate: " + itemB[1])
                                    upCur.deleteRow()
                except Exception as e:
                    # Something went wrong ..
                    # probably due to arcpy and permissions
                    print(str(e))
                    demandRerun = True

            typeUpdateNotDone = True
            # print(typesToAdd)
            while typeUpdateNotDone:
                try:
                    with arcpy.da.UpdateCursor(fcToFix,
                                               [fidName, "Name", "SHAPE@XY",
                                                "Type"]) as upCur2:
                        # Iterate on all items after deletion
                        # Update A with new types by adding to existing
                        for item in upCur2:
                            item[3] = item[3] + typesToAdd[item[0]]
                            upCur2.updateRow(item)
                        typeUpdateNotDone = False
                except Exception as ex:
                    print("Trying again to gain update access")

            if not demandRerun and createdFcToFix == None:
                messagebox.showinfo("Done", "Duplicates from \"" + fcToFix + "\" were removed!")
        else:
            messagebox.showerror("Wrong Path",
                                 "The path \"" + fcToFix +
                                 "\" does not appear to be valid")

        if demandRerun:
            infExStr = "\"\nshould fix it\n\nNote:\n\tThis probably bec" \
                       "ause your target data is in a folder that it su" \
                       "bject to synchronization. Such as having it in " \
                       "a Google Drive folder or a Dropbox folder"
            messagebox.showinfo("Done with incomplete",
                                "Some records were cleaned. However, due to a"
                                "n error the software could not complete the r"
                                "est.\nRe-running the tool again o"
                                "n:\n\"" + fcToFix + infExStr)
    createdFcToFix = None
    notbusy()


def setCursorBusy():
    global root
    root.config(cursor="wait")
    root.update()
    time.sleep(1)

def notbusy():
    global root
    root.config(cursor="")
    root.update()
    time.sleep(1)



if __name__ == "__main__":
    gKeyFile = open("GoogleKey.txt", "r")
    global googleKey
    googleKey = gKeyFile.readline().rstrip("\n")
    global typesList
    typeFile = open("placesTypes.txt",'r')
    typeStr = typeFile.readline()
    while(typeStr):
        typeStr = typeFile.readline()
        if typeStr != '':
            typesList.append(typeStr.rstrip("\n"))
    startUI(typesList)

