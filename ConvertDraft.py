import sys
from variables import *


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
    print('ERROR: No Data File Given)

# TODO: Add implement code
# data_file = sys.argv[2]  # View Number

# Opens the Calibration Data File in binary mode.
# ".read()" reads and saves the file's contents to the variable "il".
il = open(data_file, 'r+b').read()

r = []
for i in range(len(il)/sfdurecl):
    r.append(il[i*sfdurecl:i*sfdurecl+sfdurecl])

# Opens debug file to be written to
ol = open('../data2/test_file_python.txt', 'w')

#
# start processing the cal data files
#

prb(ol, ['ACA cal data file:', data_file])
prb(ol, '')
prb(ol, ['Valid SFDU sync is:', str(SFDUsync)])
prb(ol, ['Valid DSN record sync is:', str(VCDUsync), str(DSNch)])
prb(ol, '')


#
# Inspect each SFDU in the file and check its contents
#
for rr in r:
    ir = []
    for rrr in rr:
        ir.append(ord(rrr))

    synctest1 = ir[0:4]
    synctest2 = ir[sfduhdrl:sfduhdrl+4]
    notexplained = 1

    if (synctest1 == SFDUsync and synctest2 == VCDUsync):
        # This SFDU starts with a correct sync pattern
        notexplained = 0
        v = v+1
        ch = ir[sfduhdrl+4:sfduhdrl+6]
        if ch[1] == DSNch[1]:
            # the record is a "DSN record" from the ACA

            # test if the DSN record contains only fill data
            testr = [i for i in ir[sfduhdrl+10:sfduhdrl+1029] if i != 170]
            testn = len(testr)

            if testn > 3:
                idx.append(indexo)
                # TODO: FIgure out how to wrap line - Christopher Thomas
                count.append(ir[sfduhdrl + 6] * 65536 + ir[sfduhdrl + 7] * 256 + ir[sfduhdrl + 8])

                # I will carry time since the start of 1998 (the Chandra FITS file reference)
                # which is 14610 days after the start of 1958 (the ERT reference), in seconds.
                # NOTE: I ignore the 32.182 second + leap seconds offset between UTC (for ERT) and TT (for FITS)
                # TODO: FIgure out how to wrap line - Christopher Thomas
                ert.append((ir[42]*256 + ir[43] - 14610) * 84600e0 + (((ir[44] * 256 + ir[45])*256 + ir[46])*256 + ir[47])/1e3 + (ir[48]*256 + ir[49])/1e6)
                tdsn = tdsn+1

            else:
                # DSN minor frame contains only fill data
                tfil = tfil+1

        if ch != DSNch:
            tother = tother+1
            prb(ol, ['record', repr(i+1), ' has unknown VCID: ',
                ' '.join(str(x) for x in ir[sfduhdrl:sfduhdrl+6])])

    indexo = indexo+1
    if notexplained == 1:
        # I don't understand the start of the 1029-byte record at all!
        prb(ol, [' *** record ', repr(i), 'start is weird: ',
            ' '.join(ir[0:sfduhdrl+12])])

# End of While Loop


prb(ol, '')
prb(ol, [repr(tdsn), ' DSN minor frames with pixel data in the file'])
prb(ol, [repr(tfil), ' FIL minor frames in the file'])
prb(ol, [repr(tother), ' OTHER minor frames in the file'])
prb(ol, '')
prb(ol, [repr(indexo), ' SFDUs in the file'])
prb(ol, '')

if tdsn <= 0:
    prb(ol, ['No DSN minor frames in the file, Bozo! I''m stopping!'])

idx = idx[0:tdsn]
count = count[0:tdsn]
ert = ert[0:tdsn]

#
# TERMINOLOGY: a "segment" is where the 24-bit DSN record counter is contiguous
# (i.e. increments by 1 between DSN records)
# extract the DSN record counter segments
# disc contains the first indices of new DSN segments
#
disc = [i for i in (count - np.roll(count, 1)) if i != 1]
ndisc = len(disc)
disc = [disc, tdsn]

prb(ol, [repr(ndisc), 'segments in the DSN minor frame counter'])


#
# process each segment (i.e. contiguous set) of DSN records
#
"""
for f in range(ndisc):
    prb(ol, '')
    p drb(ol, ['>>>>>>>>>>>>>>> Processing DSN record segment ', repr(f),
        ' <<<<<<<<<<<<<<<'])
    prb(ol, '')

    ndrec = disc[f+1]-disc(1)
    maindat = [[], []]
    m = 0
    for j = disc(f) in range(disc(f+1)):  # disc(f+1)-1
        k = idx(j)
        ir1 = r(k)
        # maindat(*,m)=ir1(sfduhdrl+9:sfduhdrl+1028)
        mainddat.append(ir1[sfduhdrl+9: sfduhdrl+1029])
        m=m+1
    scount = count[disc[f]:disc(f+1)]
    sert = ert[disc[f]:disc(f+1)]
    prb(ol, ['first, last, delta in DSN minor frame counter:  ',
        repr(scount(0)), '  ', repr(scount(ndrec-1)), '  ',
        repr(scount(ndrec-1)-scount(0)+1)])
    prb(ol, ['DSN secondary header range: ', min(maindat(0,*)),
        max(maindat(0,*))]) # Have Fun!
    prb(ol, '')
"""
ol.close()
