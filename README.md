# pydarkcal

## Christopher Thomas
Took IDL file acalimg_sdfu and converted lines 0-219 to python in file ConvertDraft.py. Also converted entire IDL file prb and placed it as a function as the begining of ConvertDraft. I've been running the python script in ipython and the IDL code in gdl. The file I have been reading in to test is callled: 2016_125_VC2_Replica2_SFDU_31088

## ConvertDraft.py
* Starts by initializing all important variables used throughout the program.
* reads in a designated file. "il" = input file. "ol" = output file
* Loops through the file in steps of 1134. Converts each step and puts them into an Integer Array "r"
* Starts processing the cal data files and prints out header
* Loops through each 1134 step of "r" pulling out all important information.
  * Variables: count, idx, ert
  * count: ??? Used through out to program. array of integers
  * idx: list of index locations pointing to the important information in "r"
  * ert: ??? Has not popped back up sense use in this loop. array of integers
* Prints out SFDU information (counters after the loop through "r")
* Creates disc, segments in the DSN minor frame counter, from information taken from count.
* Starts loop from 0 to length of disc (Where all the important stuff seems to happen)
* ...

### Python Script Output
ACA cal data file: ../data2/2016_125_VC2_Replica2_SFDU_31088 <br />
<br />
Valid SFDU sync is: [78, 74, 80, 76] <br />
Valid DSN record sync is: [26, 207, 252, 29] [65, 147] <br />
<br />
<br />
4258  DSN minor frames with pixel data in the file <br />
29015  FIL minor frames in the file <br />
0  TOTHER minor frames in the file <br />
<br />
33272  SFDUs in the file <br />
<br />
72 segments in the DSN minor frame counter <br />
<br />
\>\>\>\>\>\>\>\>\>\>\>\>\>\>\> Processing DSN record segment  1  <<<<<<<<<<<<<<< <br />
<br />
first, last, delta in DSN minor frame counter:   34757    34818    62 <br />
DSN secondary header range:  128.0 128.0 <br />

### IDL Script Output
ACA cal data file: ../data2/2016_125_VC2_Replica2_SFDU_31088 <br />
<br />
Valid SFDU sync is: NJPL <br />
Valid DSN record sync is: 1A CF FC 1D 41 93 <br />
<br />
<br />
4258 DSN minor frames with pixel data in the file <br />
29015 FIL minor frames in the file <br />
0 OTHER minor frames in the file <br />
<br />
33273 SFDUs in the file <br />
<br />
72 segments in the DSN minor frame counter <br />
<br />
\>\>\>\>\>\>\>\>\>\>\>\>\>\>\> Processing DSN record segment 1 <<<<<<<<<<<<<<< <br />
<br />
first, last, delta in DSN minor frame counter:  34757  34818  62 <br />
DSN secondary header range: 80 80  # User Note: 80 converted from Hex to Dec is 128 <br />
