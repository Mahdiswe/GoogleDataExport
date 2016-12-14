# GoogleDataExport
Python tool that download GIS data from Google Places repository
----------------------------------------------------------------------
# author: Mahdi Al Qateefi
This is short instructions for running the project.

This app requires:
1- Internet connection: to get Google's data
2- Google API Key: required by Google's API

==============================================
====IMPORTANT FOR RUNNING THE APPLICATION====
==============================================
>ABOUT GOOGLE KEY<
You should have your own Google Key in order to run this application.
If you could not get one or you need help, please google "google api key"
==============================================
==============================================

======
GUIDE
======
Below is short guide on running the app:
1- Make sure that you have below folders/ files next to the script location:
	- "out" folder, where the ".shp" files will be stored in
	- "resource" folder, which contains images used
	- "placesTypes.txt" which contain a list of the types from Google (separated by a new line)
	- "GoogleKey.txt" which contain the key to be used when calling Google's API
2- Run the app
3- Select the required types from the check boxes
4- Follow the GUI by inputting the Lat & Long (X & Y) and the radius of the search (50000 is max)
5- Enter the name of the feature class to be created
6- Select the type required to be generated (.shp or GDB or both)
7- Click "Extract Data" to download the data and save them in the required location

=====
Note:
=====
Additional tool (Duplicate Data Removal Tool) is added to delete the duplicate data on any .shp or GDB repositories. You do not need to run it, it is provided just for user convenience.
