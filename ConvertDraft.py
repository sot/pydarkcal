# File: ConvertDraft.py
# Original Code: Robert Cameron April 1999
# Created By   : Christopher Thomas June 2016
# Lasted Edited: Christopher Thomas Aug 1st 2016

# CHANDRA
#     v_1: Convert Code to Python [238/1970]
#         * acalimg_sfdu.pro [227/621]
#         * badpix_SAUS.pro [/94]
#         * IO-median.pro [/5]
#         * legend.pro [/473]
#         * make_csv.pro [/46]
#         * plot_dark.pro [/516]
#         * plothist [/105]
#         * prb.pro [11/11]
#         * startup.pro [/102]
#     v_2: Test Python Code [/]
#     Known Bugs: (In Python Code)
#       ...

import sys
import numpy as np

# ======================
# Initializing Variables
# ======================

# SFDUsync = byte('NJPL')
SFDUsync = [78,  74,  80,  76]
# VCDUsync = ['1A'xb,'CF'xb,'FC'xb,'1D'xb]
VCDUsync = [26, 207, 252, 29]
# DSNch = ['41'xb,'93'xb]
DSNch = [65, 147]


# Number of bytes in an SFDU
sfdurecl = 1134
# Number of bytes in SFDU header
sfduhdrl = 104
# Number of bytes per truncated DSN record
dsnrecl = 1029
# Number of bytes per cal record
calrecl = 1040


# 2 microsecond clock period
cltick = 2e-6

# quadrant identifiers for values of QUADID
quadstr = ['A', 'C', 'B', 'D']


#
# create a structure record of the L0 product type
#

sl0 = {
    'TIME_ERT': 0.0,
    'REC_CTR': 0L,
    'ADC_BIAS': 0,
    'INTEG': 0.0,
    'CALTYPE': 0,
    'REPLICA': 0,
    'COLNEG': 0,
    'ROW': 0,
    'SCI_HDR_CTR': 0,
    'TWO_US_CLK': 0L,
    'PIXDATA': [None] * 512
}

# sl0n=0
sl0n = 0

#
# count the number of records in the file
#

# i=0L
i = 0
v = 0
tdsn = 0
tfil = 0
tother = 0
nrecmax = 20000
# idx=lonarr(nrecmax)
idx = []
# count=lonarr(nrecmax)
count = []
# ert=dblarr(nrecmax)
ert = []
#  a counter for composite total images written to FITS files
timecount = 0
# rotally=intarr(1024,2)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# rofill=intarr(1024,2)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# imarr=fltarr(1024,1024)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# quadarr=fltarr(512,512)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# quadfill=intarr(512)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# quadtally=intarr(4)
# NOTE: DOES NOT NEED TO BE INITIALIZED AT THIS TIME
# prevquadid=-1
# NOTE: prevquadid = -1


# prb takes in two arguments, olun and param_array.
# olun is the debug file to write to.
# param_array is an array of strings that is combined into a single string.
# prb takes a string and writes it to the terminal and a debug file.
def prb(olun, param_array):
    str = ' '.join(param_array)
    print(str)
    olun.write(str + '\n')

# Takes the first argument, which is the name of calabration data file,
# and saves it to cal_data_file.
cal_data_file = sys.argv[1]
if cal_data_file == '':
    print('ERROR: No Data File Given')

# TODO: Add implement code
# data_file = sys.argv[2]  # View Number

# Opens the Calibration Data File in binary mode.
# ".read()" reads and saves the file's contents to the variable "il".
il = open(cal_data_file, 'r+b').read()

# Opens debug file to be written to
ol = open('../data2/test_file_python.txt', 'w')

#
# start processing the cal data files
#

prb(ol, ['ACA cal data file:', cal_data_file])
prb(ol, '')
prb(ol, ['Valid SFDU sync is:', str(SFDUsync)])
prb(ol, ['Valid DSN record sync is:', str(VCDUsync), str(DSNch)])
prb(ol, '')


#
# Inspect each SFDU in the file and check its contents
#

# Looping through cal_data_file in steps of sfdurecl (1134)
for indexo in range(len(il)/sfdurecl):

    # Setting current step of 1134 to "r"
    r = il[indexo*sfdurecl:indexo*sfdurecl+sfdurecl]

    # Converting step "r" to decimals, then saving to "ir"
    ir = []
    for rr in r:
        ir.append(ord(rr))

    # Testing synchronization
    synctest1 = ir[0:4]
    synctest2 = ir[sfduhdrl:sfduhdrl+4]
    notexplained = 1

    if (synctest1 == SFDUsync and synctest2 == VCDUsync):
        # This SFDU starts with a correct sync pattern
        notexplained = 0
        v = v+1
        ch = ir[sfduhdrl+4:sfduhdrl+6]
        if ch[1] == DSNch[1]:

            # test if the DSN record contains only fill data
            # "testr" is all elements of "ir" that are not equal to 170
            testr = [i for i in ir[sfduhdrl+10:sfduhdrl+1029] if i != 170]
            testn = len(testr)

            if testn > 3:

                # idx appending integer indexo to list
                idx.append(indexo)

                # No Idea what the software is supose to be doing as a hole
                # No Usefull comment here, sorry - Christopher Thomas
                count.append(ir[sfduhdrl + 6] * 65536 + ir[sfduhdrl + 7] *
                             256 + ir[sfduhdrl + 8])

                # I will carry time since the start of 1998 (the Chandra FITS
                # file reference) which is 14610 days after the start of 1958
                # (the ERT reference), in seconds.
                # NOTE: I ignore the 32.182 second + leap seconds offset...
                # ...between UTC (for ERT) and TT (for FITS)
                ert.append((ir[42]*256 + ir[43] - 14610) * 84600e0 +
                           (((ir[44] * 256 + ir[45])*256 + ir[46]) * 256 +
                           ir[47]) / 1e3 + (ir[48] * 256 + ir[49])/1e6)

                tdsn = tdsn+1

            else:
                # DSN minor frame contains only fill data
                tfil = tfil+1

        if ch != DSNch:  # If this is hit, something bad happended...
            tother = tother+1
            prb(ol, ['record', repr(i+1), ' has unknown VCID: ',
                ' '.join(str(x) for x in ir[sfduhdrl:sfduhdrl+6])])

    if notexplained == 1:  # If this is hit, something bad happended...
        # program does not understand the start of the 1029-byte record at all!
        prb(ol, [' *** record ', repr(i), 'start is weird: ',
            ' '.join(ir[0:sfduhdrl+12])])

# End of While Loop

prb(ol, '')
prb(ol, [repr(tdsn), ' DSN minor frames with pixel data in the file'])
prb(ol, [repr(tfil), ' FIL minor frames in the file'])
prb(ol, [repr(tother), ' TOTHER minor frames in the file'])
prb(ol, '')
prb(ol, [repr(indexo), ' SFDUs in the file'])
prb(ol, '')


if tdsn <= 0:
    prb(ol, ['No DSN minor frames in the file, Bozo! I''m stopping!'])

# TBH I think this may be useless in python version, Needs to be tested to
# see if idx,count, & ert change before and after these three lines
idx = idx[0:tdsn]
count = count[0:tdsn]
ert = ert[0:tdsn]

#
# TERMINOLOGY: a "segment" is where the 24-bit DSN record counter is contiguous
# (i.e. increments by 1 between DSN records)
# extract the DSN record counter segments
# disc contains the first indices of new DSN segments
#

# returns the indexes where count - shifted_count does not equals 1
disc = np.flatnonzero(count - np.roll(count, 1) != 1)

# ndisc equals length of disc
ndisc = len(disc)
# disc is an array, tdsn is an integer
disc = np.append(disc, tdsn)

prb(ol, [repr(ndisc), 'segments in the DSN minor frame counter'])

#
# process each segment (i.e. contiguous set) of DSN records - RC
#

# f in rnage of "length of disc"
for f in range(ndisc):
    prb(ol, '')
    prb(ol, ['>>>>>>>>>>>>>>> Processing DSN record segment ', repr(f+1),
        ' <<<<<<<<<<<<<<<'])
    prb(ol, '')

    ndrec = disc[f+1]-disc[1]
    maindat = [[], []]
    m = 0
    # for j=disc(f),disc(f+1)-1 do begin IDL
    # for j = disc(f) in range(disc(f+1)): PYTHON BROKEN
    for j in range(disc[f], disc[f+1]):  # PYTHON FIXED?
        k = idx[j]
        ir1 = r[k]
        # maindat(*,m)=ir1(sfduhdrl+9:sfduhdrl+1028) IDL CODE
        # maindat is set to ir1(sfduhdrl+9:sfduhdrl+1028) for all rows
        maindat.append(ir1[sfduhdrl+9: sfduhdrl+1029])
        m = m + 1

    scount = count[disc[f]:disc[f+1]]
    sert = ert[disc[f]:disc[f+1]]
    prb(ol, ['first, last, delta in DSN minor frame counter:  ',
        repr(scount[0]), '  ', repr(scount[ndrec-1]), '  ',
        repr(scount[ndrec-1]-scount[0]+1)])
    # np.min... is finding the min values for 0-Col in maindat
    # np.max... is finding the max values for 0-Col in maindat
    prb(ol, ['DSN secondary header range: ',
             np.min(np.array(maindat)[:, 0]),  # to many indices fro array
             np.max(np.array(maindat)[:, 0])])
    prb(ol, '')

#
# find the calibration data in the DSN records,
# which is differently placed in alternating DSN records.
# Test for both ways of packing.
# TODO: Check array Index, Add 1 when needed
    if ndrec == 1:
        prb(ol, ['This is a single non-fill cal minor frame at record index ',
                 repr(idx(disc(f))+1)])
        prb(ol, "")
        prb(ol, ["Error: ndrec does not equals 1 -> ndrec = ", repr(ndrec)])

        # ======================================================================
        # ======================================================================
        # ======================================================================
        # TODO: goto nextdisc  # IDL code
        # ======================================================================
        # ======================================================================
        # ======================================================================

    ev = [i for i in scount if (scount/2)*2 == scount]
    nev = len(ev)
    od = [i for i in scount if (scount/2)*2 != scount]
    nod = len(od)
    # Line 212 in acalimg.sfdu.pro
    if not (maindat[1][ev] - 205 == 0 and maindat[1019][od] - 171 == 0):
        calsync = 0
    elif not (maindat[1][od] - 205 == 0 and maindat[1019][ev] - 171 == 0):
        calsync = 1
    else:
        prb(ol, ["Cal data doesn't sync to DSN minor frame counter! Using",
                 "previous sync..."])

    if calsync == 0:
        prb(ol, ['Cal records are synchronized to even DSN minor frame'
                 'counter'])
        for i in range(1017):
            maindat[i][ev] = maindat[i+2][ev]
        for i in range(1017):
            maindat[i][od] = maindat[i+1][od]
    elif calsync == 1:
        prb(ol, ['Cal records are synchronized to odd DSN minor frame'
                 'counter'])
        for i in range(1017):
            maindat[i][od] = maindat[i+2][od]
        for i in range(1017):
            maindat[i][ev] = maindat[i+1][ev]
    # maindat = maindat[:1018][]
    # maindat=reform(maindat,n_elements(maindat))
    maindat.np.flatten()

#
# locate complete calibration records in the extracted cal data
# and check constancy of cal record size
#

# acalimg_sfdu.pro LINE 227

ol.close()
